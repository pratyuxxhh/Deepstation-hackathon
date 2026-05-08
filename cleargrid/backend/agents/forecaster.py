"""Agent 2: Forecaster — Overflow prediction."""


def run_forecaster(bins: list[dict]) -> list[dict]:
    """
    Agent 2: Predictive overflow analysis.
    Re-evaluates each bin's BLUE flag based on overflow vs cycle timing.
    Mutates status_color only if current color is GREEN.
    Returns the updated bin list.
    """
    for bin in bins:
        # Never override PURPLE (hazard takes precedence)
        if bin["hazard_detected"]:
            continue

        will_overflow_before_collection = (
            bin["predicted_overflow_hrs"] < bin["time_to_next_cycle_hrs"]
        )

        if will_overflow_before_collection and bin["status_color"] == "GREEN":
            bin["status_color"] = "BLUE"
            bin["collection_required"] = True
            bin["collection_reason"] = "PREDICTIVE_OVERFLOW"

    return bins
