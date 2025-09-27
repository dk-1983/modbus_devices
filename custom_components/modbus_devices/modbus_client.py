"""Modbus client connection."""

import logging
from typing import Any

from pymodbus import ModbusException
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusUdpClient,
)

_LOGGER = logging.getLogger(__name__)


async def connect_mb_Serial(data: dict[str, Any]):
    """Connection Modbus Serial Port."""

    client = AsyncModbusSerialClient(
        port=data["Com_port:"],
        baudrate=int(data["Baudrate:"]),
        bytesize=int(data["Bytesize:"]),
        parity=data["Parity:"],
        stopbits=int(data["Stopbits:"]),
    )
    try:
        await client.connect()
        _LOGGER.info(
            "Connected to Serial Port: %s",
            f"{data['Com_port:']} id: {data['device_id']}",
        )
    except ModbusException as exc:
        _LOGGER.error("Error connection: %s", exc)
        client.close()
    return client


async def connect_mb_TCP_or_UDP(data: dict[str, Any]):
    """Connection Modbus TCP/UDP socket."""

    if data["ModBus MODE:"] == "ModBus UDP/IP":
        connection = AsyncModbusUdpClient
    elif data["ModBus MODE:"] == "ModBus TCP/IP":
        connection = AsyncModbusTcpClient

    client = connection(host=data["host"], port=data["port"], name=data["Connect To:"])

    try:
        await client.connect()
        _LOGGER.info("Connect to host: %s", f"{data['host']}:{data['port']} is OK.")
    except ModbusException as exc:
        _LOGGER.error("Error connection: %s", exc)
        client.close()
    return client
