"""Support for Modbus Devices Binary Sensor Entitys."""

import logging

from pymodbus.exceptions import ConnectionException

from homeassistant.components.binary_sensor import BinarySensorEntity
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
        for in_put in await device.get_inputs():
            entity = ModBusBinarySensorEntity(
                device=device,
                unique_id=entry.options["secret"],
                input=in_put,
            )
            entitys.append(entity)
        async_add_entities(entitys, True)
    except KeyError as exc:
        _LOGGER.error("Unknoun error %s", exc)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Delete current configuration."""
    hass.data[Config.DOMAIN].pop(entry.options["secret"])
    return True


class ModBusBinarySensorEntity(BinarySensorEntity):
    """Class control binary sensor entity."""

    _attr_has_entity_name = True
    # _attr_name = None

    def __init__(self, device, unique_id=None, input=None) -> None:
        """Initialization process."""
        self._device = device
        self._input = input
        self._attr_name = (
            f"{self._input['input_type']} {self._input['input_number_view']}"
        )
        self._attr_available = True
        self._is_on = input["state"]
        self._unique_id = unique_id
        # self.entity_id = unique_id
        self._attr_unique_id = f"{self._input['input_type']}_{self._input['input_number']}_{self._unique_id}"
        self._attr_device_class = input["device_class"]
        self._disabled_reported = False
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

    async def async_update(self) -> None:
        """Update entity state."""
        try:
            self._is_on = (await self._device.get_input(self._input["input_number"]))[
                "state"
            ]
            self._attr_available = True
        except ConnectionException as exc:
            _LOGGER.error("Can't update: %s", exc)
            self._attr_available = False
        return self._is_on

    @property
    def icon(self) -> str | None:
        """Icon of the entity, based on time."""
        if self._is_on:
            return self._input["icon_on"]
        return self._input["icon_off"]

    @property
    def unique_id(self):
        """Unuque id."""
        return self._attr_unique_id

    @property
    def name(self):
        """Name."""
        return self._attr_name

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on
