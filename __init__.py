"""Toyota Custom integration setup."""
from __future__ import annotations

import sys
from pathlib import Path

# Prefer vendored pytoyoda (with local fixes) over any pip-installed version
sys.path.insert(0, str(Path(__file__).parent / "_vendor"))

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .const import CONF_EMAIL, CONF_PASSWORD, PLATFORMS
from .coordinator import ToyotaDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

type ToyotaConfigEntry = ConfigEntry[list[ToyotaDataUpdateCoordinator]]


async def async_setup_entry(hass: HomeAssistant, entry: ToyotaConfigEntry) -> bool:
    """Set up Toyota integration from a config entry."""
    try:
        from pytoyoda import MyT  # noqa: PLC0415
        from pytoyoda.exceptions import ToyotaLoginError  # noqa: PLC0415
    except ImportError as err:
        raise ConfigEntryNotReady("pytoyoda is not installed") from err

    # Suppress loguru noise from pytoyoda in HA logs
    try:
        from loguru import logger as loguru_logger  # noqa: PLC0415
        loguru_logger.disable("pytoyoda")
    except ImportError:
        pass

    client = MyT(
        username=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
        use_metric=True,
        brand="T",
    )

    try:
        await client.login()
        vehicles = await client.get_vehicles()
    except ToyotaLoginError as err:
        raise ConfigEntryAuthFailed("Toyota credentials are invalid") from err
    except Exception as err:
        raise ConfigEntryNotReady(f"Cannot connect to Toyota: {err}") from err

    if not vehicles:
        _LOGGER.warning("No vehicles found for Toyota account %s", entry.data[CONF_EMAIL])

    coordinators: list[ToyotaDataUpdateCoordinator] = []
    for vehicle in vehicles:
        coordinator = ToyotaDataUpdateCoordinator(hass, vehicle)
        await coordinator.async_config_entry_first_refresh()
        coordinators.append(coordinator)

    entry.runtime_data = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ToyotaConfigEntry) -> bool:
    """Unload a Toyota config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
