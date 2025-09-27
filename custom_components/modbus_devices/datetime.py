"""Support for Modbus Devices Date Time Entitys."""

from datetime import datetime, timedelta, timezone
import logging

from pymodbus.exceptions import ConnectionException

from homeassistant.components.datetime import DateTimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import Config

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Load configuration for datetime."""
    try:
        device = hass.data[Config.DOMAIN][entry.options["secret"]]
        entitys = []
        for number in device.attr_clock_iter:
            entity = ModBusDevicesDateTime(
                device=device,
                unique_id=entry.options["secret"],
                number=number,
            )
            entitys.append(entity)
        async_add_entities(entitys, True)
    except KeyError as exc:
        _LOGGER.error("Unknoun error %s", exc)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Delete current configuration."""
    hass.data[Config.DOMAIN].pop(entry.options["secret"])
    return True


class ModBusDevicesDateTime(DateTimeEntity):
    """Load configuration for datetime."""

    _attr_has_entity_name = True

    def __init__(self, device, unique_id=None, number=None) -> None:
        """Initialization process."""
        self._device = device
        self._attr_name = f"{self._device.attr_description} clock"
        self._attr_available = True
        self._number: int = number
        self._unique_id = unique_id
        self._attr_unique_id = f"{self._device.attr_description}_{self._device.attr_device_type}_clock_{self._number}_{self._unique_id}"
        self.native_value: datetime | None = (datetime.now()).replace(
            tzinfo=timezone(timedelta(hours=Config.TIME_ZONE)),
            microsecond=0,
        )
        self._attr_device_info: DeviceInfo = DeviceInfo(
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

    async def async_update(self) -> datetime:
        """Update entity state."""
        try:
            if self.native_value < (datetime.now()).replace(
                tzinfo=timezone(timedelta(hours=Config.TIME_ZONE)),
                microsecond=0,
            ):
                self.native_value = (await self._device.set_time()) + timedelta(
                    hours=Config.TIME_DELTA
                )
                _LOGGER.info(
                    "Time in controller updated, next time value for update: %s",
                    self.native_value,
                )
            self._attr_available = True
        except ConnectionException as exc:
            _LOGGER.error("Can't update time: %s", exc)
            self.native_value = None
        return self.native_value

    async def async_set_value(self, value: datetime) -> None:
        """Updating date and time manually."""
        self.native_value = value
        _LOGGER.info("Updating date and time manually: %s", self.native_value)

    @property
    def unique_id(self):
        """Unuque id."""
        return self._attr_unique_id

    @property
    def name(self):
        """Name."""
        return self._attr_name
