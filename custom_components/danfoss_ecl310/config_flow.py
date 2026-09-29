"""Config flow for the Danfoss ECL 310 integration."""

from __future__ import annotations

import logging
from typing import Any, Final

from modbus_connection import ModbusError, ModbusTcpParams
import voluptuous as vol

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_PORT, DEFAULT_UNIT_ID, DOMAIN
from .device import INPUT, DanfossEcl310, RegisterRef

_LOGGER = logging.getLogger(__name__)

CONF_NAME: Final = "name"

#: The operating mode of the heating circuit, used purely to prove the
#: controller answers on the given host and port.
PROBE_REFS: Final[tuple[RegisterRef, ...]] = (
    RegisterRef(key="mode_heating", address=4200, space=INPUT),
)


async def _async_probe(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Check that the controller answers on the configured address.

    The connection itself is owned by the ``modbus`` integration, so a temporary
    unit is borrowed for the duration of the flow rather than opening a socket
    here. Raises :class:`~modbus_connection.ModbusError` when it does not answer,
    and :class:`HomeAssistantError` when an existing entry already uses the same
    device over different link settings.
    """
    async with async_get_temporary_unit(
        hass,
        ModbusTcpParams(host=data[CONF_HOST], port=data[CONF_PORT]),
        DEFAULT_UNIT_ID,
    ) as unit:
        await DanfossEcl310(unit).async_read_group(PROBE_REFS)


class DanfossEcl310ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle setting up a Danfoss ECL 310 from the UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the controller's address and verify it responds."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # The host is the unique id, so two entries cannot point at the same
            # controller and fight over it.
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_configured()

            try:
                await _async_probe(self.hass, user_input)
            except (ModbusError, HomeAssistantError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error while probing the controller")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME) or self._default_name(),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=self._user_schema(), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the controller's address without recreating the entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await _async_probe(self.hass, user_input)
            except (ModbusError, HomeAssistantError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error while probing the controller")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    unique_id=user_input[CONF_HOST],
                    data_updates=user_input,
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                    vol.Required(CONF_PORT, default=entry.data[CONF_PORT]): cv.port,
                }
            ),
            errors=errors,
        )

    def _default_name(self) -> str:
        """Suggest the next free name, e.g. ``ECL 2``."""
        return f"ECL {len(self._async_current_entries()) + 1}"

    def _user_schema(self) -> vol.Schema:
        """Build the setup form."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_NAME, default=self._default_name()): str,
            }
        )