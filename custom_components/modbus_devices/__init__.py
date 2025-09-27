"""The modbus_devices service integration."""

from logging import getLogger

from pymodbus.exceptions import ConnectionException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import Config
from .equipment.equipment import get_class
from .modbus_client import connect_mb_Serial, connect_mb_TCP_or_UDP

_LOGGER = getLogger(__name__)


async def async_setup(hass, config):
    """Set up the modbus devices component."""
    hass.data[Config.DOMAIN] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ModbusDevices from a config entry."""
    # migrate data (after first setup) to options
    try:
        if entry.data:
            hass.config_entries.async_update_entry(entry, data={}, options=entry.data)

        if entry.options["ModBus MODE:"] == "SerialPort":
            client = await connect_mb_Serial(data=entry.options)
        elif (
            entry.options["ModBus MODE:"] == "ModBus TCP/IP"
            or entry.options["ModBus MODE:"] == "ModBus UDP/IP"
        ):
            client = await connect_mb_TCP_or_UDP(data=entry.options)
        cls = entry.options["Connect To:"].split(" ")
        device = await get_class(module=cls[0], cls_name=cls[1])
        device = device(client, entry.options["device_id"])
        await device.data_init()
        hass.data[Config.DOMAIN][entry.options["secret"]] = device
        _LOGGER.info("Create & save objeckt in hass.data...")

        # forward to platforms setup
        coro = hass.config_entries.async_forward_entry_setups(
            entry, (hass.data[Config.DOMAIN][entry.options["secret"]]).attr_platforms
        )
        await hass.async_create_task(coro)
        _LOGGER.info("Platforms setup, task created.")

    except (ImportError, ValueError) as exc:
        _LOGGER.error(exc)
    except ConnectionException as exc:
        _LOGGER.error(exc)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set down ModbusDevices from a config entry."""
    _LOGGER.info((hass.data[Config.DOMAIN][entry.options["secret"]]).attr_platforms)
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, (hass.data[Config.DOMAIN][entry.options["secret"]]).attr_platforms
    ):
        hass.data[Config.DOMAIN].pop(entry.options["secret"])

    return unload_ok
