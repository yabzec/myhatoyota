"""Climate platform for Toyota Custom integration.

Maps the Toyota remote climate system to a HA ClimateEntity.

Important notes for the Yaris Cross Full Hybrid:
- Climate is started via AC_SETTINGS_ON command.
- Climate is stopped via ENGINE_STOP command (this is the Toyota remote-session
  stop command — it does NOT affect a physically running engine).
- There is no direct "set target temperature" API command; temperature is
  configured inside the Toyota app and reflected in climate_settings/climate_status.
  Therefore target_temperature is exposed as a read-only attribute.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


def _temperature_value(temp_obj: Any) -> float | None:
    """Extract the numeric value from a pytoyoda Temperature model."""
    if temp_obj is None:
        return None
    # Temperature model exposes .value (float) and .unit (str)
    value = getattr(temp_obj, "value", None)
    return float(value) if value is not None else None


class ToyotaClimate(ToyotaBaseEntity, ClimateEntity):
    """Remote climate control for the Toyota vehicle.

    Supported HVAC modes:
      OFF  — remote climate session is inactive
      COOL — remote AC session (type "AC")
      HEAT — remote PTC heater session (type "PTC")
    Temperature is read-only (no remote set-temp command available).
    """

    _attr_name = "Climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT]
    # Temperature display is read-only; no target-temperature control feature.
    _attr_supported_features = ClimateEntityFeature(0)

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise the climate entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_climate"

    # ------------------------------------------------------------------
    # State properties
    # ------------------------------------------------------------------

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode derived from climate_status."""
        cs = self.coordinator.data.vehicle.climate_status
        if cs is None or not cs.status:
            return HVACMode.OFF
        climate_type = getattr(cs, "type", None) or ""
        if climate_type.upper() == "PTC":
            return HVACMode.HEAT
        return HVACMode.COOL

    @property
    def current_temperature(self) -> float | None:
        """Return the current cabin temperature."""
        cs = self.coordinator.data.vehicle.climate_status
        if cs is None:
            return None
        return _temperature_value(getattr(cs, "current_temperature", None))

    @property
    def target_temperature(self) -> float | None:
        """Return the configured target temperature (read-only)."""
        cs = self.coordinator.data.vehicle.climate_status
        if cs is None:
            return None
        return _temperature_value(getattr(cs, "target_temperature", None))

    @property
    def min_temp(self) -> float:
        """Return minimum configurable temperature."""
        settings = self.coordinator.data.vehicle.climate_settings
        if settings and settings.min_temp is not None:
            return float(settings.min_temp)
        return 16.0

    @property
    def max_temp(self) -> float:
        """Return maximum configurable temperature."""
        settings = self.coordinator.data.vehicle.climate_settings
        if settings and settings.max_temp is not None:
            return float(settings.max_temp)
        return 32.0

    @property
    def target_temperature_step(self) -> float:
        """Return the temperature adjustment step."""
        settings = self.coordinator.data.vehicle.climate_settings
        if settings and settings.temp_interval is not None:
            return float(settings.temp_interval)
        return 0.5

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose additional climate details."""
        cs = self.coordinator.data.vehicle.climate_status
        if cs is None:
            return {}
        attrs: dict[str, Any] = {}
        if cs.start_time:
            attrs["start_time"] = cs.start_time.isoformat()
        if cs.duration:
            attrs["duration_minutes"] = round(cs.duration.total_seconds() / 60, 1)
        if cs.options:
            attrs["front_defogger"] = cs.options.front_defogger
            attrs["rear_defogger"] = cs.options.rear_defogger
        return attrs

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Start or stop the remote climate session."""
        try:
            from pytoyoda.models.endpoints.command import CommandType  # noqa: PLC0415
        except ImportError:
            _LOGGER.error("pytoyoda CommandType not available")
            return

        if hvac_mode == HVACMode.OFF:
            # ENGINE_STOP ends the remote climate session (not the physical engine).
            _LOGGER.debug("Stopping Toyota remote climate session")
            await self._send_command(CommandType.ENGINE_STOP)
        else:
            # AC_SETTINGS_ON starts the remote climate session.
            # The car decides heat vs cool based on ambient temperature unless
            # the user pre-configured a mode via the Toyota app.
            _LOGGER.debug("Starting Toyota remote climate session")
            await self._send_command(CommandType.AC_SETTINGS_ON)

        await self.coordinator.async_request_refresh()

    async def _send_command(self, command: Any) -> None:
        """Send a command to the vehicle, logging on failure."""
        try:
            await self.coordinator.data.vehicle.post_command(command)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Toyota climate command %s failed: %s", command, err)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota climate from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    async_add_entities(ToyotaClimate(coordinator) for coordinator in coordinators)
