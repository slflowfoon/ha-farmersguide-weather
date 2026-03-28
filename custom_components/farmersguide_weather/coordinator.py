"""Data coordinator for Farmers Guide Weather."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

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


@dataclass
class FarmersGuideData:
    """Holds scraped data from the current forecast row."""

    soil_temp: float
    soil_moisture: float


def _parse_number(text: str) -> float | None:
    """Extract the first numeric value from a string."""
    match = re.search(r"(-?\d+\.?\d*)", text)
    return float(match.group(1)) if match else None


class FarmersGuideCoordinator(DataUpdateCoordinator[FarmersGuideData]):
    """Fetches and caches forecast data from the Farmers Guide 72-hr table."""

    def __init__(self, hass: HomeAssistant, postcode: str) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="farmersguide_weather",
            update_interval=timedelta(hours=1),
        )
        self.postcode = postcode
        self.url = f"https://www.farmersguide.co.uk/weather/?postcode={postcode}"

    async def _async_update_data(self) -> FarmersGuideData:
        """Scrape the current forecast row."""
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                self.url,
                headers=HEADERS,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching Farmers Guide page: {err}") from err

        soup = BeautifulSoup(html, "html.parser")

        # All data comes from the first <tr> in the forecast table
        row = soup.find("tr", class_="first-date")
        if row is None:
            # Fall back to first data row
            row = soup.find("tbody").find("tr") if soup.find("tbody") else None
        if row is None:
            raise UpdateFailed("Could not find forecast table row — site structure may have changed")

        soil_cell = row.find("td", class_="weather-soil")
        moisture_cell = row.find("td", class_="weather-moisture")

        if soil_cell is None:
            raise UpdateFailed("Soil temperature cell not found")

        soil_temp = _parse_number(soil_cell.get_text(strip=True))
        if soil_temp is None:
            raise UpdateFailed(f"Could not parse soil temperature: {soil_cell.get_text()!r}")

        soil_moisture = None
        if moisture_cell is not None:
            soil_moisture = _parse_number(moisture_cell.get_text(strip=True))

        return FarmersGuideData(
            soil_temp=soil_temp,
            soil_moisture=soil_moisture,
        )
