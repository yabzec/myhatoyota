# mytoyota — CLAUDE.md

Home Assistant custom integration for Toyota Connected Services.
Connects HA to Toyota's cloud API via the `pytoyoda` library.

## Tech Stack

- **Language:** Python 3.12+
- **Framework:** Home Assistant custom integration
- **External API:** `pytoyoda>=4.0.0` (Toyota Connected Services)
- **Domain:** `toyota_custom`
- **Integration type:** hub / cloud_polling

## Directory Structure

```
mytoyota/
├── __init__.py          # Entry point: setup/unload config entry
├── const.py             # All constants (domain, platforms, intervals)
├── manifest.json        # HA integration metadata + requirements
├── coordinator.py       # DataUpdateCoordinator per vehicle (polling)
├── base_entity.py       # ToyotaBaseEntity shared by all platforms
├── config_flow.py       # User credential config UI
├── sensor.py            # 51 sensor entities (dashboard, trips, service)
├── binary_sensor.py     # 9 binary sensors (doors, windows, hood)
├── lock.py              # 2 lock entities (doors, trunk)
├── climate.py           # 1 climate entity (remote AC/heat)
├── device_tracker.py    # 1 GPS tracker entity
├── strings.json         # Config flow UI strings
└── translations/en.json # English translations
```

## Rule Files

@.claude/rules/architecture.md
@.claude/rules/commands.md
@.claude/rules/style.md
