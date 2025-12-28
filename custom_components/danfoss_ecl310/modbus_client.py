import logging
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

class DanfossModbusHub:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._client = AsyncModbusTcpClient(host=host, port=port)
        _LOGGER.debug(f"DanfossModbusHub initialized: {host}:{port}")

    async def connect(self):
        if not self._client.connected:
            await self._client.connect()

    def close(self):
        """Closes the connection (Synchronous in newer Pymodbus versions)."""
        if self._client.connected:
            self._client.close()
            _LOGGER.debug("Modbus connection closed.")

    async def _execute_read(self, func, address, count, slave_id):
        """
        Attempts to call the read function robustly.
        Common error: 'count' must often be passed as a keyword argument.
        """
        # Strategy 1: Modern (Pymodbus v3.x) -> count and slave as keywords
        try:
            return await func(address, count=count, slave=slave_id)
        except TypeError:
            pass

        # Strategy 2: Legacy (Pymodbus v2.x) -> count and unit as keywords
        try:
            return await func(address, count=count, unit=slave_id)
        except TypeError:
            pass

        # Strategy 3: Without Slave-ID (uses Client default, usually 1 or 0)
        # Helps if the library completely rejects slave/unit arguments.
        try:
            return await func(address, count=count)
        except Exception as e:
            # If everything fails, raise the error
            _LOGGER.error(f"All read methods failed for Addr {address}: {e}")
            raise e

    async def read_register(self, address, slave_id, input_type="holding"):
        if not self._client.connected:
            await self.connect()
            
        try:
            # _LOGGER.debug(f"READ REQ -> Addr: {address} | Slave: {slave_id} | Type: {input_type}")
            
            if input_type == "input":
                # read_input_registers(address, count=1, ...)
                result = await self._execute_read(self._client.read_input_registers, address, 1, slave_id)
            else:
                # read_holding_registers(address, count=1, ...)
                result = await self._execute_read(self._client.read_holding_registers, address, 1, slave_id)
            
            if result.isError():
                _LOGGER.error(f"READ ERR -> Addr: {address} | Error: {result}")
                return None
            
            if hasattr(result, 'registers') and len(result.registers) > 0:
                raw_val = result.registers[0]
                final_val = raw_val
                # Handle signed Int16
                if raw_val > 32767:
                    final_val = raw_val - 65536
                return final_val
            else:
                return None
                
        except Exception as e:
            _LOGGER.error(f"READ CRITICAL -> Addr: {address} | {e}")
            return None

    async def write_register(self, address, value, slave_id):
        if not self._client.connected:
            await self.connect()

        try:
            value = int(value)
            _LOGGER.debug(f"WRITE REQ -> Addr: {address} | Val: {value}")
            
            # Use robust logic for writing as well
            try:
                result = await self._client.write_register(address, value, slave=slave_id)
            except TypeError:
                try:
                    result = await self._client.write_register(address, value, unit=slave_id)
                except TypeError:
                    # Fallback without Slave ID
                    result = await self._client.write_register(address, value)
            
            if result.isError():
                _LOGGER.error(f"WRITE ERR -> Addr: {address} | Result: {result}")
                return False
            return True
            
        except Exception as e:
            _LOGGER.error(f"WRITE EXCEPTION -> Addr: {address} | Error: {e}")
            return False
