"""DataUpdateCoordinator for the Toyota Custom integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)


@dataclass
class ToyotaCoordinatorData:
    """All data fetched for a single vehicle."""

    vehicle: Any
    day_summary: Any | None = field(default=None)
    week_summary: Any | None = field(default=None)
    month_summary: Any | None = field(default=None)
    year_summary: Any | None = field(default=None)
    last_trip: Any | None = field(default=None)
    service_history: Any | None = field(default=None)


class ToyotaDataUpdateCoordinator(DataUpdateCoordinator[ToyotaCoordinatorData]):
    """Coordinator that polls a single Toyota vehicle every UPDATE_INTERVAL_MINUTES."""

    def __init__(self, hass: HomeAssistant, vehicle: Any) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{vehicle.vin}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._vehicle = vehicle

    async def _async_update_data(self) -> ToyotaCoordinatorData:
        """Fetch all data from the Toyota API."""
        try:
            await self._vehicle.update()
        except Exception as err:
            # Re-import here to avoid circular imports at module level
            try:
                from pytoyoda.exceptions import ToyotaLoginError, ToyotaApiError  # noqa: PLC0415
            except ImportError:
                raise UpdateFailed(f"Failed to update vehicle data: {err}") from err

            if isinstance(err, ToyotaLoginError):
                raise ConfigEntryAuthFailed("Authentication failed — re-enter credentials.") from err
            raise UpdateFailed(f"Toyota API error: {err}") from err

        day_summary = await self._safe_fetch(self._vehicle.get_current_day_summary, "day summary")
        week_summary = await self._safe_fetch(self._vehicle.get_current_week_summary, "week summary")
        month_summary = await self._safe_fetch(self._vehicle.get_current_month_summary, "month summary")
        year_summary = await self._safe_fetch(self._vehicle.get_current_year_summary, "year summary")
        last_trip = await self._safe_fetch(self._vehicle.get_last_trip, "last trip")
        service_history = await self._safe_fetch(self._vehicle.get_latest_service_history, "service history")

        return ToyotaCoordinatorData(
            vehicle=self._vehicle,
            day_summary=day_summary,
            week_summary=week_summary,
            month_summary=month_summary,
            year_summary=year_summary,
            last_trip=last_trip,
            service_history=service_history,
        )

    async def _safe_fetch(self, coro_fn: Any, label: str) -> Any | None:
        """Call an async method and return None on any exception."""
        try:
            return await coro_fn()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not fetch %s: %s", label, err)
            return None
