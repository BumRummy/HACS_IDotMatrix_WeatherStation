from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([IDMWeatherStatusSensor(coordinator, entry)])


class IDMWeatherStatusSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Display status"
    _attr_icon = "mdi:led-strip-variant"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self):
        return self.coordinator.data.get("condition") if self.coordinator.data else "unknown"

    @property
    def extra_state_attributes(self):
        return self.coordinator.data or {}
