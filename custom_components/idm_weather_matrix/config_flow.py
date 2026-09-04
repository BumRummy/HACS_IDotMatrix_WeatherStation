from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak, async_discovered_service_info
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
    VERSION = 2

    def __init__(self) -> None:
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak):
        self._discovery_info = discovery_info
        address = discovery_info.address
        await self.async_set_unique_id(address.lower())
        self._abort_if_unique_id_configured()

        self.context["title_placeholders"] = {
            "name": discovery_info.name or discovery_info.address
        }
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input=None):
        assert self._discovery_info is not None
        if user_input is not None:
            return self.async_create_entry(
                title=self._discovery_info.name or f"iDotMatrix {self._discovery_info.address}",
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    CONF_WEATHER_ENTITY: user_input[CONF_WEATHER_ENTITY],
                    CONF_PACK_PATH: user_input[CONF_PACK_PATH],
                    CONF_SIZE: user_input[CONF_SIZE],
                    CONF_TIME_FORMAT: user_input[CONF_TIME_FORMAT],
                    CONF_REFRESH_SECONDS: user_input[CONF_REFRESH_SECONDS],
                },
            )

        schema = vol.Schema({
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
        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=schema,
            description_placeholders={
                "name": self._discovery_info.name or self._discovery_info.address,
                "address": self._discovery_info.address,
            },
        )

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            address = user_input.pop(CONF_ADDRESS)
            await self.async_set_unique_id(address.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"iDotMatrix {address}",
                data={CONF_ADDRESS: address, **user_input},
            )

        discovered = async_discovered_service_info(self.hass, connectable=True)
        idm_devices = [
            info for info in discovered
            if (info.name or "").upper().startswith("IDM-")
            or any(str(uuid).lower() == "000000fa-0000-1000-8000-00805f9b34fb" for uuid in info.service_uuids)
        ]

        if len(idm_devices) == 1:
            self._discovery_info = idm_devices[0]
            await self.async_set_unique_id(idm_devices[0].address.lower())
            self._abort_if_unique_id_configured()
            return await self.async_step_bluetooth_confirm()

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
