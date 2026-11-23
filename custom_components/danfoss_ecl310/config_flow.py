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
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .applications import APPLICATIONS
from .const import (
    APP_KEY_REGISTER,
    APP_SUBTYPE_REGISTER,
    CONF_APPLICATION,
    DEFAULT_APPLICATION,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .device import HOLDING, INPUT, DanfossEcl310, RegisterRef

_LOGGER = logging.getLogger(__name__)

CONF_NAME: Final = "name"

#: The operating mode of the heating circuit proves the controller answers on
#: the given host and port. The application key and subtype identify the loaded
#: application, so a wrong selection can be caught during setup.
PROBE_REFS: Final[tuple[RegisterRef, ...]] = (
    RegisterRef(key="mode_heating", address=4200, space=INPUT),
    RegisterRef(key="app_key", address=APP_KEY_REGISTER, space=HOLDING),
    RegisterRef(key="app_subtype", address=APP_SUBTYPE_REGISTER, space=HOLDING),
)


async def _async_probe(
    hass: HomeAssistant, data: dict[str, Any]
) -> dict[str, int | None]:
    """Check that the controller answers on the configured address.

    The connection itself is owned by the ``modbus`` integration, so a temporary
    unit is borrowed for the duration of the flow rather than opening a socket
    here. Raises :class:`~modbus_connection.ModbusError` when it does not answer,
    and :class:`HomeAssistantError` when an existing entry already uses the same
    device over different link settings. Returns the probed values; a register
    the controller did not answer is ``None``.
    """
    async with async_get_temporary_unit(
        hass,
        ModbusTcpParams(host=data[CONF_HOST], port=data[CONF_PORT]),
        DEFAULT_UNIT_ID,
    ) as unit:
        return await DanfossEcl310(unit).async_read_group(PROBE_REFS)


def _application_matches(application_key: str, probed: dict[str, int | None]) -> bool:
    """Return whether the controller runs the selected application.

    Only a value the controller actually reported can contradict the selection:
    a register that did not answer never blocks the setup, and an application
    that declares no expected key (A247.1) is not checked at all.
    """
    application = APPLICATIONS[application_key]
    for expected, actual in (
        (application.expected_app_key, probed.get("app_key")),
        (application.expected_subtype, probed.get("app_subtype")),
    ):
        if expected is not None and actual is not None and actual != expected:
            return False
    return True


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
                probed = await _async_probe(self.hass, user_input)
            except (ModbusError, HomeAssistantError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error while probing the controller")
                errors["base"] = "unknown"
            else:
                if _application_matches(user_input[CONF_APPLICATION], probed):
                    return self.async_create_entry(
                        title=user_input.get(CONF_NAME) or self._default_name(),
                        data=user_input,
                    )
                errors[CONF_APPLICATION] = "application_mismatch"

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                self._user_schema(), user_input
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the controller's address without recreating the entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                probed = await _async_probe(self.hass, user_input)
            except (ModbusError, HomeAssistantError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error while probing the controller")
                errors["base"] = "unknown"
            else:
                # The application is not changeable here: entities are tied to
                # the register map they were created with. Pointing the entry at
                # a controller that runs a different application is refused.
                if _application_matches(
                    entry.data.get(CONF_APPLICATION, DEFAULT_APPLICATION), probed
                ):
                    return self.async_update_reload_and_abort(
                        entry,
                        unique_id=user_input[CONF_HOST],
                        data_updates=user_input,
                    )
                errors["base"] = "application_mismatch"

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
                vol.Required(
                    CONF_APPLICATION, default=DEFAULT_APPLICATION
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=key, label=application.name)
                            for key, application in APPLICATIONS.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_NAME, default=self._default_name()): str,
            }
        )