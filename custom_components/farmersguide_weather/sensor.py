"""Farmers Guide soil temperature sensor."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import FarmersGuideCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from a config entry."""
    coordinator: FarmersGuideCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FarmersGuideSoilTempSensor(coordinator)])


class FarmersGuideSoilTempSensor(CoordinatorEntity, SensorEntity):
    """Current soil temperature from the Farmers Guide 72-hour forecast."""

    _attr_name = "Farmers Guide Soil Temperature"
    _attr_unique_id = "farmersguide_soil_temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    @property
    def native_value(self) -> float | None:
        """Return the current soil temperature."""
        return self.coordinator.data

    @property
    def extra_state_attributes(self) -> dict:
        """Return source attributes."""
        return {
            "source": "farmersguide.co.uk",
            "postcode": "RH19 3QG",
        }
