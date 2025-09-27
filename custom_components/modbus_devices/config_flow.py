"""Config flow for modbus_devices integration."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_PORT
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector

from .const import Config
from .equipment.equipment import (
    get_classes_from_files,
    get_random_hex_string,
    get_serial_ports,
)

_LOGGER = logging.getLogger(__name__)


class ModbusDevicesConfigFlow(ConfigFlow, domain=Config.DOMAIN):
    """class ConfigFLowHandler."""

    VERSION = 1

    def __init__(self) -> None:
        """Initcialization class."""
        self._step_user_data: dict[str, Any] = {}
        self._entry: ConfigFlow | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """User actions when initializing a component."""
        errors: dict[str, str] = {}
        data: dict[str, Any] = {}
        con_type = {
            vol.Required("ModBus MODE:"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": [
                            "ModBus TCP/IP",
                            "ModBus UDP/IP",
                            "SerialPort",
                        ],
                    },
                },
            )
        }
        tcp_udp = {
            vol.Required(CONF_HOST, default="10.0.2.13"): cv.string,
            vol.Required(CONF_PORT, default=510): int,
            vol.Required(CONF_DEVICE_ID, default=15): int,
            vol.Required("Connect To:"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": await get_classes_from_files(),
                    },
                },
            ),
        }
        serial = {
            vol.Required("Connect To:"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": await get_classes_from_files(),
                    },
                },
            ),
            vol.Required(CONF_DEVICE_ID, default=1): int,
            vol.Required("Com_port:"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": await get_serial_ports(),
                    },
                },
            ),
            vol.Required("Baudrate:", default="9600"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": [
                            "300",
                            "600",
                            "1200",
                            "2400",
                            "4800",
                            "9600",
                            "14400",
                            "19200",
                            "38400",
                            "56000",
                            "57600",
                            "115200",
                            "128000",
                            "153600",
                            "230400",
                            "256000",
                            "460800",
                            "921600",
                        ],
                    },
                },
            ),
            vol.Required("Bytesize:", default="8"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": ["7", "8"],
                    },
                },
            ),
            vol.Required("Parity:", default="N"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": ["E", "O", "N"],
                    },
                },
            ),
            vol.Required("Stopbits:", default="1"): selector(
                {
                    "select": {
                        "mode": "dropdown",
                        "options": ["0", "1", "2"],
                    },
                },
            ),
        }

        if user_input is not None:
            try:
                if (
                    user_input["ModBus MODE:"] == "ModBus TCP/IP"
                    or user_input["ModBus MODE:"] == "ModBus UDP/IP"
                ):
                    self._step_user_data = user_input
                    return self.async_show_form(
                        step_id="user", data_schema=vol.Schema(tcp_udp), errors=errors
                    )
                if user_input["ModBus MODE:"] == "SerialPort":
                    self._step_user_data = user_input
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema(serial),
                        errors=errors,
                    )
            except KeyError:
                self._step_user_data["secret"] = get_random_hex_string(
                    Config.WORD_LENGTH
                )
                data = dict(**self._step_user_data, **user_input)
                self._abort_if_unique_id_configured()
                await self.async_set_unique_id(self._step_user_data["secret"])
                _LOGGER.info("Creating a flow: %s", data)
                return self.async_create_entry(title=Config.NAME, data=data)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(con_type), errors=errors
        )
