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

    # ---------------------------------------------------------------------------
    # Lock / door / window status
    # ---------------------------------------------------------------------------
    print("\n  lock_status:")
    ls = vehicle.lock_status
    if ls is None:
        print("    (None — endpoint not fetched or parse failed)")
    else:
        _row("last_updated", ls.last_updated)
        doors = ls.doors
        if doors is None:
            _row("doors", None)
        else:
            for attr in ("driver_seat", "passenger_seat", "driver_rear_seat", "passenger_rear_seat", "trunk"):
                door = getattr(doors, attr, None)
                _row(f"doors.{attr}.closed", door.closed if door else None)
                _row(f"doors.{attr}.locked", door.locked if door else None)
        hood = ls.hood
        _row("hood.closed", hood.closed if hood else None)
        windows = ls.windows
        if windows is None:
            _row("windows", None)
        else:
            for attr in ("driver_seat", "passenger_seat", "driver_rear_seat", "passenger_rear_seat"):
                win = getattr(windows, attr, None)
                _row(f"windows.{attr}.closed", win.closed if win else None)


if __name__ == "__main__":
    asyncio.run(main())
