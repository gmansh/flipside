from datetime import datetime

_settings = {
    "enabled": False,
    "start_hour": 22,
    "end_hour": 7,
}


def get_settings() -> dict:
    return dict(_settings)


def update_settings(enabled: bool | None = None, start_hour: int | None = None, end_hour: int | None = None) -> dict:
    if enabled is not None:
        _settings["enabled"] = enabled
    if start_hour is not None:
        if not (0 <= start_hour <= 23):
            raise ValueError("start_hour must be 0-23")
        _settings["start_hour"] = start_hour
    if end_hour is not None:
        if not (0 <= end_hour <= 23):
            raise ValueError("end_hour must be 0-23")
        _settings["end_hour"] = end_hour
    return dict(_settings)


def is_quiet() -> bool:
    """Return True if board updates should be suppressed right now."""
    if not _settings["enabled"]:
        return False
    now_hour = datetime.now().hour
    start = _settings["start_hour"]
    end = _settings["end_hour"]
    if start < end:
        # e.g. 9 AM to 5 PM
        return start <= now_hour < end
    else:
        # wraps midnight, e.g. 10 PM to 7 AM
        return now_hour >= start or now_hour < end
