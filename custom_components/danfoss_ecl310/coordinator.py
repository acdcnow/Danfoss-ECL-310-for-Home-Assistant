"""DataUpdateCoordinator for Danfoss ECL 310."""
import asyncio
import logging
import struct
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, REGISTER_MAP

_LOGGER = logging.getLogger(__name__)

class ECL310Coordinator(DataUpdateCoordinator):
    """Handle communication with ECL 310."""

    def __init__(self, hass, entry):
        """Initialize."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, 
            update_interval=timedelta(seconds=entry.options.get("scan_interval", entry.data.get("scan_interval", 60)))
        )
        self.host = entry.data["host"]
        self.port = entry.data.get("port", 502)
        self.slave = int(entry.data.get("slave_id", 254))
        self.client = None

    async def _async_update_data(self):
        """Fetch data from ECL 310."""
        try:
            from pymodbus.client import AsyncModbusTcpClient
        except ImportError:
            raise UpdateFailed("Pymodbus library missing")

        if not self.client:
            self.client = AsyncModbusTcpClient(self.host, port=self.port)

        if not self.client.connected:
            await self.client.connect()

        data = {}
        for reg in REGISTER_MAP:
            addr = reg["address"]
            try:
                # Wir rufen die Methode dynamisch auf, um Keyword-Fehler zu vermeiden
                # Pymodbus 3.8.x verlangt 'slave' als Keyword.
                if reg["type"] == "input":
                    res = await self.client.read_input_registers(addr, 1, slave=self.slave)
                else:
                    res = await self.client.read_holding_registers(addr, 1, slave=self.slave)

                if res and not res.isError():
                    raw_val = res.registers[0]
                    # Signed Int16 Decoding
                    decoded_val = struct.unpack('>h', struct.pack('>H', raw_val))[0]
                    data[addr] = decoded_val
                else:
                    _LOGGER.debug("Modbus response error at %s: %s", addr, res)
            except TypeError as e:
                # FALLBACK: Falls 'slave' nicht akzeptiert wird, probieren wir es ohne Keyword (positional)
                _LOGGER.debug("TypeError at %s, trying positional fallback: %s", addr, e)
                try:
                    if reg["type"] == "input":
                        res = await self.client.read_input_registers(addr, 1, self.slave)
                    else:
                        res = await self.client.read_holding_registers(addr, 1, self.slave)
                    
                    if res and not res.isError():
                        data[addr] = struct.unpack('>h', struct.pack('>H', res.registers[0]))[0]
                except Exception as ex:
                    _LOGGER.error("Double failure at %s: %s", addr, ex)
            except Exception as e:
                _LOGGER.error("Communication exception at Addr %s: %s", addr, e)

        if not data:
            raise UpdateFailed("No response from device")
            
        return data

    async def write_register(self, addr, val):
        """Write value to register."""
        if not self.client or not self.client.connected:
            await self.client.connect()
        raw_val = struct.unpack('>H', struct.pack('>h', int(val)))[0]
        try:
            await self.client.write_register(addr, raw_val, slave=self.slave)
        except TypeError:
            await self.client.write_register(addr, raw_val, self.slave)
        await self.async_request_refresh()
