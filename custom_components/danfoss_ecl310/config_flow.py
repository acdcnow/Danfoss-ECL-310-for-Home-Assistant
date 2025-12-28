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
    """Validiert die Eingaben."""
    # Import lokal, um Zirkelbezüge/Ladefehler zu vermeiden
    from .modbus_client import DanfossModbusHub
    
    hub = DanfossModbusHub(data[CONF_HOST], data[CONF_PORT])
    
    try:
        await hub.connect()
        # Test-Register lesen (Slave 254)
        # Wir nutzen hier 4200 (Betriebsart Heizung) als Test
        test_val = await hub.read_register(4200, slave_id=254, input_type="input")
        
        if test_val is None:
            _LOGGER.warning("Verbindung steht, aber keine Daten lesbar.")
            
    except Exception as e:
        _LOGGER.error(f"Verbindungsfehler im Config Flow: {e}")
        raise ConnectionError
    finally:
        # WICHTIG: Hier stand vorher 'await hub.close()'.
        # Da close() jetzt synchron ist, muss das 'await' weg!
        hub.close()

    return {"title": f"Danfoss ECL310 ({data[CONF_HOST]})"}

class DanfossConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # Prüfen ob IP schon existiert
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.exception("Unerwarteter Fehler")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
