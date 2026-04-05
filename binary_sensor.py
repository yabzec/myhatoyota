"""Binary sensor platform for Toyota Custom integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaCoordinatorData, ToyotaDataUpdateCoordinator

PARALLEL_UPDATES = 0


def _closed_to_is_on(closed: Any) -> bool | None:
    """Convert a pytoyoda 'closed' value to a binary sensor is_on value.

    Returns True (open/alert) when closed is explicitly False.
    Returns None when the value is None or unavailable — prevents None being
    treated as falsy and incorrectly showing the sensor as open.
    """
    if closed is None:
        return False
    return not closed


@dataclass(frozen=True, kw_only=True)
class ToyotaBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Extends BinarySensorEntityDescription with a value_fn.

    is_on=True means the "alert" state: door OPEN, window OPEN.
    """

    value_fn: Callable[[ToyotaCoordinatorData], bool | None] = lambda _: None


BINARY_SENSOR_DESCRIPTIONS: tuple[ToyotaBinarySensorEntityDescription, ...] = (
    # ---- Doors (is_on = True → door is OPEN) --------------------------------
    ToyotaBinarySensorEntityDescription(
        key="door_driver",
        translation_key="door_driver",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.doors.driver_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.driver_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="door_driver_rear",
        translation_key="door_driver_rear",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.doors.driver_rear_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.driver_rear_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="door_passenger",
        translation_key="door_passenger",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.doors.passenger_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.passenger_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="door_passenger_rear",
        translation_key="door_passenger_rear",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.doors.passenger_rear_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.passenger_rear_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="door_trunk",
        translation_key="door_trunk",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.doors.trunk.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.trunk
            else None
        ),
    ),
    # ---- Hood (is_on = True → hood is OPEN) ---------------------------------
    ToyotaBinarySensorEntityDescription(
        key="hood",
        translation_key="hood",
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.hood.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.hood
            else None
        ),
    ),
    # ---- Windows (is_on = True → window is OPEN) ----------------------------
    ToyotaBinarySensorEntityDescription(
        key="window_driver",
        translation_key="window_driver",
        device_class=BinarySensorDeviceClass.WINDOW,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.windows.driver_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.windows and d.vehicle.lock_status.windows.driver_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="window_driver_rear",
        translation_key="window_driver_rear",
        device_class=BinarySensorDeviceClass.WINDOW,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.windows.driver_rear_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.windows and d.vehicle.lock_status.windows.driver_rear_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="window_passenger",
        translation_key="window_passenger",
        device_class=BinarySensorDeviceClass.WINDOW,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.windows.passenger_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.windows and d.vehicle.lock_status.windows.passenger_seat
            else None
        ),
    ),
    ToyotaBinarySensorEntityDescription(
        key="window_passenger_rear",
        translation_key="window_passenger_rear",
        device_class=BinarySensorDeviceClass.WINDOW,
        value_fn=lambda d: (
            _closed_to_is_on(d.vehicle.lock_status.windows.passenger_rear_seat.closed)
            if d.vehicle.lock_status and d.vehicle.lock_status.windows and d.vehicle.lock_status.windows.passenger_rear_seat
            else None
        ),
    ),
)


class ToyotaBinarySensor(ToyotaBaseEntity, BinarySensorEntity):
    """A single Toyota binary sensor."""

    entity_description: ToyotaBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: ToyotaDataUpdateCoordinator,
        description: ToyotaBinarySensorEntityDescription,
    ) -> None:
        """Initialise the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._vin}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return True when the door/window is open."""
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (AttributeError, TypeError):
            return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota binary sensors from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    async_add_entities(
        ToyotaBinarySensor(coordinator, description)
        for coordinator in coordinators
        for description in BINARY_SENSOR_DESCRIPTIONS
    )
