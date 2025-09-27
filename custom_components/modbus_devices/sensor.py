"""Support for Modbus Devices Sensor Entitys."""

import logging

from pymodbus.exceptions import ConnectionException

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import Config

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Load configuration for inputs."""
    try:
        device = hass.data[Config.DOMAIN][entry.options["secret"]]
        entitys = []
        for chanel in await device.get_chanels():
            entity = ModBusSensorEntity(
                device=device,
                unique_id=entry.options["secret"],
                chanel=chanel,
            )
            entitys.append(entity)
        async_add_entities(entitys, True)
    except KeyError as exc:
        _LOGGER.error("Unknoun error %s", exc)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Delete current device configuration."""
    hass.data[Config.DOMAIN].pop(entry.options["secret"])
    return True


class ModBusSensorEntity(SensorEntity):
    """Class pull values from sensores."""

    _attr_has_entity_name = True
    # _attr_name = None

    def __init__(self, device, unique_id=None, chanel=None) -> None:
        """Initialization process."""
        self._device = device
        self._chanel = chanel
        self._attr_name = (
            f"{self._chanel['chanel_type']} {self._chanel['chanel_number_view']}"
        )
        self._attr_available = True
        self._is_on = chanel["value"]
        self._unique_id = unique_id
        # self.entity_id = unique_id
        self._attr_unique_id = f"{self._chanel['chanel_type']}_{self._chanel['chanel_number']}_{self._unique_id}"
        self._attr_device_class = self._chanel["device_class"]
        self._attr_state_class = self._chanel["state_class"]
        self._attr_native_unit_of_measurement = self._chanel["unit_of_temperature_c"]
        self._attr_native_value = 0
        self._attr_suggested_display_precision = 0
        self._attr_device_info = DeviceInfo(
            identifiers={
                (Config.DOMAIN, self._unique_id),
            },
            manufacturer=self._device.attr_manufactures_name,
            model=self._device.attr_model_name,
            name=self._device.attr_description,
            hw_version=str(self._device.attr_hardware_version),
            sw_version=str(self._device.attr_software_version),
            serial_number=self._device.attr_serial_number,
        )

    @property
    def should_poll(self):
        """Should pool."""
        return True

    async def async_update(self) -> str:
        """Update entity state."""
        try:
            native_value = (
                await self._device.get_chanel(self._chanel["chanel_number"])
            )["value"]
            self._attr_suggested_display_precision = native_value[0]
            self._attr_native_value = native_value[1] / (10 ** native_value[0])
            self._attr_available = True
        except ConnectionException as exc:
            _LOGGER.error("Can't update: %s", exc)
            self._attr_available = False
        return self._attr_native_value

    @property
    def unique_id(self):
        """Unuque id."""
        return self._attr_unique_id

    @property
    def name(self):
        """Name."""
        return self._attr_name
