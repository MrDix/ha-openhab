"""Sensor platform for openHAB."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN, ITEMS_MAP, SENSOR, LOGGER
from .device_classes_map import SENSOR_DEVICE_CLASS_MAP
from .entity import OpenHABEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Define group types that have specific platforms
    specific_group_types = {"Switch", "Rollershutter", "Color", "Dimmer", "Contact", "Player"}

    sensors = []
    for item in coordinator.data.values():
        if (item.type_ex == 'devireg_attr_ui_sensor'):
            sensors.append(OpenHABSensor(hass, coordinator, item))
        elif ((item.type_ex == False) and (item.type_ in ITEMS_MAP[SENSOR])):
            sensors.append(OpenHABSensor(hass, coordinator, item))
        elif (item.type_ == "Group" and (not hasattr(item, 'groupType') or item.groupType not in specific_group_types)):
            sensors.append(OpenHABSensor(hass, coordinator, item))
        # NOTE: Untyped groups (type_ = None) are now handled as switches, not sensors
    
    LOGGER.info(f"Sensor platform: Adding {len(sensors)} sensor entities out of {len(coordinator.data)} total items")
    async_add_entities(sensors)


class OpenHABSensor(OpenHABEntity, SensorEntity):
    """openHAB Sensor class."""

    _attr_device_class_map = SENSOR_DEVICE_CLASS_MAP

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self.item._state
