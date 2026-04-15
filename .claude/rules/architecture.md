# Architecture

> For physical file locations and import graph, always query `graphify-out/` — never infer from this file.

## Core Triad (hyperedge — every platform depends on all three)

```
ToyotaDataUpdateCoordinator  ←─── god node #1 (63 edges)
  polls pytoyoda every 5 min
  holds ToyotaCoordinatorData  ←── god node #3
    .vehicle: Vehicle
    .day/week/month/year_summary: Summary | None
    .last_trip: Trip | None
    .service_history: ServiceHistory | None

ToyotaBaseEntity  ←───────────────── god node #2 (53 edges)
  CoordinatorEntity[ToyotaDataUpdateCoordinator]
  all platform entities inherit from this
  exposes DeviceInfo grouped by VIN
```

## Module Responsibilities

- `const.py` — DOMAIN, PLATFORMS list, config keys, UPDATE_INTERVAL_MINUTES, MANUFACTURER, MODEL. No logic.
- `coordinator.py` — `ToyotaCoordinatorData` dataclass + `ToyotaDataUpdateCoordinator`. Owns all API calls. Uses `_safe_fetch` to isolate optional data (summaries, trips) from hard failures.
- `base_entity.py` — `ToyotaBaseEntity`. Stores `self._vin`, builds `DeviceInfo`. No platform logic.
- `__init__.py` — Entry setup/teardown. Creates `MyT` client, logs in, fetches vehicles, builds one coordinator per vehicle, calls `async_config_entry_first_refresh`, stores list in `entry.runtime_data`. Defines `ToyotaConfigEntry` type alias.
- `config_flow.py` — Single-step user flow (email + password). Validates by attempting login. Sets unique_id to lowercased email.
- Platform files (`sensor`, `binary_sensor`, `lock`, `device_tracker`, `button`) — each follows the **Platform Pattern** below.

## Platform Pattern

Every platform file has exactly this shape:

1. **Description dataclass** — `@dataclass(frozen=True, kw_only=True)` extending the HA description base, adding `value_fn: Callable[[ToyotaCoordinatorData], T]`.
2. **Description tuple** — module-level constant, all descriptions declared inline.
3. **Entity class** — inherits `ToyotaBaseEntity` + HA platform entity. Sets `unique_id = f"{self._vin}_{description.key}"` in `__init__`. Reads state via `self.entity_description.value_fn(self.coordinator.data)`.
4. **`async_setup_entry`** — iterates `entry.runtime_data` (list of coordinators), creates one entity per coordinator (× description for multi-entity platforms).

## Key Design Decisions

**Climate endpoints stripped at init** (`coordinator.py:54`): Toyota's climate GET endpoints return `ONE_GLOBAL_RS_40000` (HTTP 500), which breaks `asyncio.gather()` inside `vehicle.update()`. The coordinator removes `climate_settings` and `climate_status` from `_endpoint_collect` once at init rather than catching per-call.

**`_safe_fetch` pattern**: Optional data (summaries, trips, service history) is fetched via `_safe_fetch(coro_fn, label)` which returns `None` on any exception and logs at DEBUG. Core vehicle update failure raises `UpdateFailed` or `ConfigEntryAuthFailed` instead.

**`entry.runtime_data`**: Coordinators are stored as `list[ToyotaDataUpdateCoordinator]` on the config entry. Platforms read this directly — no `hass.data` dict.

**`pytoyoda` lazy import**: Imported inside `async_setup_entry` and `async_step_user` with `# noqa: PLC0415` to avoid HA startup failures when the package is not yet installed.

**Lock post-command refresh**: After `post_command()`, `async_call_later(hass, 20, _refresh_status)` schedules a refresh 20 s later to reflect the new lock state — Toyota API has a propagation delay.
