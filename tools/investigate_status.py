"""Dump raw Toyota API status response to understand door/lock field names."""
from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

email = os.environ.get("TOYOTA_EMAIL")
password = os.environ.get("TOYOTA_PASSWORD")

if not email or not password:
    print("ERROR: TOYOTA_EMAIL and TOYOTA_PASSWORD must be set in .env", file=sys.stderr)
    sys.exit(1)


async def main() -> None:
    from pytoyoda import MyT  # noqa: PLC0415

    client = MyT(username=email, password=password, use_metric=True, brand="T")
    print("Logging in...")
    await client.login()

    print("Fetching vehicles...")
    vehicles = await client.get_vehicles()
    if not vehicles:
        print("No vehicles found.")
        return

    vehicle = vehicles[0]
    print(f"Vehicle: {vehicle.vin}")

    # Strip climate endpoints to avoid known HTTP 500 errors
    vehicle._endpoint_collect = [  # noqa: SLF001
        (name, fn)
        for name, fn in vehicle._endpoint_collect  # noqa: SLF001
        if name not in {"climate_settings", "climate_status"}
    ]
    print(f"Polling endpoints: {[n for n, _ in vehicle._endpoint_collect]}")  # noqa: SLF001

    print("Calling vehicle.update()...")
    await vehicle.update()

    endpoint_data = vehicle._endpoint_data  # noqa: SLF001
    print(f"\nEndpoints populated: {list(endpoint_data.keys())}\n")

    # --- Status endpoint (door/lock data) ---
    status = endpoint_data.get("status")
    print("=" * 60)
    print("RAW STATUS ENDPOINT RESPONSE:")
    print("=" * 60)
    if status is None:
        print("  status endpoint not in _endpoint_data")
    else:
        try:
            print(json.dumps(status.dict(), indent=2, default=str))
        except Exception:
            print(repr(status))

    # --- Trip history (summary data) ---
    trip_history = endpoint_data.get("trip_history")
    print("\n" + "=" * 60)
    print("RAW TRIP_HISTORY SUMMARY SAMPLE (first entry):")
    print("=" * 60)
    if trip_history is None:
        print("  trip_history not in _endpoint_data")
    else:
        try:
            payload = trip_history.payload
            if payload and payload.summary:
                first = payload.summary[0]
                print(json.dumps(first.dict() if hasattr(first, "dict") else vars(first), indent=2, default=str))
                print(f"\nTotal summary entries: {len(payload.summary)}")
                print(f"Histograms in first entry: {len(first.histograms) if hasattr(first, 'histograms') else 'N/A'}")
                if hasattr(first, "histograms") and first.histograms:
                    h = first.histograms[0]
                    print(f"\nFirst histogram sample:")
                    print(json.dumps(h.dict() if hasattr(h, "dict") else vars(h), indent=2, default=str))
            else:
                print("  No summary data in payload")
        except Exception as e:
            print(f"  Error: {e}")
            print(repr(trip_history))


if __name__ == "__main__":
    asyncio.run(main())
