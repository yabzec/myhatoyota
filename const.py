"""Constants for the Toyota Custom integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "myhatoyota"

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.LOCK,
]

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

UPDATE_INTERVAL_MINUTES = 5

MANUFACTURER = "Toyota"
MODEL = "Yaris Cross"
