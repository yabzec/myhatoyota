# Coding Style & Principles

## Naming Conventions

| Target | Convention | Example |
|--------|-----------|---------|
| Constants | `UPPER_SNAKE_CASE` | `DOMAIN`, `UPDATE_INTERVAL_MINUTES` |
| Module logger | `_LOGGER` (private, upper) | `_LOGGER = logging.getLogger(__name__)` |
| Classes | `PascalCase` with `Toyota` prefix | `ToyotaBaseEntity`, `ToyotaClimate` |
| Public methods/functions | `snake_case` | `get_vehicles()` |
| Async methods | `async_` prefix | `async_setup_entry`, `async_lock` |
| Private methods/attrs | `_leading_underscore` | `_vin`, `_safe_fetch`, `_is_locking` |
| Type aliases | PascalCase (`type` syntax) | `type ToyotaConfigEntry = ...` |
| File names | `snake_case` matching HA platform | `binary_sensor.py`, `device_tracker.py` |

## Imports

Always in this order, each group separated by a blank line:

```python
"""Module docstring."""

from __future__ import annotations  # always first

# 1. Standard library (alphabetical)
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

# 2. Home Assistant / third-party (alphabetical)
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant

# 3. Local (relative, alphabetical)
from . import ToyotaConfigEntry
from .coordinator import ToyotaDataUpdateCoordinator
```

Lazy imports (inside `try/except` blocks to handle optional deps) must use `# noqa: PLC0415`.

## Type Annotations

- Modern PEP 604 union syntax: `bool | None`, `Any | None` — never `Optional[X]`
- Modern `type` alias syntax (Python 3.12): `type ToyotaConfigEntry = ConfigEntry[...]`
- Return types on all functions, including `-> None`
- Use `Any` for pytoyoda model fields where types are unclear
- Generic coordinators: `DataUpdateCoordinator[ToyotaCoordinatorData]`

## Docstrings

Required on every:
- Module (first line of file, single-line OK: `"""Toyota Custom integration setup."""`)
- Class (single-line for simple, multi-line when explaining API constraints or design decisions)
- Public method/function

Multi-line docstrings are used to explain non-obvious things: API limitations, design tradeoffs, why a command uses an unexpected enum value. Keep them factual, not verbose.

## Comments

- **ASCII section dividers** separate logical groups within a file:
  ```python
  # ---------------------------------------------------------------------------
  # Dashboard sensors
  # ---------------------------------------------------------------------------
  ```
  or shorter:
  ```python
  # ---- Doors (is_on = True → door is OPEN) --------------------------------
  ```
- Inline comments explain intent or suppress linting (`# noqa: BLE001`, `# Suppress loguru noise`)
- No redundant comments that restate what the code says

## Error Handling

1. **Specific exceptions first**, generic `Exception` last
2. **Always chain exceptions:** `raise XxxError("msg") from err`
3. **Broad catches:** allowed only with `# noqa: BLE001`
4. **Non-fatal fetch failures:** catch, log at `debug` level, return `None` — never raise
5. **Fatal startup failures:** raise HA exceptions:
   - `ConfigEntryAuthFailed` — bad credentials
   - `ConfigEntryNotReady` — transient startup issue
   - `UpdateFailed` — coordinator poll failure
6. **Command failures:** log as `warning`, do not re-raise; always reset state flags in `finally`

```python
# Correct pattern for _safe_fetch
async def _safe_fetch(self, coro_fn: Any, label: str) -> Any | None:
    try:
        return await coro_fn()
    except Exception as err:  # noqa: BLE001
        _LOGGER.debug("Could not fetch %s: %s", label, err)
        return None
```

## Defensive Programming

- Multi-level `None` guards before accessing nested attributes:
  ```python
  value_fn=lambda d: (
      not d.vehicle.lock_status.doors.driver_seat.closed
      if d.vehicle.lock_status
      and d.vehicle.lock_status.doors
      and d.vehicle.lock_status.doors.driver_seat
      else None
  )
  ```
- `native_value` on sensors catches `AttributeError` and `TypeError`, returns `None`
- Safe defaults over exceptions for read-only properties (return `0`, not crash)

## Architecture Patterns

### Entity Descriptions as Data
When adding new sensors/binary sensors, define them as entries in a description tuple — do NOT create new entity subclasses. Use a `value_fn: Callable[[ToyotaCoordinatorData], Any]` lambda to extract data.

### Factory Functions for Repetitive Sets
If a group of sensors shares structure across multiple time periods or positions, write a factory function (e.g., `_make_summary_sensors(period, accessor)`) rather than duplicating descriptions.

### Multiple Inheritance
All entity classes use: `class ToyotaFoo(ToyotaBaseEntity, FooEntity)` — HA platform entity last.

### Coordinator Refresh After Commands
After any `post_command()` call, always trigger:
```python
await self.coordinator.async_request_refresh()
```

## File Structure

Every module follows this top-to-bottom order:
1. Module docstring
2. `from __future__ import annotations`
3. Imports (stdlib → HA → local)
4. Module-level constants (`PARALLEL_UPDATES`, custom units)
5. `_LOGGER` if needed
6. Helper functions (private, `_` prefix)
7. Dataclass definitions
8. Section dividers + entity description tuples
9. Entity class definitions
10. `async_setup_entry()` — always last

## Async

- All I/O (API calls, command sends, setup) must be `async`/`await`
- Never use blocking calls (`time.sleep`, synchronous HTTP)
- Use `await self.coordinator.async_request_refresh()` — not `coordinator.async_update()`

## Principles (Non-Negotiable)

- **No speculative abstractions.** Don't create helpers, base classes, or utilities unless they are used in at least two places right now.
- **No scope creep.** Don't add extra sensors, options, or features beyond what was asked.
- **Preserve HA conventions.** Follow Home Assistant integration patterns (`_attr_*` properties, entity descriptions, coordinator pattern).
- **Match existing patterns exactly** when adding new entities. New sensors go into the appropriate description tuple; new platforms follow the same file structure as existing ones.
- **No test infrastructure** unless explicitly requested.
