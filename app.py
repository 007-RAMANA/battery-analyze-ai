
from pathlib import Path
import time

import pandas as pd
import streamlit as st

from battery_ai.analysis_engine import (
    read_battery_file,
    analyze_battery_data,
)
from battery_ai.chatbot_llm import (
    build_battery_context,
    chat_with_battery_data,
)

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Battery Analyze AI",
    page_icon="🔋",
    layout="wide",
)

# ---------------------------------------------------------
# PREMIUM UI THEME
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root { --bg:#07111f; --panel:#0d1b2b; --line:#1c3348; --cyan:#35d6e8; --mint:#66f0bd; --muted:#91a7bd; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #102c43 0%, #07111f 43%, #050b14 100%); color:#e8f2fb; }
[data-testid="stHeader"] { background: rgba(5,11,20,.82); }
.block-container { max-width: 1450px; padding-top: 1.7rem; padding-bottom: 2.5rem; }
h1,h2,h3 { letter-spacing:-.035em; color:#f2f8ff; }
h1 { font-weight:800; font-size:2.3rem; }
h2 { font-weight:750; }
p, label, .stCaption { color:#b4c6d8; }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0b1929 0%,#07111d 100%); border-right:1px solid #1c3348; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color:#e9f7ff; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(18,43,62,.96),rgba(10,25,40,.96)); border:1px solid #24445b; border-radius:16px; padding:18px 18px 16px; box-shadow:0 8px 24px rgba(0,0,0,.16); }
div[data-testid="stMetric"] label { color:#9bb5c9 !important; font-size:.82rem; font-weight:600; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#42dbea; font-weight:800; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color:#66f0bd; }
.stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid #2a7185; background:linear-gradient(120deg,#0f8097,#146b83); color:white; font-weight:700; min-height:2.7rem; transition:all .18s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:#55e7ef; color:white; box-shadow:0 0 0 3px rgba(53,214,232,.12); transform:translateY(-1px); }
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea { background:#0b1a29 !important; border-color:#28445b !important; color:#eaf6ff !important; border-radius:10px !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border:1px solid #1e3a50; border-radius:12px; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid #1e3a50; border-radius:12px; background:rgba(11,26,41,.7); }
[data-testid="stAlert"] { border-radius:12px; }
[data-testid="stChatMessage"] { background:rgba(13,29,46,.88); border:1px solid #1b354b; border-radius:14px; padding:12px 14px; margin-bottom:10px; }
[data-testid="stChatInput"] { border-color:#2b5368; border-radius:14px; }
hr { border-color:#1b3549; }
div[data-testid="stMarkdownContainer"] a { color:#49dce8; }
.ui-hero { padding:25px 28px; border:1px solid #24506a; border-radius:20px; background:linear-gradient(115deg,rgba(17,53,76,.96),rgba(9,24,40,.96)); margin-bottom:22px; position:relative; overflow:hidden; }
.ui-kicker { color:#54e6e8; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:800; margin-bottom:7px; }
.ui-title { color:#f2fbff; font-size:2rem; font-weight:800; letter-spacing:-.05em; line-height:1.15; }
.ui-subtitle { color:#a9c1d4; font-size:.96rem; margin-top:9px; }
.ui-pill { display:inline-block; padding:6px 10px; margin-top:15px; border-radius:999px; color:#7cf5c8; background:rgba(102,240,189,.09); border:1px solid rgba(102,240,189,.25); font-size:.75rem; font-weight:700; }
.section-label { color:#57dce8; text-transform:uppercase; letter-spacing:.13em; font-size:.74rem; font-weight:800; margin: 8px 0 12px; }
@media (max-width: 700px) { .block-container { padding-left:1rem; padding-right:1rem; } .ui-title {font-size:1.55rem;} h1 {font-size:1.8rem;} }

/* BLACK + ELECTRIC GREEN / STYLISH TYPOGRAPHY */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --bg:#050706; --panel:#0b100c; --line:#1b3221; --green:#39ff78; --mint:#9bffb4; --muted:#a0b5a5; }
html, body, [class*="css"], button, input, textarea, select { font-family:'Space Grotesk','Inter',sans-serif !important; }
.stApp { background:radial-gradient(ellipse at 12% 0%,#102619 0%,#070b08 42%,#030504 100%) !important; color:#eaffef !important; }
[data-testid="stHeader"] { background:rgba(3,7,4,.88) !important; }
h1,h2,h3,h4 { color:#f0fff3 !important; letter-spacing:-.04em !important; }
h1 { font-size:2.35rem !important; font-weight:700 !important; }
p, label, .stCaption, [data-testid="stCaptionContainer"] { color:#b3c8b8; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#0b140d 0%,#050806 100%) !important; border-right:1px solid #1b3824 !important; }
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:#edfff0 !important; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(17,34,21,.98),rgba(8,15,10,.98)) !important; border:1px solid #244a2e !important; border-radius:17px !important; box-shadow:0 10px 30px rgba(0,0,0,.28),inset 0 1px 0 rgba(57,255,120,.04) !important; }
div[data-testid="stMetric"] label { color:#a6c2ad !important; letter-spacing:.025em; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#52ff86 !important; font-weight:700 !important; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color:#a1ffb5 !important; }
.stButton > button,.stDownloadButton > button { border-radius:11px !important; border:1px solid #39e96f !important; background:linear-gradient(120deg,#1d9d45,#11652c) !important; color:#f3fff5 !important; font-weight:700 !important; min-height:2.8rem; transition:all .2s ease; }
.stButton > button:hover,.stDownloadButton > button:hover { border-color:#83ffa2 !important; background:linear-gradient(120deg,#29c956,#16833a) !important; box-shadow:0 0 0 3px rgba(57,255,120,.13),0 8px 24px rgba(18,170,65,.12) !important; transform:translateY(-1px); }
.stTextInput input,.stSelectbox div[data-baseweb="select"],.stTextArea textarea,[data-baseweb="input"] { background:#080e09 !important; border-color:#294731 !important; color:#eaffef !important; border-radius:10px !important; }
[data-testid="stDataFrame"],[data-testid="stTable"] { border:1px solid #203b27 !important; border-radius:13px !important; overflow:hidden; }
[data-testid="stExpander"] { border:1px solid #203b27 !important; border-radius:13px !important; background:rgba(8,17,10,.82) !important; }
[data-testid="stChatMessage"] { background:rgba(11,24,14,.94) !important; border:1px solid #203d28 !important; border-radius:15px !important; padding:13px 15px !important; margin-bottom:10px; }
[data-testid="stChatInput"] { border-color:#2a5936 !important; border-radius:14px !important; }
hr { border-color:#1d3925 !important; }
div[data-testid="stMarkdownContainer"] a { color:#62ff8e !important; }
.ui-hero { padding:27px 30px !important; border:1px solid #285b36 !important; border-radius:21px !important; background:linear-gradient(115deg,rgba(17,42,24,.98),rgba(6,15,9,.98)) !important; box-shadow:0 18px 50px rgba(0,0,0,.22),inset 0 1px 0 rgba(105,255,143,.06); }
.ui-kicker,.section-label { color:#65ff91 !important; text-transform:uppercase; letter-spacing:.17em !important; font-weight:700 !important; }
.ui-title { color:#f2fff4 !important; font-family:'Space Grotesk',sans-serif !important; font-size:2.15rem !important; font-weight:700 !important; letter-spacing:-.055em !important; }
.ui-title span { color:#49ff80 !important; }
.ui-subtitle { color:#afc8b5 !important; }
.ui-pill { color:#8dffac !important; background:rgba(57,255,120,.08) !important; border:1px solid rgba(57,255,120,.28) !important; letter-spacing:.035em; }
[data-testid="stProgressBar"] > div > div { background:#39ff78 !important; }
[data-baseweb="tab-list"] button[aria-selected="true"] { color:#64ff91 !important; border-bottom-color:#39ff78 !important; }
@media (max-width:700px) { .ui-title {font-size:1.65rem !important;} h1 {font-size:1.85rem !important;} }

/* Hide Streamlit's fixed top header/toolbar strip */
[data-testid="stHeader"] { display:none !important; height:0 !important; }

/* FIX: chatbot bottom white strip -> true black */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] > div {
    background: #030504 !important;
    background-color: #030504 !important;
}

/* Chat input outer wrapper */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {
    background: #030504 !important;
    background-color: #030504 !important;
    border-color: #39ff78 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

/* Text typed into the chatbot */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    background: #030504 !important;
    color: #39ff78 !important;
    -webkit-text-fill-color: #39ff78 !important;
    caret-color: #39ff78 !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color: #8affaa !important;
    -webkit-text-fill-color: #8affaa !important;
    opacity: 1 !important;
}

/* Neon-green send button */
[data-testid="stChatInput"] button {
    background: #030504 !important;
    color: #39ff78 !important;
    border: 1px solid #39ff78 !important;
    border-radius: 8px !important;
}
[data-testid="stChatInput"] button:hover {
    background: #102416 !important;
    box-shadow: 0 0 10px rgba(57, 255, 120, .28) !important;
}

[data-testid="stToolbar"] { visibility:hidden !important; height:0 !important; }
.block-container { padding-top:1.2rem !important; }

/* Make chatbot typing area readable on the black/green theme */
[data-testid="stChatInput"] { background:#080e09 !important; border:1px solid #39a957 !important; border-radius:14px !important; }
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input,
[data-testid="stChatInput"] [contenteditable="true"],
[data-testid="stChatInput"] div[data-baseweb="textarea"] textarea {
    color:#f2fff4 !important;
    -webkit-text-fill-color:#f2fff4 !important;
    caret-color:#39ff78 !important;
    background:#080e09 !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInput"] input::placeholder {
    color:#91a895 !important;
    -webkit-text-fill-color:#91a895 !important;
    opacity:1 !important;
}
[data-testid="stChatInput"] button { color:#39ff78 !important; }

/* FULL BLACK + NEON GREEN CHATBOT */
[data-testid="stChatMessage"] {
    background:#050805 !important;
    border:1px solid #1d6b32 !important;
    border-left:3px solid #39ff78 !important;
    border-radius:14px !important;
    color:#eaffef !important;
    box-shadow:0 0 18px rgba(57,255,120,.045) !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color:#eaffef !important;
}
[data-testid="stChatMessage"] code {
    background:#0b160d !important;
    color:#8dffac !important;
    border:1px solid #1d4d2a !important;
}
[data-testid="stChatMessage"] pre {
    background:#020402 !important;
    border:1px solid #1d4d2a !important;
}
[data-testid="stChatInput"] {
    background:#030503 !important;
    border:1px solid #39ff78 !important;
    box-shadow:0 0 0 1px rgba(57,255,120,.08),0 0 18px rgba(57,255,120,.07) !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] textarea {
    background:#030503 !important;
    color:#f0fff3 !important;
    -webkit-text-fill-color:#f0fff3 !important;
    caret-color:#39ff78 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color:#80a88a !important;
    -webkit-text-fill-color:#80a88a !important;
    opacity:1 !important;
}
[data-testid="stChatInput"] button {
    background:#0b1a0e !important;
    color:#39ff78 !important;
    border:1px solid #1d6b32 !important;
    border-radius:10px !important;
}
[data-testid="stChatInput"] button:hover {
    background:#12351b !important;
    box-shadow:0 0 12px rgba(57,255,120,.18) !important;
}
</style>
<div class="ui-hero">
  <div class="ui-kicker">Battery intelligence platform</div>
  <div class="ui-title">Battery Analyze <span style="color:#49ff80">AI</span></div>
  <div class="ui-subtitle">Explore battery performance, track charge and discharge behaviour, and ask your dataset questions with Groq AI.</div>
  <span class="ui-pill">● SYSTEM READY &nbsp; · &nbsp; NUMERICAL ANALYSIS + AI CHAT</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Workspace overview</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------
DEFAULT_FOLDER = Path(r"C:\BatteryAI\watched_files")
DEFAULT_FOLDER.mkdir(parents=True, exist_ok=True)

SUPPORTED = {
    ".csv", ".txt", ".log", ".md",
    ".xlsx", ".xls", ".pdf", ".docx", ".json",
}

with st.sidebar:
    st.markdown("## 🔋 Battery AI")
    st.caption("ANALYSIS WORKSPACE")
    st.divider()
    st.header("⚙️ Workspace settings")

    folder_text = st.text_input(
        "Battery output folder",
        value=str(DEFAULT_FOLDER),
    )

    language = st.selectbox(
        "AI response language",
        ["Tamil + Tanglish", "Tamil", "English"],
    )

folder = Path(folder_text).expanduser()

if not folder.exists() or not folder.is_dir():
    st.error("Valid folder path enter pannunga.")
    st.stop()

# ---------------------------------------------------------
# FILE LIST
# ---------------------------------------------------------
files = sorted(
    [
        path
        for path in folder.iterdir()
        if path.is_file()
        and not path.is_symlink()
        and path.suffix.lower() in SUPPORTED
        and not path.name.startswith("~$")
    ],
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)

st.markdown('<div class="section-label">01 / Data source</div>', unsafe_allow_html=True)
st.subheader("📂 Battery output files")
st.caption(f"Folder: {folder}")

if not files:
    st.info("Indha folder-la supported battery files edhuvum illai.")
    st.stop()

for path in files:
    modified = time.strftime(
        "%d-%m-%Y %H:%M",
        time.localtime(path.stat().st_mtime),
    )
    st.write(f"📄 **{path.name}** — {modified}")

# ---------------------------------------------------------
# FILE SELECTION
# ---------------------------------------------------------
st.divider()

selected = st.selectbox(
    "Analyze a file",
    files,
    format_func=lambda path: path.name,
)

sheet_name = None

if selected.suffix.lower() in {".xlsx", ".xls"}:
    try:
        workbook = pd.ExcelFile(selected)
        sheet_name = st.selectbox(
            "Excel worksheet",
            workbook.sheet_names,
        )
    except Exception as exc:
        st.error(f"Excel file read error: {exc}")
        st.stop()

# ---------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------
if st.button("🔬 Analyze battery data", type="primary"):
    try:
        extension = selected.suffix.lower()

        if extension in {
            ".csv", ".txt", ".log", ".md", ".xlsx", ".xls"
        }:
            dataframe = read_battery_file(
                selected,
                sheet_name=sheet_name,
            )
        else:
            st.warning(
                "Indha file format-ku current numerical analysis "
                "reader support confirm pannunga. PDF, DOCX, JSON "
                "extraction irundhaalum battery measurements "
                "correct-a identify aagudha verify pannanum."
            )
            st.stop()

        result = analyze_battery_data(dataframe)

        st.session_state["battery_df"] = dataframe
        st.session_state["battery_result"] = result
        st.session_state["battery_filename"] = selected.name

        # Clear chat when a new file is analyzed.
        st.session_state["battery_chat_history"] = []

    except Exception as exc:
        st.error(f"Analysis error: {exc}")

# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------
if "battery_result" in st.session_state:
    df = st.session_state["battery_df"]
    result = st.session_state["battery_result"]
    metrics = result.get("metrics", {})

    st.divider()
    st.markdown('<div class="section-label">02 / Analysis report</div>', unsafe_allow_html=True)
    st.subheader(f"📊 {st.session_state['battery_filename']}")

    st.write(f"Rows analysed: **{result.get('rows', len(df))}**")

    # -----------------------------------------------------
    # METRIC HELPERS
    # -----------------------------------------------------
    def metric_value(key):
        item = metrics.get(key)

        if isinstance(item, dict):
            return item.get("last")

        return item

    def show_metric(value, unit, decimals=3):
        if value is None:
            return "N/A"

        try:
            number = float(value)

            if pd.isna(number):
                return "N/A"

            return f"{number:.{decimals}f} {unit}".strip()

        except (TypeError, ValueError):
            return "N/A"

    # -----------------------------------------------------
    # MAIN MEASUREMENT CARDS
    # -----------------------------------------------------
    metric_cols = st.columns(3)

    cards = [
        ("Latest Voltage", "latest_voltage", "voltage", "V", 3),
        ("Latest Current", "latest_current", "current", "A", 3),
        (
            "Latest Temperature",
            "latest_temperature",
            "temperature",
            "°C",
            3,
        ),
    ]

    for col, (label, new_key, old_key, unit, decimals) in zip(
        metric_cols, cards
    ):
        value = metric_value(new_key)

        if value is None:
            value = metric_value(old_key)

        col.metric(
            label,
            show_metric(value, unit, decimals),
        )

    # -----------------------------------------------------
    # CAPACITY CARDS
    # -----------------------------------------------------
    cap_cols = st.columns(2)

    charge = metric_value("charge_capacity")
    discharge = metric_value("discharge_capacity")

    if charge is None:
        charge = metric_value("charge_capacity_ah")

    if discharge is None:
        discharge = metric_value("discharge_capacity_ah")

    cap_cols[0].metric(
        "Charge Capacity",
        show_metric(charge, "Ah", 4),
    )

    cap_cols[1].metric(
        "Discharge Capacity",
        show_metric(discharge, "Ah", 4),
    )

    # -----------------------------------------------------
    # CAPACITY RATIO
    # -----------------------------------------------------
    ratio = result.get("capacity_ratio")

    if ratio is None:
        comparison = metrics.get("capacity_comparison")

        if isinstance(comparison, dict):
            ratio = comparison.get("last")

            # Older engine reports this ratio as a percentage.
            if ratio is not None:
                ratio = float(ratio) / 100.0

    if ratio is not None:
        try:
            ratio_number = float(ratio)

            st.metric(
                "Discharge / Charge Capacity Ratio",
                f"{ratio_number * 100:.2f}%",
            )

            st.caption(
                "Recorded capacity ratio mattum; idhu verified "
                "battery SOH illa."
            )

        except (TypeError, ValueError):
            st.info("Capacity ratio calculate panna mudiyala.")

    # -----------------------------------------------------
    # BATTERY TRENDS
    # -----------------------------------------------------
    st.markdown('<div class="section-label">Performance telemetry</div>', unsafe_allow_html=True)
    st.subheader("📈 Battery trends")

    # Preserve support for canonical and older column names.
    # The analysis engine's multilingual normalization is unchanged.
    chart_aliases = {
        "Voltage": ["Voltage", "voltage"],
        "Current": ["Current", "current"],
        "Temperature": [
            "Temperature",
            "temperature",
            "セル温度(℃)",
        ],
    }

    plot_df = pd.DataFrame(index=df.index)

    for display_name, candidates in chart_aliases.items():
        for candidate in candidates:
            if candidate in df.columns:
                numeric = pd.to_numeric(
                    df[candidate],
                    errors="coerce",
                )

                if numeric.notna().any():
                    plot_df[display_name] = numeric
                    break

    if not plot_df.empty:
        st.line_chart(plot_df, height=320)
    else:
        st.info(
            "Graph create panna numeric voltage/current/temperature "
            "columns kidaikkala."
        )

    # -----------------------------------------------------
    # PHASE SUMMARY
    # -----------------------------------------------------
    st.markdown('<div class="section-label">Operating behaviour</div>', unsafe_allow_html=True)
    st.subheader("🔄 Charge / discharge phase summary")

    phase = result.get("phase_summary")

    if isinstance(phase, dict) and phase:
        phase_df = pd.DataFrame.from_dict(
            phase,
            orient="index",
        )
        phase_df.index.name = "Phase"

        st.dataframe(
            phase_df.reset_index(),
            use_container_width=True,
        )

    elif isinstance(phase, pd.DataFrame) and not phase.empty:
        st.dataframe(phase, use_container_width=True)

    else:
        phase_column = next(
            (
                column
                for column in ["Phase", "step_type", "phase"]
                if column in df.columns
            ),
            None,
        )

        if phase_column:
            st.dataframe(
                df.groupby(phase_column, dropna=False)
                .size()
                .reset_index(name="Rows"),
                use_container_width=True,
            )
        else:
            st.info("Phase summary available illa.")

    # -----------------------------------------------------
    # CYCLE SUMMARY
    # -----------------------------------------------------
    st.subheader("🔋 Cycle summary")

    cycles = result.get("cycle_summary")

    if isinstance(cycles, list) and cycles:
        st.dataframe(
            pd.DataFrame(cycles),
            use_container_width=True,
        )

    elif isinstance(cycles, pd.DataFrame) and not cycles.empty:
        st.dataframe(cycles, use_container_width=True)

    else:
        cycle_column = next(
            (
                column
                for column in ["Cycle", "cycle"]
                if column in df.columns
            ),
            None,
        )

        if cycle_column:
            st.dataframe(
                df.groupby(cycle_column, dropna=False)
                .size()
                .reset_index(name="Rows"),
                use_container_width=True,
            )
        else:
            st.info("Cycle summary available illa.")

    # -----------------------------------------------------
    # WARNINGS
    # -----------------------------------------------------
    st.subheader("⚠️ Potential anomalies")

    warnings = result.get("warnings", [])

    if warnings:
        for warning in warnings:
            st.warning(str(warning))
    else:
        st.success(
            "Current screening rules-la warnings detect aagala. "
            "Idhu battery safety certification illa."
        )

    # -----------------------------------------------------
    # IMPORTED DATA + CSV DOWNLOAD
    # -----------------------------------------------------
    with st.expander("View imported data"):
        st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Download analysis data as CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="battery_analysis_data.csv",
        mime="text/csv",
    )

    # -----------------------------------------------------
    # SINGLE GROQ CHATBOT
    # -----------------------------------------------------
    st.divider()
    st.markdown('<div class="section-label">03 / AI copilot</div>', unsafe_allow_html=True)
    st.subheader("💬 Chat with Battery AI")

    st.caption(
        "Ask questions about the selected battery dataset. "
        "Responses are generated using Groq; API limits apply."
    )

    if "battery_chat_history" not in st.session_state:
        st.session_state["battery_chat_history"] = []

    if st.button("🗑️ Clear chat", key="clear_groq_chat"):
        st.session_state["battery_chat_history"] = []
        st.rerun()

    # Display existing conversation.
    for message in st.session_state["battery_chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask about voltage, capacity, temperature, cycles...",
        key="groq_battery_question",
    )

    if user_question:
        # Show and store the user's question.
        st.session_state["battery_chat_history"].append({
            "role": "user",
            "content": user_question,
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        # Use the current analyzed dataset and results.
        context = build_battery_context(
            df=df,
            result=result,
            filename=st.session_state.get("battery_filename", ""),
        )

        with st.chat_message("assistant"):
            with st.spinner(
                "Battery data analyze panni answer pannudhu..."
            ):
                answer = chat_with_battery_data(
                    question=user_question,
                    history=st.session_state[
                        "battery_chat_history"
                    ][:-1],
                    context=context,
                    language=language,
                )

            st.markdown(answer)

        st.session_state["battery_chat_history"].append({
            "role": "assistant",
            "content": answer,
        })

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.caption(
    "Battery AI Assistant • Numerical analysis + Groq chatbot. "
    "Readings and warnings depend on the selected file; always "
    "verify against the battery manufacturer's specifications."
)
