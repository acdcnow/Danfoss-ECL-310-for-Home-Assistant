"""DataUpdateCoordinator with Keyword-Safe Modbus Calls."""
import asyncio
import logging
import struct
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, REGISTER_MAP

_LOGGER = logging.getLogger(__name__)

class ECL310Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(
            hass, _LOGGER, name=DOMAIN, 
            update_interval=timedelta(seconds=entry.options.get("scan_interval", entry.data.get("scan_interval", 60)))
        )
        self.host = entry.data["host"]
        self.slave = int(entry.data.get("slave_id", 254))
        self.client = None

    async def _async_update_data(self):
        from pymodbus.client import AsyncModbusTcpClient
        if not self.client:
            self.client = AsyncModbusTcpClient(self.host, port=502)

        if not self.client.connected:
            await self.client.connect()

        data = {}
        for reg in REGISTER_MAP:
            addr = reg["address"]
            try:
                # Use positional fallback to avoid "unexpected keyword argument slave"
                if reg["type"] == "input":
                    res = await self.client.read_input_registers(addr, 1, slave=self.slave)
                else:
                    res = await self.client.read_holding_registers(addr, 1, slave=self.slave)
                
                if res and not res.isError():
                    raw = res.registers[0]
                    # Direct Struct Unpacking (Signed Int16)
                    data[addr] = struct.unpack('>h', struct.pack('>H', raw))[0]
            except Exception as e:
                _LOGGER.error("Modbus error at %s: %s", addr, e)
        return data

    async def write_register(self, addr, val):
        if not self.client.connected: await self.client.connect()
        raw = struct.unpack('>H', struct.pack('>h', int(val)))[0]
        await self.client.write_register(addr, raw, slave=self.slave)
        await self.async_request_refresh()
