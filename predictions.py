
from dataclasses import dataclass
from typing import Optional

# Battery reference specifications
RATED_CAPACITY_AH = 32.0
NOMINAL_VOLTAGE_V = 48.0
MAX_VOLTAGE_V = 54.6
MIN_REFERENCE_VOLTAGE_V = 34.45

# Screening reference only, not a certified safe charging limit
SCREENING_CURRENT_A = RATED_CAPACITY_AH * 0.5


@dataclass
class Prediction:
    value: Optional[float]
    unit: str
    status: str
    explanation: str


def battery_health(
    measured_capacity_ah: Optional[float]
) -> Prediction:
    """Estimate battery health from measured discharge capacity."""

    if measured_capacity_ah is None or measured_capacity_ah <= 0:
        return Prediction(
            None,
            "%",
            "Insufficient data",
            "A valid measured discharge capacity is required."
        )

    soh = measured_capacity_ah / RATED_CAPACITY_AH * 100

    if soh > 100:
        return Prediction(
            round(soh, 2),
            "%",
            "Verify measurement",
            "Measured capacity exceeds the 32 Ah rating. "
            "Verify the test before interpreting battery health."
        )

    return Prediction(
        round(soh, 2),
        "%",
        "Estimate",
        "Estimated from measured capacity divided by rated capacity. "
        "Use a complete discharge-capacity test."
    )


def remaining_life(
    cycles_used: Optional[int],
    expected_cycle_life: Optional[int] = None
) -> Prediction:
    """Estimate remaining rated cycles when valid data is available."""

    if cycles_used is None or cycles_used < 0:
        return Prediction(
            None,
            "cycles",
            "Insufficient data",
            "Valid cycle-count data is required."
        )

    if expected_cycle_life is None or expected_cycle_life <= 0:
        return Prediction(
            None,
            "cycles",
            "Insufficient data",
            "Enter the manufacturer's rated cycle life."
        )

    remaining = max(expected_cycle_life - cycles_used, 0)

    return Prediction(
        float(remaining),
        "cycles",
        "Rough estimate",
        "Actual battery life depends on temperature, depth of discharge, "
        "charging conditions and battery ageing."
    )


def charging_prediction(
    soc_percent: Optional[float],
    charge_current_a: Optional[float],
    battery_voltage_v: Optional[float] = None
) -> dict:
    """Estimate charge time and screen voltage/current references."""

    result = {
        "time_hours": None,
        "status": "Insufficient data",
        "message": "",
        "current_screening": "Not evaluated",
    }

    if (
        soc_percent is None
        or not 0 <= soc_percent <= 100
    ):
        result["message"] = (
            "Provide a measured or validated SOC between 0 and 100%."
        )
        return result

    if charge_current_a is None or charge_current_a <= 0:
        result["message"] = "A positive charging current is required."
        return result

    if battery_voltage_v is not None and battery_voltage_v < 0:
        result["message"] = "Battery voltage cannot be negative."
        return result

    if battery_voltage_v is not None and battery_voltage_v > MAX_VOLTAGE_V:
        result["status"] = "WARNING"
        result["message"] = (
            "Voltage exceeds the 54.6 V reference. Stop charging and "
            "follow the battery manufacturer's safety instructions."
        )
        return result

    if (
        battery_voltage_v is not None
        and battery_voltage_v < MIN_REFERENCE_VOLTAGE_V
    ):
        result["message"] = (
            "Voltage is below the reference minimum. Verify the reading "
            "and follow manufacturer instructions."
        )

    remaining_ah = RATED_CAPACITY_AH * (1 - soc_percent / 100)

    # Rough estimate: allowance for charging losses and taper.
    result["time_hours"] = round(
        remaining_ah / charge_current_a * 1.2, 2
    )
    result["status"] = "Rough estimate"

    if charge_current_a > SCREENING_CURRENT_A:
        result["current_screening"] = "Review required"
    else:
        result["current_screening"] = (
            "Within screening threshold; not safety-certified"
        )

    if not result["message"]:
        result["message"] = (
            "Approximation only. Confirm the charger profile, battery "
            "temperature and manufacturer-approved charging current."
        )

    return result


def idle_charge_loss(
    starting_soc_percent: Optional[float],
    ending_soc_percent: Optional[float],
    elapsed_hours: Optional[float]
) -> Prediction:
    """Calculate observed SOC change over an idle period."""

    if (
        starting_soc_percent is None
        or ending_soc_percent is None
        or elapsed_hours is None
        or elapsed_hours <= 0
        or not 0 <= starting_soc_percent <= 100
        or not 0 <= ending_soc_percent <= 100
    ):
        return Prediction(
            None,
            "% per day",
            "Insufficient data",
            "Provide two valid SOC readings and positive elapsed hours."
        )

    loss_per_day = (
        (starting_soc_percent - ending_soc_percent)
        / elapsed_hours * 24
    )

    if loss_per_day < 0:
        return Prediction(
            round(loss_per_day, 3),
            "% per day",
            "SOC increased",
            "SOC increased between readings. Check charging activity "
            "and measurement variation."
        )

    return Prediction(
        round(loss_per_day, 3),
        "% per day",
        "Observed estimate",
        "Calculated from two SOC readings. This does not independently "
        "prove battery self-discharge."
    )
