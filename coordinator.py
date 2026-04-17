"""DataUpdateCoordinator for the Toyota Custom integration."""
from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import TypeVar

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pytoyoda.exceptions import ToyotaApiError, ToyotaLoginError
from pytoyoda.models.service_history import ServiceHistory
from pytoyoda.models.summary import Summary
from pytoyoda.models.trips import Trip
from pytoyoda.models.vehicle import Vehicle

from .const import DOMAIN, UPDATE_INTERVAL_MINUTES

_T = TypeVar("_T")

_LOGGER = logging.getLogger(__name__)


@dataclass
class ToyotaCoordinatorData:
    """All data fetched for a single vehicle."""

    vehicle: Vehicle
    day_summary: Summary | None = field(default=None)
    week_summary: Summary | None = field(default=None)
    month_summary: Summary | None = field(default=None)
    year_summary: Summary | None = field(default=None)
    last_trip: Trip | None = field(default=None)
    service_history: ServiceHistory | None = field(default=None)


class ToyotaDataUpdateCoordinator(DataUpdateCoordinator[ToyotaCoordinatorData]):
    """Coordinator that polls a single Toyota vehicle every UPDATE_INTERVAL_MINUTES."""

    def __init__(self, hass: HomeAssistant, vehicle: Vehicle) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{vehicle.vin}",
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
        )
        self._vehicle = vehicle
        # Toyota's climate GET endpoints currently return ONE_GLOBAL_RS_40000 (HTTP 500),
        # which causes asyncio.gather() inside vehicle.update() to raise ToyotaApiError
        # and breaks the entire coordinator. Strip them from the poll list once at init.
        self._vehicle._endpoint_collect = [  # noqa: SLF001
            (name, fn)
            for name, fn in self._vehicle._endpoint_collect  # noqa: SLF001
            if name not in {"climate_settings", "climate_status"}
        ]

    async def _async_update_data(self) -> ToyotaCoordinatorData:
        """Fetch all data from the Toyota API."""
        try:
            await self._vehicle.update()
        except ToyotaLoginError as err:
            raise ConfigEntryAuthFailed("Authentication failed — re-enter credentials.") from err
        except ToyotaApiError as err:
            if not self.data:
                raise UpdateFailed(f"Toyota API error: {err}") from err
            _LOGGER.warning("Toyota API error during vehicle update (using cached data): %s", err)
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Toyota API error: {err}") from err

        day_summary = await self._safe_fetch(self._vehicle.get_current_day_summary, "day summary")
        week_summary = await self._safe_fetch(self._vehicle.get_current_week_summary, "week summary")
        month_summary = await self._safe_fetch(self._vehicle.get_current_month_summary, "month summary")
        year_summary = await self._safe_fetch(self._vehicle.get_current_year_summary, "year summary")
        last_trip = await self._safe_fetch(self._vehicle.get_last_trip, "last trip")
        # get_latest_service_history is sync in pytoyoda 4.x
        try:
            service_history = self._vehicle.get_latest_service_history()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not fetch service history: %s", err)
            service_history = None

        return ToyotaCoordinatorData(
            vehicle=self._vehicle,
            day_summary=day_summary,
            week_summary=week_summary,
            month_summary=month_summary,
            year_summary=year_summary,
            last_trip=last_trip,
            service_history=service_history,
        )

    async def _safe_fetch(self, coro_fn: Callable[[], Awaitable[_T]], label: str) -> _T | None:
        """Call an async method and return None on any exception."""
        try:
            return await coro_fn()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Could not fetch %s: %s", label, err)
            return None
