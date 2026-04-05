"""Base entity class shared across all Toyota platforms."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import ToyotaDataUpdateCoordinator


class ToyotaBaseEntity(CoordinatorEntity[ToyotaDataUpdateCoordinator]):
    """Common base for all Toyota entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator) -> None:
        """Store the VIN for use in unique_id and device_info."""
        super().__init__(coordinator)
        self._vin: str = coordinator.data.vehicle.vin or "unknown"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info that groups all entities under one device per VIN."""
        vehicle = self.coordinator.data.vehicle
        name = vehicle.alias or f"Toyota {self._vin[-6:]}"
        return DeviceInfo(
            identifiers={(DOMAIN, self._vin)},
            name=name,
            manufacturer=MANUFACTURER,
            model=MODEL,
            serial_number=self._vin,
        )
