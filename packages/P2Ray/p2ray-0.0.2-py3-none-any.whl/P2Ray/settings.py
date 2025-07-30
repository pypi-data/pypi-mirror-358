from typing import TypedDict


class SettingsDict(TypedDict):
    """
    Application settings persisted in JSON.
    """
    log_level: str         # e.g. "DEBUG", "INFO", "WARNING", etc.
    default_timeout: float
    v2ray_path: str
    
    # (future fields go here, e.g. default_timeout, v2ray_path, etc.)


DEFAULT_SETTINGS: SettingsDict = {
    "log_level": "INFO",
    "default_timeout": 15.0,
    "v2ray_path": "v2ray",
}

# A parallel schema of allowed values or validators
ValidValue = list[str] | range | tuple  # e.g. list of strings, numeric range, etc.
VALID_SETTINGS: dict[str, ValidValue] = {
    "log_level": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    # For numeric fields, you could specify a (min, max) tuple:
    "default_timeout": (0.1, 300.0),  # allowed from 0.1 to 300 seconds
    # No real constraint on v2ray_path (any non-empty string):
    "v2ray_path": []
}