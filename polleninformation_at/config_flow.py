"""Config flow for Polleninformation.at integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_API_URL, DEFAULT_API_URL, SENSOR_TYPES

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Polleninformation.at."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_API_URL, default=DEFAULT_API_URL): str,
                        vol.Required("sensors"): cv.multi_select(SENSOR_TYPES),
                    }
                ),
            )

        return self.async_create_entry(title="Polleninformation.at", data=user_input)