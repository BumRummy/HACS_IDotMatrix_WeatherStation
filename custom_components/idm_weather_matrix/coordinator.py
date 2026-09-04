from __future__ import annotations

from datetime import timedelta
import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .builtin_pack import ensure_builtin_pack
from .const import (
    CONF_ADDRESS,
    CONF_WEATHER_ENTITY,
    CONF_PACK_PATH,
    CONF_SIZE,
    CONF_TIME_FORMAT,
    CONF_REFRESH_SECONDS,
)
from .pack import AnimationPack
from .renderer import GifRenderer, RenderValues
from .transport import IDMTransport

_LOGGER = logging.getLogger(__name__)


class IDMWeatherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.entry = entry
        self.weather_entity = entry.data[CONF_WEATHER_ENTITY]
        pack_path = entry.data[CONF_PACK_PATH]
        if pack_path == "__bundled_giraffe__":
            # Generate the bundled 64x64 giraffe GIF set locally on first use.
            # This keeps the HACS repository text-only and avoids shipping large binaries.
            pack_path = str(ensure_builtin_pack(Path(hass.config.path(".storage"))))
        self.pack = AnimationPack(pack_path, entry.data[CONF_SIZE])
        self.renderer = GifRenderer(entry.data[CONF_SIZE])
        self.transport = IDMTransport(hass, entry.data[CONF_ADDRESS])
        self.time_format = entry.data[CONF_TIME_FORMAT]

        self.last_render_key = None
        self.last_gif_size = 0

        super().__init__(
            hass,
            _LOGGER,
            name="iDotMatrix Weather Matrix",
            update_interval=timedelta(seconds=entry.data[CONF_REFRESH_SECONDS]),
        )

    async def _async_update_data(self):
        state = self.hass.states.get(self.weather_entity)
        if state is None:
            raise UpdateFailed(f"Weather entity {self.weather_entity} not found")

        condition = state.state
        temp = state.attributes.get("temperature")
        try:
            numeric_temp = float(temp) if temp is not None else None
        except (TypeError, ValueError):
            numeric_temp = None

        if numeric_temp is not None:
            unit_name = str(state.attributes.get("temperature_unit", "")).upper()
            if "C" in unit_name:
                if numeric_temp <= 0:
                    condition = "freezing"
                elif numeric_temp >= 32:
                    condition = "extreme_heat"
            else:
                if numeric_temp <= 32:
                    condition = "freezing"
                elif numeric_temp >= 90:
                    condition = "extreme_heat"

        now = dt_util.now()
        try:
            clock = now.strftime(self.time_format)
        except ValueError:
            clock = now.strftime("%I:%M").lstrip("0")

        if temp is None:
            temp_text = "--°"
        else:
            try:
                temp_text = f"{round(float(temp))}°"
            except (ValueError, TypeError):
                temp_text = f"{temp}°"

        condition_text = condition.replace("-", " ").replace("_", " ")
        render_key = (clock, temp_text, condition_text)

        if render_key != self.last_render_key:
            gif_path = self.pack.animation_for(condition)
            values = RenderValues(clock, temp_text, condition_text)
            gif_bytes = await self.hass.async_add_executor_job(
                self.renderer.render, gif_path, self.pack.layout, values
            )
            await self.transport.upload_gif(gif_bytes)
            self.last_gif_size = len(gif_bytes)
            self.last_render_key = render_key

        return {
            "condition": condition,
            "temperature": temp,
            "clock": clock,
            "gif_bytes": self.last_gif_size,
            "pack": str(self.pack.path),
        }

    async def async_force_refresh_display(self):
        self.last_render_key = None
        await self.async_request_refresh()

    async def async_close(self):
        await self.transport.close()
