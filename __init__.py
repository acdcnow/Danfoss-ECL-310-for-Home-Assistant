import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DanfossECLFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Danfoss ECL."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step (IP and Port input)."""
        errors = {}
        if user_input is not None:
            # In einer echten Integration würden Sie hier die Verbindung testen
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=502): int,
            }),
            errors=errors,
        )
