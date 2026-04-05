"""Button platform for Toyota Custom integration."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


class ToyotaForceRefreshButton(ToyotaBaseEntity, ButtonEntity):
    """Button that triggers an immediate coordinator refresh."""

    _attr_name = "Force Refresh"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise the force refresh button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_force_refresh"

    async def async_press(self) -> None:
        """Trigger an immediate data refresh."""
        _LOGGER.debug("Force refresh requested for vehicle %s", self._vin)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota button from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    async_add_entities(
        ToyotaForceRefreshButton(coordinator) for coordinator in coordinators
    )
