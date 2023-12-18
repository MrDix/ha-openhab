"""Switch platform for openHAB."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ITEMS_MAP, SWITCH
from .device_classes_map import SWITCH_DEVICE_CLASS_MAP
from .entity import OpenHABEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_devices(
        OpenHABBinarySwitch(hass, coordinator, item)
        for item in coordinator.data.values()
        if (item.type_ex == 'devireg_attr_ui_switch') or ( (item.type_ex == False) and (item.type_ in ITEMS_MAP[SWITCH]))
    )


class OpenHABBinarySwitch(OpenHABEntity, SwitchEntity):
    """openHAB switch class."""

    _attr_device_class_map = SWITCH_DEVICE_CLASS_MAP

    async def async_turn_on(self, **kwargs: dict[str, Any]) -> None:
        """Turn on the switch."""
        await self.hass.async_add_executor_job(self.item.on)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: dict[str, Any]) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(self.item.off)
        await self.coordinator.async_request_refresh()

    async def async_toggle(self, **kwargs: dict[str, Any]) -> None:
        """Turn off the switch."""
        await self.hass.async_add_executor_job(self.item.toggle)
        await self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.item._state == "ON"
