"""Inspect all Toyota API responses and parsed sensor values."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# Vendor path
sys.path.insert(0, str(Path(__file__).parent.parent / "_vendor"))

email = os.environ.get("TOYOTA_EMAIL")
password = os.environ.get("TOYOTA_PASSWORD")
if not email or not password:
    print("ERROR: TOYOTA_EMAIL and TOYOTA_PASSWORD must be set in .env", file=sys.stderr)
    sys.exit(1)


def _fmt(v) -> str:
    if v is None:
        return "None"
    return str(v)


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def _row(label: str, value) -> None:
    print(f"  {label:<35} {_fmt(value)}")


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

    # Strip climate endpoints (known HTTP 500)
    vehicle._endpoint_collect = [  # noqa: SLF001
        (name, fn) for name, fn in vehicle._endpoint_collect  # noqa: SLF001
        if name not in {"climate_settings", "climate_status"}
    ]

    print(f"Vehicle: {vehicle.vin}")
    print(f"Polling: {[n for n, _ in vehicle._endpoint_collect]}")  # noqa: SLF001
    print("Updating...")
    await vehicle.update()

    # -----------------------------------------------------------------------
    # Dashboard
    # -----------------------------------------------------------------------
    _section("DASHBOARD")
    d = vehicle.dashboard
    if d:
        _row("odometer", d.odometer)
        _row("fuel_level (%)", d.fuel_level)
        _row("fuel_range (km)", d.fuel_range)
        _row("battery_level (%)", d.battery_level)
        _row("battery_range (km)", d.battery_range)
        _row("battery_range_with_ac (km)", d.battery_range_with_ac)
        _row("total range (km)", d.range)
    else:
        print("  dashboard: None")

    # -----------------------------------------------------------------------
    # Summaries
    # -----------------------------------------------------------------------
    for label, coro in [
        ("DAY SUMMARY", vehicle.get_current_day_summary),
        ("WEEK SUMMARY", vehicle.get_current_week_summary),
        ("MONTH SUMMARY", vehicle.get_current_month_summary),
        ("YEAR SUMMARY", vehicle.get_current_year_summary),
    ]:
        _section(label)
        try:
            s = await coro()
            if s is None:
                print("  None")
                continue
            _row("from_date", s.from_date)
            _row("to_date", s.to_date)
            _row("distance (km)", s.distance)
            _row("duration", s.duration)
            _row("average_speed (km/h)", s.average_speed)
            _row("fuel_consumed (L)", s.fuel_consumed)
            _row("average_fuel_consumed (L/100km)", s.average_fuel_consumed)
            _row("ev_distance (km)", s.ev_distance)
            _row("ev_duration", s.ev_duration)
            _row("countries", s.countries)
        except Exception as e:
            print(f"  ERROR: {e}")

    # -----------------------------------------------------------------------
    # Last trip
    # -----------------------------------------------------------------------
    _section("LAST TRIP")
    try:
        t = await vehicle.get_last_trip()
        if t is None:
            print("  None")
        else:
            _row("start_time", t.start_time)
            _row("end_time", t.end_time)
            _row("duration", t.duration)
            _row("distance (km)", t.distance)
            _row("fuel_consumed (L)", t.fuel_consumed)
            _row("average_fuel_consumed (L/100km)", t.average_fuel_consumed)
            _row("ev_distance (km)", t.ev_distance)
            _row("ev_duration", t.ev_duration)
            _row("score", t.score)
            _row("score_acceleration", t.score_acceleration)
            _row("score_braking", t.score_braking)
            _row("score_advice", t.score_advice)
            _row("score_constant_speed", t.score_constant_speed)
    except Exception as e:
        print(f"  ERROR: {e}")

    # -----------------------------------------------------------------------
    # Service history
    # -----------------------------------------------------------------------
    _section("SERVICE HISTORY")
    try:
        sh = vehicle.get_latest_service_history()
        if sh is None:
            print("  None")
        else:
            _row("service_date", sh.service_date)
            _row("odometer (km)", sh.odometer)
            _row("service_category", sh.service_category)
            _row("service_provider", sh.service_provider)
            _row("notes", sh.notes)
    except Exception as e:
        print(f"  ERROR: {e}")

    # -----------------------------------------------------------------------
    # Raw endpoint data (JSON dump per endpoint)
    # -----------------------------------------------------------------------
    _section("RAW ENDPOINT DATA")
    endpoint_data = vehicle._endpoint_data  # noqa: SLF001
    print(f"  Endpoints populated: {list(endpoint_data.keys())}\n")

    for name, data in endpoint_data.items():
        print(f"\n--- {name} ---")
        if data is None:
            print("  None")
            continue
        try:
            raw = data.model_dump() if hasattr(data, 'model_dump') else data.dict()
            print(json.dumps(raw, indent=2, default=str))
        except Exception as e:  # noqa: BLE001
            print(f"  repr: {repr(data)[:500]}")
            print(f"  error: {e}")

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


if __name__ == "__main__":
    asyncio.run(main())
