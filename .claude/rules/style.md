# Coding Style

Strict rules derived from the existing codebase. Follow exactly when writing new code.

## File Structure

Every file must begin with, in order:
1. Module docstring: `"""<One sentence describing the module>."""`
2. `from __future__ import annotations`
3. stdlib imports, then third-party, then HA (`homeassistant.*`), then local (`. import ...`)
4. `_LOGGER = logging.getLogger(__name__)` — only when the file actually logs

## Type Annotations

- Use Python 3.12 `type` alias syntax: `type ToyotaConfigEntry = ConfigEntry[list[ToyotaDataUpdateCoordinator]]`
- Always annotate function signatures fully, including return types
- Use `T | None` not `Optional[T]`
- Use `list[X]` not `List[X]`

## Description Dataclasses

```python
@dataclass(frozen=True, kw_only=True)
class ToyotaXxxEntityDescription(XxxEntityDescription):
    """Extends XxxEntityDescription with a value_fn."""

    value_fn: Callable[[ToyotaCoordinatorData], SomeType] = lambda _: None
```

- Always `frozen=True, kw_only=True`
- `value_fn` default is `lambda _: None`, never `None`
- Description tuples are module-level constants, typed as `tuple[ToyotaXxxEntityDescription, ...]`

## value_fn Lambdas

Safe None-chain pattern — always guard each level:

```python
value_fn=lambda d: d.vehicle.dashboard.odometer if d.vehicle.dashboard else None,
```

For deeply nested access (lock_status), guard each intermediate:

```python
value_fn=lambda d: (
    _closed_to_is_on(d.vehicle.lock_status.doors.driver_seat.closed)
    if d.vehicle.lock_status and d.vehicle.lock_status.doors and d.vehicle.lock_status.doors.driver_seat
    else None
),
```

Never raise inside a `value_fn` lambda — the entity's `native_value`/`is_on` has a safety net but lambdas should be clean.

## Entity Classes

```python
class ToyotaXxxEntity(ToyotaBaseEntity, XxxEntity):
    """A single Toyota xxx."""

    entity_description: ToyotaXxxEntityDescription

    def __init__(self, coordinator: ToyotaDataUpdateCoordinator, description: ToyotaXxxEntityDescription) -> None:
        """Initialise the xxx."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._vin}_{description.key}"
```

- `unique_id` always `f"{self._vin}_{description.key}"` (description-based) or `f"{self._vin}_<fixed_suffix>"` (single entities)
- Use `_attr_translation_key` for entity names — not hardcoded strings (exception: one-off utility entities may use `_attr_name`)
- Use `_attr_*` class attributes for static HA properties; only use instance attributes for dynamic state

## State Properties (safety net)

```python
@property
def native_value(self) -> Any:
    """Return the sensor value, safely handling None chains."""
    try:
        return self.entity_description.value_fn(self.coordinator.data)
    except (AttributeError, TypeError):
        return None
```

Always wrap `value_fn` calls in `try/except (AttributeError, TypeError)` — never let a bad API response crash an entity update.

## Error Handling

```python
# Hard failure — raise to HA
except ToyotaLoginError as err:
    raise ConfigEntryAuthFailed("...") from err

# Soft failure — log and degrade gracefully
except Exception as err:  # noqa: BLE001
    _LOGGER.warning("Toyota command %s failed: %s", command, err)

# Optional data — return None silently
except Exception as err:  # noqa: BLE001
    _LOGGER.debug("Could not fetch %s: %s", label, err)
    return None
```

- `# noqa: BLE001` is required on every bare `except Exception` — never omit it
- Re-raise as HA exceptions (`ConfigEntryAuthFailed`, `ConfigEntryNotReady`, `UpdateFailed`) with `from err`
- Never swallow exceptions silently without at least a debug log

## Logging

- Use `%s` style formatting, never f-strings in log calls: `_LOGGER.warning("msg %s", var)`
- DEBUG for optional data failures and diagnostic info
- WARNING for recoverable errors that degrade functionality
- No INFO logs — HA integrations avoid chattiness

## Platform Module Constants

Every platform file must have at module level, before any class definitions:

```python
PARALLEL_UPDATES = 0
```

## Deferred Imports

`pytoyoda` is always imported inside the function, not at module level:

```python
from pytoyoda import MyT  # noqa: PLC0415
from pytoyoda.exceptions import ToyotaLoginError  # noqa: PLC0415
```

`# noqa: PLC0415` is required — never suppress it or move these to module level.

## Section Banners

Use `# ---` banners to group related blocks in long files:

```python
# ---------------------------------------------------------------------------
# Dashboard sensors
# ---------------------------------------------------------------------------
```

## Comments

- Comment the **why**, not the what
- Cite API error codes when working around known bugs: `# Toyota's climate GET endpoints return ONE_GLOBAL_RS_40000 (HTTP 500)`
- Comment semantic gotchas: `# is_on=True means OPEN (alert state), not closed`
- No redundant inline comments restating the code

## async_setup_entry Signature

Always exactly:

```python
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ToyotaConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Toyota <platform> from a config entry."""
    coordinators: list[ToyotaDataUpdateCoordinator] = entry.runtime_data
    ...
```
