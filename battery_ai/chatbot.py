
import re
import pandas as pd


# Free, rule-based Battery Assistant. No API key or internet required.

ALIASES = {
    "voltage": [
        "voltage", "voltagev", "volt", "volts",
        "電圧", "端子電圧", "전압"
    ],
    "current": [
        "current", "currenta", "amps", "ampere",
        "電流", "전류"
    ],
    "temperature": [
        "temperature", "temperaturec", "temp",
        "celltemperature", "celltemp", "セル温度",
        "温度", "셀온도", "온도"
    ],
    "charge_capacity": [
        "chargecapacity", "chargecapacityah",
        "chargeah", "充電容量", "충전용량"
    ],
    "discharge_capacity": [
        "dischargecapacity", "dischargecapacityah",
        "dischargeah", "放電容量", "방전용량"
    ],
    "cycle": [
        "cycle", "cyclenumber", "cycleno",
        "サイクル数", "サイクル番号", "사이클수",
        "사이클번호", "사이클"
    ],
    "phase": [
        "phase", "step", "steptype", "mode",
        "teststep", "試験ステップ", "시험단계"
    ],
    "timestamp": [
        "timestamp", "time", "datetime", "date",
        "測定日時", "日時", "측정시간"
    ],
}


def _normalize(value):
    value = str(value).casefold().strip()
    return re.sub(r"[\s_\-./\\()[\]{}:%℃°]+", "", value)


def _find_column(df, field):
    aliases = {_normalize(x) for x in ALIASES[field]}
    aliases.add(_normalize(field))

    for column in df.columns:
        if _normalize(column) in aliases:
            return column

    return None


def _numbers(df, field):
    column = _find_column(df, field)
    if column is None:
        return pd.Series(dtype="float64")

    values = df[column]

    if not pd.api.types.is_numeric_dtype(values):
        values = (
            values.astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.strip()
        )

    return pd.to_numeric(values, errors="coerce").dropna()


def _format(value, unit=""):
    if value is None or pd.isna(value):
        return "Not available in the loaded data"
    return f"{value:.3f}{(' ' + unit) if unit else ''}"


def answer_battery_question(question, df, result=None, language="Tamil + Tanglish"):
    """Answer supported battery questions using only the loaded dataset."""

    if df is None or df.empty:
        return "Mudhalil battery file-ai select panni Analyze button click pannunga."

    q = question.casefold()
    english = language == "English"

    if any(word in q for word in ["hello", "hi", "hey", "vanakkam"]):
        return (
            "Hello! Battery readings pathi kelunga."
            if not english
            else "Hello! Ask me about your loaded battery readings."
        )

    if any(word in q for word in [
        "help", "what can", "enna kekka", "examples", "என்ன கேட்க"
    ]):
        return (
            "Neenga kekkalaam:\n"
            "- Latest voltage/current/temperature enna?\n"
            "- Maximum temperature evlo?\n"
            "- Charge vs discharge capacity compare pannu.\n"
            "- Cycle count evlo?\n"
            "- Warnings enna?\n"
            "- Data-la ethana rows irukku?"
        )

    if any(word in q for word in [
        "warning", "warnings", "anomaly", "anomalies",
        "abnormal", "problem", "issue", "எச்சரிக்கை"
    ]):
        warnings = (result or {}).get("warnings", [])
        if not warnings:
            return (
                "Current screening-la warnings record aagala. "
                "Idhu battery safe-nu guarantee illa."
                if not english else
                "No screening warnings were recorded. "
                "This does not guarantee that the battery is safe."
            )
        return "Recorded warnings:\n" + "\n".join(
            f"- {item}" for item in warnings
        )

    if any(word in q for word in ["row", "rows", "records", "data count"]):
        return f"Loaded dataset-la {len(df)} rows irukku."

    if any(word in q for word in [
        "ratio", "compare capacity", "capacity comparison",
        "efficiency", "ஒப்பிடு"
    ]):
        charge = _numbers(df, "charge_capacity")
        discharge = _numbers(df, "discharge_capacity")

        if charge.empty or discharge.empty:
            return "Charge and discharge capacity rendu columns-um thevai."

        c = float(charge.iloc[-1])
        d = float(discharge.iloc[-1])

        if c <= 0:
            return "Charge capacity zero/negative; ratio calculate panna mudiyadhu."

        ratio = d / c * 100
        return (
            f"Last recorded charge capacity: {c:.3f} Ah\n"
            f"Last recorded discharge capacity: {d:.3f} Ah\n"
            f"Discharge-to-charge ratio: {ratio:.2f}%\n\n"
            "Indha ratio mattum battery SOH or efficiency-ai prove pannaadhu."
        )

    fields = {
        "voltage": ("voltage", "V", [
            "voltage", "volt", " v ", "電圧", "전압"
        ]),
        "current": ("current", "A", [
            "current", "amp", "電流", "전류"
        ]),
        "temperature": ("temperature", "°C", [
            "temperature", "temp", "hot", "heat",
            "செல்சூடு", "セル温度", "온도"
        ]),
        "charge_capacity": ("charge capacity", "Ah", [
            "charge capacity", "charging capacity",
            "charge_capacity", "充電容量", "충전용량"
        ]),
        "discharge_capacity": ("discharge capacity", "Ah", [
            "discharge capacity", "discharging capacity",
            "discharge_capacity", "放電容量", "방전용량"
        ]),
        "cycle": ("cycle", "", [
            "cycle", "cycles", "சைக்கிள்", "サイクル", "사이클"
        ]),
    }

    selected = None
    for field, (label, unit, keywords) in fields.items():
        if any(keyword in q for keyword in keywords):
            selected = (field, label, unit)
            break

    if selected:
        field, label, unit = selected
        values = _numbers(df, field)

        if values.empty:
            return (
                f"{label} column/data identify aagala. "
                "File headers-ai check pannunga."
            )

        # For cycle count, the largest recorded cycle is more useful
        # than treating it as an ordinary measurement.
        if field == "cycle" and any(
            word in q for word in ["count", "total", "number", "எண்ணிக்கை"]
        ):
            value = float(values.max())
            return f"Maximum recorded cycle number: {value:g}"

        if any(word in q for word in [
            "maximum", "max", "highest", "highest", "adhigama",
            "highest", "மிக அதிக", "최고"
        ]):
            value = float(values.max())
            prefix = "Maximum"
        elif any(word in q for word in [
            "minimum", "min", "lowest", "least", "kammi",
            "குறைந்த", "최저"
        ]):
            value = float(values.min())
            prefix = "Minimum"
        elif any(word in q for word in [
            "average", "mean", "average", "avg", "sar average"
        ]):
            value = float(values.mean())
            prefix = "Average"
        else:
            value = float(values.iloc[-1])
            prefix = "Latest recorded"

        return f"{prefix} {label}: {_format(value, unit)}"

    return (
        "Indha question-ku exact answer kandupidikka mudiyala. "
        "Voltage, current, temperature, capacity, cycle, ratio, "
        "or warnings pathi kelunga. Data-la illaadha readings-ai "
        "naan guess panna maatten."
    )
