import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
})

async def validate_input(hass: HomeAssistant, data: dict) -> dict:
    """Validiert die Eingaben und testet die Verbindung."""
    from .modbus_client import DanfossModbusHub
    
    hub = DanfossModbusHub(data[CONF_HOST], data[CONF_PORT])
    
    try:
        await hub.connect()
        # Test-Register lesen (Slave 254), z.B. 4200 (Betriebsart)
        test_val = await hub.read_register(4200, slave_id=254, input_type="input")
        
        if test_val is None:
            _LOGGER.warning("Verbindung steht, aber keine Daten lesbar.")
            
    except Exception as e:
        _LOGGER.error(f"Verbindungsfehler im Config Flow: {e}")
        raise ConnectionError
    finally:
        hub.close()

    return {"title": data.get("name", f"ECL 310 ({data[CONF_HOST]})")}

class DanfossConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        
        # 1. Berechne Vorschlag für den Namen (ECL 1, ECL 2 ...)
        current_entries = self._async_current_entries()
        count = len(current_entries) + 1
        default_name = f"ECL {count}"

        if user_input is not None:
            # Prüfen ob IP schon existiert
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            try:
                await validate_input(self.hass, user_input)
                
                # WICHTIG: Den vom User gewählten Namen als Titel setzen
                return self.async_create_entry(
                    title=user_input.get("name", default_name), 
                    data=user_input
                )
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.exception("Unerwarteter Fehler")
                errors["base"] = "unknown"

        # Schema mit Namens-Feld erweitern
        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Optional("name", default=default_name): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )