"""Constants for the Toyota Custom integration."""
from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "toyota_custom"

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.LOCK,
    Platform.CLIMATE,
]

CONF_EMAIL = "email"
CONF_PASSWORD = "password"

UPDATE_INTERVAL_MINUTES = 5

MANUFACTURER = "Toyota"
MODEL = "Yaris Cross"
