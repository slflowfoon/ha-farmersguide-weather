"""Config flow for Farmers Guide Weather."""
from __future__ import annotations

import re

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

DOMAIN = "farmersguide_weather"


def _normalise_postcode(postcode: str) -> str:
    """Strip spaces and uppercase for use in the URL."""
    return re.sub(r"\s+", "+", postcode.strip().upper())


class FarmersGuideConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Farmers Guide Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Prompt for a UK postcode."""
        errors: dict[str, str] = {}

        if user_input is not None:
            postcode_raw = user_input["postcode"].strip()
            # Basic UK postcode format check
            if not re.match(
                r"^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$",
                postcode_raw.upper(),
            ):
                errors["postcode"] = "invalid_postcode"
            else:
                postcode_url = _normalise_postcode(postcode_raw)
                await self.async_set_unique_id(postcode_url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Farmers Guide Weather ({postcode_raw.upper()})",
                    data={"postcode": postcode_url},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("postcode"): str}),
            errors=errors,
        )
