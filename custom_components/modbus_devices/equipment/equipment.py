"""helpers function for dir work."""

import inspect
import logging
import os
from pathlib import Path
import random
import sys

from serial import Serial, SerialException

from ..const import Config

_LOGGER = logging.getLogger(__name__)


async def get_class(module: str, cls_name: str):
    """Get objeckt from equipment."""

    return getattr(
        __import__(name=module, globals=globals(), locals=locals(), level=1),
        cls_name,
    )


async def get_classes_from_files() -> list[str]:
    """Get classes name from files with equipment."""
    module: list[str] = []
    dir_path = Path(os.path.realpath(__file__)).parent

    for file in [f.name.replace(".py", "") for f in dir_path.iterdir() if f.is_file()]:
        for name, obj in inspect.getmembers(
            __import__(name=file, globals=globals(), locals=locals(), level=1),
            inspect.isclass,
        ):
            try:
                if (
                    obj.__module__.split(".", -1)[3] == file
                    and obj.__module__ is not __name__
                    and obj.__module__ != "__init__"
                ):
                    module.append(f"{file} {name}")
            except IndexError:
                continue
    return module


async def get_serial_ports() -> list[str]:
    """
    Lists serial port names

    :raises EnvironmentError:
       On unsupported or unknown platforms

    :returns:
       A list of the serial ports available on the system.
    """

    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        # this excludes your current terminal "/dev/tty"
        ports = list(Path("/dev").glob("tty[A-Za-z]*"))
    elif sys.platform.startswith("darwin"):
        ports = list(Path("/dev").glob("tty.*"))
    else:
        raise OSError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = Serial(str(port))
            s.close()
            result.append(str(port))
        except (OSError, SerialException):
            pass
    return (
        result[::-1],
        [
            "Not Found.",
        ],
    )[not result]


def get_random_hex_string(_range: int = 32):
    """Randomize hex number string."""
    return "".join([random.choice(Config.WORD) for x in range(_range)])
