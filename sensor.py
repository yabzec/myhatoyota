"""Sensor platform for Toyota Custom integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
    UnitOfVolume,
    UnitOfSpeed,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import ToyotaConfigEntry
from .base_entity import ToyotaBaseEntity
from .coordinator import ToyotaCoordinatorData, ToyotaDataUpdateCoordinator

PARALLEL_UPDATES = 0

# L/100km is not a standard HA unit — expose as a plain state with unit_of_measurement
UNIT_L_PER_100KM = "L/100km"


@dataclass(frozen=True, kw_only=True)
class ToyotaSensorEntityDescription(SensorEntityDescription):
    """Extends SensorEntityDescription with a value_fn."""

    value_fn: Callable[[ToyotaCoordinatorData], Any] = lambda _: None


def _timedelta_to_minutes(td: timedelta | None) -> float | None:
    if td is None:
        return None
    return round(td.total_seconds() / 60, 1)


# ---------------------------------------------------------------------------
# Dashboard sensors
# ---------------------------------------------------------------------------
_DASHBOARD_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    ToyotaSensorEntityDescription(
        key="odometer",
        translation_key="odometer",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:counter",
        value_fn=lambda d: d.vehicle.dashboard.odometer if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="fuel_level",
        translation_key="fuel_level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:gas-station",
        value_fn=lambda d: d.vehicle.dashboard.fuel_level if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="fuel_range",
        translation_key="fuel_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:map-marker-distance",
        value_fn=lambda d: d.vehicle.dashboard.fuel_range if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="battery_level",
        translation_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-heart-variant",
        value_fn=lambda d: d.vehicle.dashboard.battery_level if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="battery_range",
        translation_key="battery_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda d: d.vehicle.dashboard.battery_range if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="battery_range_with_ac",
        translation_key="battery_range_with_ac",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda d: d.vehicle.dashboard.battery_range_with_ac if d.vehicle.dashboard else None,
    ),
    ToyotaSensorEntityDescription(
        key="total_range",
        translation_key="total_range",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:map-marker-distance",
        value_fn=lambda d: d.vehicle.dashboard.range if d.vehicle.dashboard else None,
    ),
)

# ---------------------------------------------------------------------------
# Summary sensors helper
# ---------------------------------------------------------------------------
def _make_summary_sensors(prefix: str, label: str, attr: str) -> tuple[ToyotaSensorEntityDescription, ...]:
    """Build 6 sensors for a given summary period."""
    return (
        ToyotaSensorEntityDescription(
            key=f"{prefix}_distance",
            translation_key=f"{prefix}_distance",
            native_unit_of_measurement=UnitOfLength.KILOMETERS,
            device_class=SensorDeviceClass.DISTANCE,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:road",
            value_fn=lambda d, a=attr: getattr(d, a).distance if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_fuel_consumed",
            translation_key=f"{prefix}_fuel_consumed",
            native_unit_of_measurement=UnitOfVolume.LITERS,
            device_class=SensorDeviceClass.VOLUME,
            state_class=SensorStateClass.TOTAL,
            icon="mdi:gas-station",
            value_fn=lambda d, a=attr: getattr(d, a).fuel_consumed if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_avg_fuel_consumed",
            translation_key=f"{prefix}_avg_fuel_consumed",
            native_unit_of_measurement=UNIT_L_PER_100KM,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:gauge",
            value_fn=lambda d, a=attr: getattr(d, a).average_fuel_consumed if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_ev_distance",
            translation_key=f"{prefix}_ev_distance",
            native_unit_of_measurement=UnitOfLength.KILOMETERS,
            device_class=SensorDeviceClass.DISTANCE,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:lightning-bolt",
            value_fn=lambda d, a=attr: getattr(d, a).ev_distance if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_ev_duration",
            translation_key=f"{prefix}_ev_duration",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:clock-outline",
            value_fn=lambda d, a=attr: _timedelta_to_minutes(getattr(d, a).ev_duration) if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_average_speed",
            translation_key=f"{prefix}_average_speed",
            native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
            device_class=SensorDeviceClass.SPEED,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:speedometer",
            value_fn=lambda d, a=attr: getattr(d, a).average_speed if getattr(d, a) else None,
        ),
    )


_SUMMARY_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    *_make_summary_sensors("day", "Today", "day_summary"),
    *_make_summary_sensors("week", "This Week", "week_summary"),
    *_make_summary_sensors("month", "This Month", "month_summary"),
    *_make_summary_sensors("year", "This Year", "year_summary"),
)

# ---------------------------------------------------------------------------
# Last trip sensors
# ---------------------------------------------------------------------------
_LAST_TRIP_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    ToyotaSensorEntityDescription(
        key="last_trip_distance",
        translation_key="last_trip_distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:road",
        value_fn=lambda d: d.last_trip.distance if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_fuel_consumed",
        translation_key="last_trip_fuel_consumed",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.VOLUME,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gas-station",
        value_fn=lambda d: d.last_trip.fuel_consumed if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_avg_fuel",
        translation_key="last_trip_avg_fuel",
        native_unit_of_measurement=UNIT_L_PER_100KM,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        value_fn=lambda d: d.last_trip.average_fuel_consumed if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_ev_distance",
        translation_key="last_trip_ev_distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightning-bolt",
        value_fn=lambda d: d.last_trip.ev_distance if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_ev_duration",
        translation_key="last_trip_ev_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:clock-outline",
        value_fn=lambda d: _timedelta_to_minutes(d.last_trip.ev_duration) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_score",
        translation_key="last_trip_score",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:star",
        value_fn=lambda d: round(d.last_trip.score, 1) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_score_acceleration",
        translation_key="last_trip_score_acceleration",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-speed-limiter",
        value_fn=lambda d: round(d.last_trip.score_acceleration, 1) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_score_braking",
        translation_key="last_trip_score_braking",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:car-brake-alert",
        value_fn=lambda d: round(d.last_trip.score_braking, 1) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_score_advice",
        translation_key="last_trip_score_advice",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:lightbulb",
        value_fn=lambda d: round(d.last_trip.score_advice, 1) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_score_constant_speed",
        translation_key="last_trip_score_constant_speed",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:speedometer",
        value_fn=lambda d: round(d.last_trip.score_constant_speed, 1) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_start",
        translation_key="last_trip_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-start",
        value_fn=lambda d: d.last_trip.start_time if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_end",
        translation_key="last_trip_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
        value_fn=lambda d: d.last_trip.end_time if d.last_trip else None,
    ),
)

# ---------------------------------------------------------------------------
# Service history sensors
# ---------------------------------------------------------------------------
_SERVICE_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    ToyotaSensorEntityDescription(
        key="last_service_date",
        translation_key="last_service_date",
        device_class=SensorDeviceClass.DATE,
        icon="mdi:wrench-clock",
        value_fn=lambda d: d.service_history.service_date if d.service_history else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_service_odometer",
        translation_key="last_service_odometer",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:counter",
        value_fn=lambda d: d.service_history.odometer if d.service_history else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_service_category",
        translation_key="last_service_category",
        icon="mdi:tag",
        value_fn=lambda d: d.service_history.service_category if d.service_history else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_service_provider",
        translation_key="last_service_provider",
        icon="mdi:store",
        value_fn=lambda d: d.service_history.service_provider if d.service_history else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_service_notes",
        translation_key="last_service_notes",
        icon="mdi:note-text",
        value_fn=lambda d: d.service_history.notes if d.service_history else None,
    ),
)

# ---------------------------------------------------------------------------
# Miscellaneous sensors
# ---------------------------------------------------------------------------
_MISC_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    ToyotaSensorEntityDescription(
        key="unread_notifications",
        translation_key="unread_notifications",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:bell-alert",
        value_fn=lambda d: sum(
            1 for n in (d.vehicle.notifications or []) if not n.read
        ),
    ),
    ToyotaSensorEntityDescription(
        key="vehicle_type",
        translation_key="vehicle_type",
        icon="mdi:car-info",
        value_fn=lambda d: d.vehicle.type,
    ),
    ToyotaSensorEntityDescription(
        key="vehicle_alias",
        translation_key="vehicle_alias",
        icon="mdi:tag-text",
        value_fn=lambda d: d.vehicle.alias,
    ),
)

SENSOR_DESCRIPTIONS: tuple[ToyotaSensorEntityDescription, ...] = (
    *_DASHBOARD_SENSORS,
    *_SUMMARY_SENSORS,
    *_LAST_TRIP_SENSORS,
    *_SERVICE_SENSORS,
    *_MISC_SENSORS,
)


class ToyotaSensorEntity(ToyotaBaseEntity, SensorEntity):
    """A single Toyota sensor."""

    entity_description: ToyotaSensorEntityDescription

    def __init__(
        self,
        coordinator: ToyotaDataUpdateCoordinator,
        description: ToyotaSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._vin}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value, safely handling None chains."""
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except (AttributeError, TypeError):
            return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota sensors from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    async_add_entities(
        ToyotaSensorEntity(coordinator, description)
        for coordinator in coordinators
        for description in SENSOR_DESCRIPTIONS
    )
