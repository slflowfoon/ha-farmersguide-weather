"""Farmers Guide soil temperature sensor.

Scrapes the 72-hour forecast table from farmersguide.co.uk and exposes
the current soil temperature as a Home Assistant sensor.
"""
from __future__ import annotations

import logging
import re
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "farmersguide_weather"
SCAN_INTERVAL = timedelta(hours=1)

POSTCODE = "RH19+3QG"
URL = f"https://www.farmersguide.co.uk/weather/?postcode={POSTCODE}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.farmersguide.co.uk/",
}


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Farmers Guide soil temperature sensor."""
    coordinator = FarmersGuideCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    async_add_entities([FarmersGuideSoilTempSensor(coordinator)])


class FarmersGuideCoordinator(DataUpdateCoordinator):
    """Fetches and caches soil temperature from the Farmers Guide 72-hr forecast."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> float:
        """Scrape the current soil temperature value."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                URL,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Farmers Guide page: {err}") from err

        soup = BeautifulSoup(html, "html.parser")
        cell = soup.find("td", class_="weather-soil")
        if cell is None:
            raise UpdateFailed("Soil temperature cell not found in page — site structure may have changed")

        text = cell.get_text(strip=True)
        match = re.search(r"(-?\d+\.?\d*)", text)
        if not match:
            raise UpdateFailed(f"Could not parse soil temperature value: {text!r}")

        return float(match.group(1))


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
        """Return additional attributes."""
        return {
            "source": "farmersguide.co.uk",
            "postcode": POSTCODE.replace("+", " "),
        }
