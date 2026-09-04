from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_ADDRESS,
    CONF_WEATHER_ENTITY,
    CONF_PACK_PATH,
    CONF_SIZE,
    CONF_TIME_FORMAT,
    CONF_REFRESH_SECONDS,
    DEFAULT_PACK_PATH,
    DEFAULT_SIZE,
    DEFAULT_TIME_FORMAT,
    DEFAULT_REFRESH_SECONDS,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_ADDRESS].lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"iDotMatrix {user_input[CONF_ADDRESS]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_ADDRESS): str,
            vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="weather")
            ),
            vol.Required(CONF_PACK_PATH, default=DEFAULT_PACK_PATH): str,
            vol.Required(CONF_SIZE, default=DEFAULT_SIZE): vol.In([32, 64]),
            vol.Required(CONF_TIME_FORMAT, default=DEFAULT_TIME_FORMAT): str,
            vol.Required(CONF_REFRESH_SECONDS, default=DEFAULT_REFRESH_SECONDS): vol.All(
                vol.Coerce(int), vol.Range(min=15, max=900)
            ),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
