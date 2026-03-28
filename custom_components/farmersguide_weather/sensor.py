"""Farmers Guide soil sensors."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .coordinator import FarmersGuideCoordinator, FarmersGuideData

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="soil_temp",
        name="Farmers Guide Soil Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="soil_moisture",
        name="Farmers Guide Soil Moisture",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:water-percent",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: FarmersGuideCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        FarmersGuideSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class FarmersGuideSensor(CoordinatorEntity[FarmersGuideCoordinator], SensorEntity):
    """A sensor sourced from the Farmers Guide 72-hour forecast."""

    def __init__(
        self,
        coordinator: FarmersGuideCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"farmersguide_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        data: FarmersGuideData = self.coordinator.data
        return getattr(data, self.entity_description.key, None)

    @property
    def extra_state_attributes(self) -> dict:
        """Return source attributes."""
        return {
            "source": "farmersguide.co.uk",
            "postcode": self.coordinator.postcode.replace("+", " "),
        }
