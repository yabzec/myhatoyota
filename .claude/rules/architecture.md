# Architecture

## Component Interaction Chain

```
User adds integration
        ↓
config_flow.py          validates credentials, creates ConfigEntry
        ↓
__init__.py             async_setup_entry: instantiates MyT client,
                        creates one ToyotaDataUpdateCoordinator per vehicle,
                        forwards setup to all platforms
        ↓
coordinator.py          polls Toyota API every 5 min via pytoyoda,
                        stores results in ToyotaCoordinatorData dataclass
        ↓
base_entity.py          ToyotaBaseEntity(CoordinatorEntity): shared device_info,
                        VIN-based unique_id, _attr_has_entity_name=True
        ↓
Platform modules        each extends ToyotaBaseEntity + HA platform entity
  sensor.py             ToyotaSensorEntity
  binary_sensor.py      ToyotaBinarySensor
  lock.py               ToyotaBaseLock → ToyotaDoorsLock / ToyotaTrunkLock
  device_tracker.py     ToyotaDeviceTracker
```

## Data Flow (read path)

1. `ToyotaDataUpdateCoordinator._async_update_data()` fires every 5 min
2. Calls `vehicle.update()` + 6 optional `_safe_fetch()` calls
3. Returns `ToyotaCoordinatorData` (dataclass with vehicle + summaries + trips + service)
4. HA coordinator notifies all subscribed entities
5. Each entity's `native_value` / `is_on` / etc. reads from `self.coordinator.data`

## Command Flow (write path)

1. User triggers action (lock/unlock door, set HVAC mode)
2. Entity calls `await self.coordinator.data.vehicle.post_command(CommandType.X)`
3. Entity sets `_is_locking / _is_unlocking` flag, writes async state
4. `finally` block resets flag + calls `await self.coordinator.async_request_refresh()`
5. Coordinator fetches fresh data → all entities update

## Key Types

| Type | File | Role |
|------|------|------|
| `ToyotaConfigEntry` | `__init__.py` | `ConfigEntry[list[ToyotaDataUpdateCoordinator]]` type alias |
| `ToyotaCoordinatorData` | `coordinator.py` | Dataclass holding all fetched vehicle data |
| `ToyotaDataUpdateCoordinator` | `coordinator.py` | One instance per vehicle; owns polling lifecycle |
| `ToyotaBaseEntity` | `base_entity.py` | Shared base for all 4 platform entity types |
| `ToyotaSensorEntityDescription` | `sensor.py` | Extends `SensorEntityDescription` with `value_fn` callable |

## Entity Description Pattern

Entities are defined declaratively as tuples of description dataclasses:

```python
@dataclass(frozen=True, kw_only=True)
class ToyotaSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[ToyotaCoordinatorData], Any] = lambda _: None

_DASHBOARD_SENSORS: tuple[ToyotaSensorEntityDescription, ...] = (
    ToyotaSensorEntityDescription(
        key="odometer",
        name="Odometer",
        value_fn=lambda d: d.vehicle.dashboard.odometer,
        ...
    ),
)
```

Factory functions (`_make_summary_sensors()`) generate repetitive sets from a single template.
`async_setup_entry` iterates all description tuples and instantiates entity objects.

## Scaling Notes

- One coordinator per vehicle; supports multiple vehicles per account
- `PARALLEL_UPDATES = 0` on command platforms (lock) to prevent race conditions
- Data fetching is sequential, not parallelised within a coordinator
