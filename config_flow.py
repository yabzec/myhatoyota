"""Config flow for Toyota Custom integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ToyotaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Toyota Custom."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                from pytoyoda import MyT  # noqa: PLC0415
                from pytoyoda.exceptions import (  # noqa: PLC0415
                    ToyotaLoginError,
                    ToyotaInvalidUsernameError,
                )
            except ImportError:
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="user", data_schema=DATA_SCHEMA, errors=errors
                )

            try:
                client = MyT(
                    username=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                    use_metric=True,
                    brand="T",
                )
                await client.login()
                vehicles = await client.get_vehicles()
            except ToyotaInvalidUsernameError:
                errors["base"] = "invalid_username"
            except ToyotaLoginError:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error connecting to Toyota")
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
                self._abort_if_unique_id_configured()

                title = user_input[CONF_EMAIL]
                if vehicles:
                    v = vehicles[0]
                    title = v.alias or f"Toyota ({(v.vin or '')[-6:]})"

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
