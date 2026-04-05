"""Lock platform for Toyota Custom integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.lock import LockEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_call_later
from pytoyoda.models.endpoints.command import CommandType

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


class ToyotaBaseLock(ToyotaBaseEntity, LockEntity):
    """Shared base for Toyota lock entities."""

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise base lock state."""
        super().__init__(coordinator)
        self._is_locking: bool = False
        self._is_unlocking: bool = False

    @property
    def is_locking(self) -> bool:
        """Return True while a lock command is in-flight."""
        return self._is_locking

    @property
    def is_unlocking(self) -> bool:
        """Return True while an unlock command is in-flight."""
        return self._is_unlocking


    async def _refresh_status(self, now) -> None:
        self._is_locking = False
        self._is_unlocking = False
        await self.coordinator.async_request_refresh()

    async def _send(self, command: CommandType) -> None:
        """Send a command and refresh coordinator data."""
        try:
            await self.coordinator.data.vehicle.post_command(command)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Toyota command %s failed: %s", command, err)
        finally:
            async_call_later(self.hass, 20, self._refresh_status)


class ToyotaDoorsLock(ToyotaBaseLock):
    """Lock/unlock all main doors."""

    _attr_translation_key = "doors"

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise the doors lock."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_doors_lock"

    @property
    def is_locked(self) -> bool | None:
        """Return True when all four main doors are locked."""
        lock = self.coordinator.data.vehicle.lock_status
        if lock is None or lock.doors is None:
            return None
        doors = lock.doors
        locked_states = []
        for attr in ("driver_seat", "passenger_seat", "driver_rear_seat", "passenger_rear_seat"):
            door = getattr(doors, attr, None)
            if door is not None and door.locked is not None:
                locked_states.append(door.locked)
        if not locked_states:
            return None
        return all(locked_states)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock all doors."""
        self._is_locking = True
        self.async_write_ha_state()
        await self._send(CommandType.DOOR_LOCK)

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock all doors."""
        self._is_unlocking = True
        self.async_write_ha_state()
        await self._send(CommandType.DOOR_UNLOCK)


class ToyotaTrunkLock(ToyotaBaseLock):
    """Lock/unlock the trunk separately."""

    _attr_translation_key = "trunk"

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Initialise the trunk lock."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._vin}_trunk_lock"

    @property
    def is_locked(self) -> bool | None:
        """Return True when the trunk is locked."""
        lock = self.coordinator.data.vehicle.lock_status
        if lock is None or lock.doors is None or lock.doors.trunk is None:
            return None
        return lock.doors.trunk.locked

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the trunk."""
        self._is_locking = True
        self.async_write_ha_state()
        await self._send(CommandType.TRUNK_LOCK)

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the trunk."""
        self._is_unlocking = True
        self.async_write_ha_state()
        await self._send(CommandType.TRUNK_UNLOCK)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota lock entities from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    entities: list[ToyotaBaseLock] = []
    for coordinator in coordinators:
        entities.append(ToyotaDoorsLock(coordinator))
        entities.append(ToyotaTrunkLock(coordinator))
    async_add_entities(entities)
