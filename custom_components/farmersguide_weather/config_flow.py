"""Config flow for Farmers Guide Weather."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

DOMAIN = "farmersguide_weather"


class FarmersGuideConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Farmers Guide Weather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        """Single-step setup — no inputs needed, postcode is fixed."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title="Farmers Guide Weather (RH19 3QG)",
                data={},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={
                "postcode": "RH19 3QG",
                "source": "farmersguide.co.uk",
            },
        )
