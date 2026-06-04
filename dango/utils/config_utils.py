def env_onoff_to_bool(value, default=False):
    """Convert 'on'/'off' env var string to bool."""
    if value is None:
        return default
    return value.lower() == "on"


def env_bool(value, default=False):
    """Convert 'true'/'false' (or '1'/'0') env var string to bool."""
    if value is None:
        return default
    return value.lower() in ("true", "1")
