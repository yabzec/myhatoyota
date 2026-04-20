# Design: Fix Unknown/None Sensor Values + inspect_api.py Truncation

**Date:** 2026-04-17  
**Branch:** fixes  
**Status:** approved

---

## Problem

Two related issues:

1. `tools/inspect_api.py` truncates raw JSON output at 3 000 characters, hiding the full API response.
2. Several HA sensors (`distance`, `fuel_consumed`, `average_speed`, `ev_distance`, `ev_duration`) show "unknown" for all summary periods and Last Trip, despite `inspect_api.py` showing parsed values for these fields.

The user confirmed: `inspect_api.py` returns actual numbers in its parsed output sections; HA shows unknown for the same fields. This localises the bug to the HA integration layer, not pytoyoda's parsing.

Additionally, a `duration` sensor is entirely absent from both summary and last-trip sensor groups — the `Summary.duration` and `Trip.duration` fields exist in pytoyoda but are never exposed to HA.

---

## Root Cause Hypotheses

In priority order (to be confirmed by the diagnostic script in Phase 2):

1. **`_safe_fetch` swallowing a silent exception** — any exception thrown inside `get_current_*_summary()` or `get_last_trip()` is caught and logged only at DEBUG level. In HA's default log level this is invisible, and the return value is `None` → sensors show unknown.
2. **`get_summary()` `len(None)` TypeError** — `vehicle.py:516` does `len(resp.payload.summary)` which raises `TypeError` if `payload.summary` is `None`; caught by `_safe_fetch`.
3. **Session/credential state difference** — `inspect_api.py` runs with a fresh login; the coordinator reuses a long-lived `MyT` session that may have drifted.

---

## Design

### Phase 1 — Fix `tools/inspect_api.py`

**File:** `tools/inspect_api.py`

Two changes:

1. **Remove truncation cap** — delete `[:3000]` at the end of the `json.dumps(...)` call (line 170). Output becomes unlimited.

2. **Add raw fresh-call dump section** — after the existing `RAW ENDPOINT DATA` block, add a new section `RAW FRESH CALLS` that directly invokes `vehicle._api.get_trips()` with the same parameters used by `get_last_trip()` and `get_summary()`, and dumps the full `TripsResponseModel.model_dump()`. This distinguishes pre-fetched endpoint data from fresh-call responses and exposes any discrepancy between `summary=True` (pre-fetch) and `summary=False` (last-trip) API payloads.

---

### Phase 2 — New `tools/test_coordinator_flow.py`

**File:** `tools/test_coordinator_flow.py` (new)

A standalone script that reproduces exactly what `ToyotaDataUpdateCoordinator._async_update_data()` does, with one difference: `safe_fetch` prints the exception instead of swallowing it.

Structure:

```
login → vehicle.update()
→ safe_fetch each of: get_current_day/week/month/year_summary, get_last_trip
→ for each result, print every sensor-mapped field:
    distance, duration, fuel_consumed, average_fuel_consumed,
    average_speed, ev_distance, ev_duration
    (plus scores for last_trip)
```

`safe_fetch` in this script:
- On success: prints `OK → <type>` and returns the result
- On exception: prints `FAILED → <ExceptionType>: <message>` and returns None

No HA imports. Reads `.env` for credentials, injects `_vendor/` into `sys.path` identically to `inspect_api.py`.

This script will immediately show whether `_safe_fetch` is hiding a real error, and what value each sensor field would have.

---

### Phase 3 — `coordinator.py`: raise `_safe_fetch` log level

**File:** `coordinator.py`

Change `_LOGGER.debug("Could not fetch %s: %s", label, err)` → `_LOGGER.warning(...)`.

Rationale: optional-data failures are not noise — they explain "unknown" sensors. WARNING is the right level for degraded functionality.

---

### Phase 4 — Add missing `duration` sensors

**Files:** `sensor.py`, `strings.json`, `translations/en.json`, `translations/it.json`

Add a `duration` entry (in minutes, `UnitOfTime.MINUTES`, `SensorDeviceClass.DURATION`) to `_make_summary_sensors`, giving all four summary groups (`day_`, `week_`, `month_`, `year_`) a `*_duration` sensor.

Add a `last_trip_duration` entry (same unit/class) to `_LAST_TRIP_SENSORS`, using `_timedelta_to_minutes(d.last_trip.duration)`.

Add corresponding `translation_key` entries in `strings.json` and mirror to both translation files. Italian translation may use a placeholder if unknown; English must be present.

---

## What is NOT in scope

- Adding `route` or `locations` sensors.
- Changing the coordinator's polling interval.
- Fixing `ev_time == 0` returning `None` (separate issue; current behaviour is intentional per architecture notes).
- Any pytoyoda vendored code changes — pytoyoda parses correctly.

---

## Verification

After implementation:

1. Run `python3 tools/inspect_api.py 2>/dev/null` — verify no truncation, full JSON visible.
2. Run `python3 tools/test_coordinator_flow.py 2>/dev/null` — verify all summary/trip fields print actual values (not "FAILED").
3. Deploy to HA (`git push` + `git pull` on HA machine + restart).
4. Check HA dashboard — `distance`, `fuel_consumed`, `average_speed`, `ev_distance`, `ev_duration`, and new `duration` sensors should show values, not "unknown".
5. Check `home-assistant.log` — any remaining failures now appear at WARNING level.
