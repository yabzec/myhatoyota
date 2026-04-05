"""Device tracker platform for Toyota Custom integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaDataUpdateCoordinator

PARALLEL_UPDATES = 0


class ToyotaDeviceTracker(ToyotaBaseEntity, TrackerEntity):
    """Tracks the parking location of the vehicle via GPS."""

    _attr_translation_key = "location"
    _attr_source_type = SourceType.GPS
    _attr_icon = "mdi:car-marker"

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise the tracker."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_location"

    @property
    def latitude(self) -> float | None:
        """Return the latest latitude."""
        loc = self.coordinator.data.vehicle.location
        return loc.latitude if loc else None

    @property
    def longitude(self) -> float | None:
        """Return the latest longitude."""
        loc = self.coordinator.data.vehicle.location
        return loc.longitude if loc else None

    @property
    def location_accuracy(self) -> int:
        """Return 0 — Toyota API does not expose GPS accuracy."""
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose extra location metadata as attributes."""
        loc = self.coordinator.data.vehicle.location
        if loc is None:
            return {}
        return {
            "state": loc.state,
            "timestamp": loc.timestamp.isoformat() if loc.timestamp else None,
        }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota device tracker from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    async_add_entities(
        ToyotaDeviceTracker(coordinator) for coordinator in coordinators
    )
