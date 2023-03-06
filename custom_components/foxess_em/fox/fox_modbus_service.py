"""Fox controller"""
import logging
from datetime import datetime
from datetime import time

from homeassistant.core import HomeAssistant

from .fox_modbus import FoxModbus
from .fox_service import FoxService

_LOGGER = logging.getLogger(__name__)
_DAY = 40002
_CHARGE_CURRENT = 41007
_MIN_SOC = 41009
_P1_ENABLE = 41001


class FoxModbuservice(FoxService):
    """Fox Cloud service"""

    def __init__(
        self,
        hass: HomeAssistant,
        modbus: FoxModbus,
        off_peak_start: time,
        off_peak_end: time,
        user_min_soc: int = 10,
    ) -> None:
        """Init Fox Cloud service"""
        self._hass = hass
        self._modbus = modbus
        self._off_peak_start = off_peak_start
        self._off_peak_end = off_peak_end
        self._user_min_soc = user_min_soc

    async def start_force_charge_now(self, *args) -> None:
        """Start force charge now"""
        now = datetime.now().astimezone()
        start = now.replace(hour=0, minute=1).time()
        stop = now.replace(hour=23, minute=59).time()

        await self._start_force_charge(start, stop)

    async def start_force_charge_off_peak(self, *args) -> None:
        """Start force charge off peak"""
        await self._start_force_charge(self._off_peak_start, self._off_peak_end)

    async def _start_force_charge(self, start, stop) -> None:
        """Start force charge"""
        _LOGGER.debug("Requesting start force charge from Fox Modbus")
        start_encoded, stop_encoded = self._encode_time(start, stop)

        self._modbus.write_registers(
            _P1_ENABLE, [1, start_encoded, stop_encoded, 0, 0, 0]
        )

    async def stop_force_charge(self, *args) -> None:  # pylint: disable=unused-argument
        """Start force charge"""
        _LOGGER.debug("Requesting stop force charge from Fox Modbus")
        self._modbus.write_registers(_P1_ENABLE, [0, 0, 0, 0, 0, 0])

    async def set_min_soc(
        self, soc: int, *args
    ) -> None:  # pylint: disable=unused-argument
        """Start force charge"""
        _LOGGER.debug("Request set min SoC to Fox Modbus")
        self._modbus.write_registers(_MIN_SOC, [soc])

    async def set_charge_current(self, charge_current: float, *args) -> None:
        """Set charge current"""
        _LOGGER.debug(
            f"Requesting set charge current of {charge_current}A to Fox Modbus"
        )
        self._modbus.write_registers(_CHARGE_CURRENT, [charge_current * 10])

    async def device_info(self) -> None:
        """Get device info"""
        return self._modbus.read_input_registers(_DAY, 1)[0] == datetime.now().day

    def _encode_time(self, start, stop):
        """Encode time to Fox time"""
        start_encoded = (start.hour * 256) + start.minute
        stop_encoded = (stop.hour * 256) + stop.minute
        return start_encoded, stop_encoded