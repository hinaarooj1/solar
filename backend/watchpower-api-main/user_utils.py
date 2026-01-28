from typing import Any, Dict


def _get_watchpower_block(user: Dict[str, Any]) -> Dict[str, Any]:
    watchpower = user.get("watchpower")
    if not watchpower:
        raise ValueError("WatchPower credentials missing for user")
    required_fields = [
        "username",
        "password",
        "serial_number",
        "wifi_pn",
        "dev_code",
        "dev_addr",
    ]
    missing = [field for field in required_fields if field not in watchpower]
    if missing:
        raise ValueError(f"Missing WatchPower fields: {', '.join(missing)}")
    return watchpower


def get_watchpower_credentials(user: Dict[str, Any]) -> Dict[str, str]:
    block = _get_watchpower_block(user)
    return {
        "username": block["username"],
        "password": block["password"],
    }


def get_device_identifiers(user: Dict[str, Any]) -> Dict[str, Any]:
    block = _get_watchpower_block(user)
    return {
        "serial_number": block["serial_number"],
        "wifi_pn": block["wifi_pn"],
        "dev_code": int(block["dev_code"]),
        "dev_addr": int(block["dev_addr"]),
    }


