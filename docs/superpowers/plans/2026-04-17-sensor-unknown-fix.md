# Sensor Unknown Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix "unknown" sensor values for distance/duration/fuel/speed in all summary periods and Last Trip, expose silent coordinator failures, add missing duration sensors, and remove inspect_api.py truncation.

**Architecture:** No test framework exists — verification is done by running the diagnostic scripts in `tools/` and observing HA logs after deploy. Four independent changes: (1) fix inspect_api.py output, (2) new diagnostic script mirroring coordinator logic, (3) one-line log-level fix in coordinator, (4) new duration sensors + translations.

**Tech Stack:** Python 3.12, pytoyoda 4.2.0 (vendored in `_vendor/`), Home Assistant custom integration. No pytest. Credentials in `.env` (`TOYOTA_EMAIL`, `TOYOTA_PASSWORD`).

---

## File Map

| File | Change |
|------|--------|
| `tools/inspect_api.py` | Remove `[:3000]` cap; add `RAW FRESH CALLS` section |
| `tools/test_coordinator_flow.py` | **Create** — mirrors coordinator `_async_update_data` exactly |
| `coordinator.py` | `_safe_fetch`: `debug` → `warning` |
| `sensor.py` | Add `{prefix}_duration` in `_make_summary_sensors`; add `last_trip_duration` in `_LAST_TRIP_SENSORS` |
| `strings.json` | Add `entity.sensor` block with 5 new duration keys |
| `translations/en.json` | Add 5 new duration sensor entries |
| `translations/it.json` | Add 5 new duration sensor entries (Italian) |

---

## Task 1: Fix `tools/inspect_api.py` — remove truncation and add fresh-call dump

**Files:**
- Modify: `tools/inspect_api.py:170` (remove cap)
- Modify: `tools/inspect_api.py:174` (add new section after RAW ENDPOINT DATA block)

- [ ] **Step 1: Remove the 3000-char truncation cap**

In `tools/inspect_api.py`, line 170, change:

```python
            print(json.dumps(raw, indent=2, default=str)[:3000])  # cap at 3000 chars
```

to:

```python
            print(json.dumps(raw, indent=2, default=str))
```

- [ ] **Step 2: Add RAW FRESH CALLS section after the existing raw endpoint loop**

After line 173 (the final `print(f"  error: {e}")` line inside the endpoint loop), add this block at the end of `main()`, before the closing of the function:

```python
    # -----------------------------------------------------------------------
    # Raw fresh API calls (not in _endpoint_data — separate requests)
    # -----------------------------------------------------------------------
    _section("RAW FRESH CALLS")
    from datetime import date, timedelta  # noqa: PLC0415

    for label, kwargs in [
        (
            "get_last_trip params (summary=False, limit=1)",
            {"summary": False, "limit": 1, "offset": 0, "route": False},
        ),
        (
            "get_summary params (summary=True, limit=1)",
            {"summary": True, "limit": 1, "offset": 0},
        ),
    ]:
        print(f"\n--- {label} ---")
        try:
            resp = await vehicle._api.get_trips(  # noqa: SLF001
                vehicle.vin,
                date.today() - timedelta(days=90),  # noqa: DTZ011
                date.today(),  # noqa: DTZ011
                **kwargs,
            )
            raw = resp.model_dump() if hasattr(resp, "model_dump") else resp.dict()
            print(json.dumps(raw, indent=2, default=str))
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR: {e}")
```

- [ ] **Step 3: Verify the script runs without truncation**

```bash
cd /home/mcolpo/Developer/Private/mytoyota
source .venv/bin/activate
python3 tools/inspect_api.py 2>/dev/null | grep -c "}"
```

Expected: a number much larger than what you'd get from 3 000 chars of JSON. Also verify the `RAW FRESH CALLS` section appears at the end of the output.

- [ ] **Step 4: Commit**

```bash
git add tools/inspect_api.py
git commit -m "fix(tools): remove 3000-char JSON truncation in inspect_api, add fresh-call dump"
```

---

## Task 2: Create `tools/test_coordinator_flow.py`

**Files:**
- Create: `tools/test_coordinator_flow.py`

This script mirrors exactly what `ToyotaDataUpdateCoordinator._async_update_data()` does. The key difference: `safe_fetch` prints the exception message instead of logging it at DEBUG and returning None silently.

- [ ] **Step 1: Create the file**

```python
"""Simulate coordinator data fetch to expose silent failures."""
from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar

# Load .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(Path(__file__).parent.parent / "_vendor"))

email = os.environ.get("TOYOTA_EMAIL")
password = os.environ.get("TOYOTA_PASSWORD")
if not email or not password:
    print("ERROR: TOYOTA_EMAIL and TOYOTA_PASSWORD must be set in .env", file=sys.stderr)
    sys.exit(1)

_T = TypeVar("_T")


async def safe_fetch(coro_fn: Callable[[], Awaitable[_T]], label: str) -> _T | None:
    """Mirror _safe_fetch but print exceptions instead of swallowing them."""
    try:
        result = await coro_fn()
        print(f"  {label}: OK -> {type(result).__name__}")
        return result
    except Exception as err:  # noqa: BLE001
        print(f"  {label}: FAILED -> {type(err).__name__}: {err}")
        return None


def _row(label: str, value: object) -> None:
    print(f"    {label:<38} {value!r}")


async def main() -> None:
    from pytoyoda import MyT  # noqa: PLC0415

    client = MyT(username=email, password=password, use_metric=True, brand="T")
    print("Logging in...")
    await client.login()

    vehicles = await client.get_vehicles()
    if not vehicles:
        print("No vehicles found.")
        return

    vehicle = vehicles[0]
    # Mirror coordinator.__init__: strip broken climate endpoints
    vehicle._endpoint_collect = [  # noqa: SLF001
        (name, fn)
        for name, fn in vehicle._endpoint_collect  # noqa: SLF001
        if name not in {"climate_settings", "climate_status"}
    ]

    print(f"Vehicle: {vehicle.vin}")
    print("Updating (vehicle.update())...")
    await vehicle.update()

    print("\n=== COORDINATOR FETCH (mirrors _async_update_data) ===")
    day_summary = await safe_fetch(vehicle.get_current_day_summary, "day_summary")
    week_summary = await safe_fetch(vehicle.get_current_week_summary, "week_summary")
    month_summary = await safe_fetch(vehicle.get_current_month_summary, "month_summary")
    year_summary = await safe_fetch(vehicle.get_current_year_summary, "year_summary")
    last_trip = await safe_fetch(vehicle.get_last_trip, "last_trip")

    print("\n=== SENSOR VALUES (what HA would receive) ===")

    for period, summary in [
        ("day", day_summary),
        ("week", week_summary),
        ("month", month_summary),
        ("year", year_summary),
    ]:
        print(f"\n  {period}_summary ({type(summary).__name__ if summary else 'None'}):")
        if summary is None:
            print("    (None — either fetch failed or API returned no data)")
            continue
        _row(f"{period}_distance", summary.distance)
        _row(f"{period}_duration", summary.duration)
        _row(f"{period}_fuel_consumed", summary.fuel_consumed)
        _row(f"{period}_average_fuel_consumed", summary.average_fuel_consumed)
        _row(f"{period}_average_speed", summary.average_speed)
        _row(f"{period}_ev_distance", summary.ev_distance)
        _row(f"{period}_ev_duration", summary.ev_duration)

    print(f"\n  last_trip ({type(last_trip).__name__ if last_trip else 'None'}):")
    if last_trip is None:
        print("    (None — either fetch failed or API returned no data)")
    else:
        _row("distance", last_trip.distance)
        _row("duration", last_trip.duration)
        _row("fuel_consumed", last_trip.fuel_consumed)
        _row("average_fuel_consumed", last_trip.average_fuel_consumed)
        _row("ev_distance", last_trip.ev_distance)
        _row("ev_duration", last_trip.ev_duration)
        _row("score", last_trip.score)
        _row("score_acceleration", last_trip.score_acceleration)
        _row("score_braking", last_trip.score_braking)
        _row("score_advice", last_trip.score_advice)
        _row("score_constant_speed", last_trip.score_constant_speed)


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Run the script and read the output carefully**

```bash
cd /home/mcolpo/Developer/Private/mytoyota
source .venv/bin/activate
python3 tools/test_coordinator_flow.py 2>/dev/null
```

Expected outcomes:

- If all fetches show `OK -> Summary` / `OK -> Trip` **and** sensor values show actual numbers: the bug is a HA session/credential issue — the coordinator's API calls are failing silently in HA. Check HA logs after deploying Task 3.
- If any fetch shows `FAILED -> <ExceptionType>: <message>`: that exception is being silently swallowed by `_safe_fetch` in the real coordinator. The exception message tells you exactly what to fix.
- If fetches show `OK` but sensor values are `None`: pytoyoda parses but fields are None (API sends null for this vehicle for those fields — expected per architecture notes for Yaris Cross hybrid).

- [ ] **Step 3: Commit**

```bash
git add tools/test_coordinator_flow.py
git commit -m "feat(tools): add test_coordinator_flow script to expose silent coordinator failures"
```

---

## Task 3: Fix `coordinator.py` — raise `_safe_fetch` log level

**Files:**
- Modify: `coordinator.py:106`

- [ ] **Step 1: Change log level in `_safe_fetch`**

In `coordinator.py`, the `_safe_fetch` method (lines 100–106), change:

```python
    async def _safe_fetch(self, coro_fn: Callable[[], Awaitable[_T]], label: str) -> _T | None:
        """Call an async method and return None on any exception."""
        try:
            return await coro_fn()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not fetch %s: %s", label, err)
            return None
```

to:

```python
    async def _safe_fetch(self, coro_fn: Callable[[], Awaitable[_T]], label: str) -> _T | None:
        """Call an async method and return None on any exception."""
        try:
            return await coro_fn()
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Could not fetch %s: %s", label, err)
            return None
```

- [ ] **Step 2: Verify the change is correct**

```bash
grep -n "Could not fetch" coordinator.py
```

Expected output:
```
106:            _LOGGER.warning("Could not fetch %s: %s", label, err)
```

- [ ] **Step 3: Commit**

```bash
git add coordinator.py
git commit -m "fix(coordinator): raise _safe_fetch log level debug->warning so failures are visible in HA"
```

---

## Task 4: Add missing `duration` sensors + update translations

**Files:**
- Modify: `sensor.py:122–178` (`_make_summary_sensors`) and `sensor.py:191` (`_LAST_TRIP_SENSORS`)
- Modify: `strings.json`
- Modify: `translations/en.json`
- Modify: `translations/it.json`

### 4a — sensor.py

- [ ] **Step 1: Add `{prefix}_duration` to `_make_summary_sensors`**

In `sensor.py`, inside `_make_summary_sensors`, add a new entry **after** the `distance` entry and **before** the `fuel_consumed` entry. The function currently starts with:

```python
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
```

Change it to:

```python
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
            key=f"{prefix}_duration",
            translation_key=f"{prefix}_duration",
            native_unit_of_measurement=UnitOfTime.MINUTES,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            icon="mdi:timer",
            value_fn=lambda d, a=attr: _timedelta_to_minutes(getattr(d, a).duration) if getattr(d, a) else None,
        ),
        ToyotaSensorEntityDescription(
            key=f"{prefix}_fuel_consumed",
```

- [ ] **Step 2: Add `last_trip_duration` to `_LAST_TRIP_SENSORS`**

In `sensor.py`, inside `_LAST_TRIP_SENSORS`, add after the `last_trip_distance` entry and before `last_trip_fuel_consumed`. The block currently reads:

```python
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
```

Change it to:

```python
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
        key="last_trip_duration",
        translation_key="last_trip_duration",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:timer",
        value_fn=lambda d: _timedelta_to_minutes(d.last_trip.duration) if d.last_trip else None,
    ),
    ToyotaSensorEntityDescription(
        key="last_trip_fuel_consumed",
```

- [ ] **Step 3: Verify sensor.py parses cleanly**

```bash
cd /home/mcolpo/Developer/Private/mytoyota
source .venv/bin/activate
python3 -c "
import ast, sys
with open('sensor.py') as f:
    src = f.read()
ast.parse(src)
print('sensor.py: syntax OK')
"
```

Expected: `sensor.py: syntax OK`

### 4b — strings.json

- [ ] **Step 4: Add `entity.sensor` block to `strings.json`**

The current `strings.json` has only a `config` block. Add the `entity` section with the five new duration keys. Replace the entire file content with:

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Connect to Toyota",
        "description": "Enter your Toyota Connected Services credentials.",
        "data": {
          "email": "Email Address",
          "password": "Password"
        }
      }
    },
    "error": {
      "invalid_username": "Invalid email address format.",
      "invalid_auth": "Invalid credentials. Check your email and password.",
      "cannot_connect": "Failed to connect to Toyota services. Try again later."
    },
    "abort": {
      "already_configured": "This Toyota account is already configured."
    }
  },
  "entity": {
    "sensor": {
      "day_duration": { "name": "Today Duration" },
      "week_duration": { "name": "This Week Duration" },
      "month_duration": { "name": "This Month Duration" },
      "year_duration": { "name": "This Year Duration" },
      "last_trip_duration": { "name": "Last Trip Duration" }
    }
  }
}
```

### 4c — translations/en.json

- [ ] **Step 5: Add 5 duration entries to `translations/en.json`**

In `translations/en.json`, inside `"entity" > "sensor"`, add the following five entries. Insert them in logical positions — `day_duration` after `day_distance`, `week_duration` after `week_distance`, etc., and `last_trip_duration` after `last_trip_distance`.

After `"day_distance": { "name": "Today Distance" },` add:
```json
      "day_duration": {
        "name": "Today Duration"
      },
```

After `"week_distance": { "name": "This Week Distance" },` add:
```json
      "week_duration": {
        "name": "This Week Duration"
      },
```

After `"month_distance": { "name": "This Month Distance" },` add:
```json
      "month_duration": {
        "name": "This Month Duration"
      },
```

After `"year_distance": { "name": "This Year Distance" },` add:
```json
      "year_duration": {
        "name": "This Year Duration"
      },
```

After `"last_trip_distance": { "name": "Last Trip Distance" },` add:
```json
      "last_trip_duration": {
        "name": "Last Trip Duration"
      },
```

### 4d — translations/it.json

- [ ] **Step 6: Add 5 duration entries to `translations/it.json`**

Apply the same insertions as Step 5, with Italian text:

After `"day_distance": { "name": "Distanza Oggi" },` add:
```json
      "day_duration": {
        "name": "Durata Oggi"
      },
```

After `"week_distance": { "name": "Distanza Questa Settimana" },` add:
```json
      "week_duration": {
        "name": "Durata Questa Settimana"
      },
```

After `"month_distance": { "name": "Distanza Questo Mese" },` add:
```json
      "month_duration": {
        "name": "Durata Questo Mese"
      },
```

After `"year_distance": { "name": "Distanza Quest'Anno" },` add:
```json
      "year_duration": {
        "name": "Durata Quest'Anno"
      },
```

After `"last_trip_distance": { "name": "Distanza Ultimo Viaggio" },` add:
```json
      "last_trip_duration": {
        "name": "Durata Ultimo Viaggio"
      },
```

- [ ] **Step 7: Verify both JSON files parse cleanly**

```bash
python3 -c "import json; json.load(open('translations/en.json')); print('en.json: OK')"
python3 -c "import json; json.load(open('translations/it.json')); print('it.json: OK')"
python3 -c "import json; json.load(open('strings.json')); print('strings.json: OK')"
```

Expected:
```
en.json: OK
it.json: OK
strings.json: OK
```

- [ ] **Step 8: Commit all translation + sensor changes**

```bash
git add sensor.py strings.json translations/en.json translations/it.json
git commit -m "feat(sensor): add duration sensors for all summary periods and last trip"
```

---

## Task 5: Deploy and verify in Home Assistant

- [ ] **Step 1: Push to remote**

```bash
git push
```

- [ ] **Step 2: Pull on HA machine and restart**

On the HA machine, in the integration directory (`<ha_config>/custom_components/myhatoyota/`):

```bash
git pull
```

Then restart HA via the UI: **Settings → System → Restart**.

- [ ] **Step 3: Check HA logs**

In HA: **Settings → System → Logs**. Filter for `myhatoyota`. After the coordinator's first poll (up to 5 minutes), look for:

- No `WARNING: Could not fetch ...` entries → all fetches succeeded, sensors should show values.
- If `WARNING: Could not fetch day summary: ...` appears → the exception message will tell you exactly what to fix next.

- [ ] **Step 4: Verify sensors in HA dashboard**

Check that the following sensors now show values (not "unknown"):
- `sensor.*_day_distance`, `*_day_fuel_consumed`, `*_day_average_speed`
- Same for `week_`, `month_`, `year_` prefixes
- `sensor.*_last_trip_distance`, `*_last_trip_fuel_consumed`
- New sensors: `*_day_duration`, `*_week_duration`, `*_month_duration`, `*_year_duration`, `*_last_trip_duration`

If sensors still show "unknown" after a successful poll cycle and no WARNING logs appear: the API genuinely returns null for those fields for this vehicle (Yaris Cross hybrid limitation per architecture notes). The `test_coordinator_flow.py` output from Task 2 will have confirmed this.
