"""Support for Modbus Devices Switch Entitys."""

import logging

from pymodbus.exceptions import ConnectionException

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import Config

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Load configuration for outputs."""

    try:
        device = hass.data[Config.DOMAIN][entry.options["secret"]]
        entitys = []
        for output in await device.get_outputs():
            entity = ModBusSwitchEntity(
                device=device,
                unique_id=entry.options["secret"],
                output=output,
            )
            entitys.append(entity)
        async_add_entities(entitys, True)
    except KeyError as exc:
        _LOGGER.error("Unknoun error %s", exc)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Delete current configuration."""
    hass.data[Config.DOMAIN].pop(entry.options["secret"])
    return True


class ModBusSwitchEntity(SwitchEntity):
    """Class control switch."""

    _attr_has_entity_name = True
    # _attr_name = None

    def __init__(self, device, unique_id=None, output=None) -> None:
        """Initialization process."""
        self._device = device
        self._output = output
        self._attr_name = (
            f"{self._output['out_type']} {self._output['out_number_view']}"
        )
        self._attr_available = True
        self._is_on = output["state"]
        self._unique_id = unique_id
        # self.entity_id = unique_id
        self._attr_unique_id = (
            f"{self._output['out_type']}_{self._output['out_number']}_{self._unique_id}"
        )
        self._attr_device_class = self._output["device_class"]
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
            self._is_on = (await self._device.get_output(self._output["out_number"]))[
                "state"
            ]
            self._attr_available = True
        except ConnectionException as exc:
            _LOGGER.error("Can't update: %s", exc)
            self._attr_available = False
        return self._is_on

    @property
    def icon(self) -> str | None:
        """Icon of the entity."""
        if self._is_on:
            return self._output["icon_on"]
        return self._output["icon_off"]

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

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        _LOGGER.info("Turn on output: %s", self._output["out_number"])
        out = await self._device.set_output(self._output["out_number"], True)
        self._is_on = out["state"]

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        _LOGGER.info("Turn off output: %s", self._output["out_number"])
        out = await self._device.set_output(self._output["out_number"], False)
        self._is_on = out["state"]
