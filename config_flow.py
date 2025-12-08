import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from .const import DOMAIN, DEFAULT_SLAVE_ID

_LOGGER = logging.getLogger(__name__)

class DanfossECLFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Danfoss ECL."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Hier könnten Sie eine Verbindungsprüfung hinzufügen, 
            # um sicherzustellen, dass die IP/Port gültig sind, bevor Sie speichern.
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        # Verwenden Sie ein Wörterbuch für die Standardwerte, das hilft oft bei der UI-Darstellung
        data_schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=502): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
