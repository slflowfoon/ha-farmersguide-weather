"""Data coordinator for Farmers Guide Weather."""
from __future__ import annotations

import logging
import re
from datetime import timedelta

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

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


class FarmersGuideCoordinator(DataUpdateCoordinator):
    """Fetches and caches soil temperature from the Farmers Guide 72-hr forecast."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="farmersguide_weather",
            update_interval=timedelta(hours=1),
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
            raise UpdateFailed(
                "Soil temperature cell not found — site structure may have changed"
            )

        text = cell.get_text(strip=True)
        match = re.search(r"(-?\d+\.?\d*)", text)
        if not match:
            raise UpdateFailed(f"Could not parse soil temperature: {text!r}")

        return float(match.group(1))
