import logging
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

class DanfossModbusHub:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._client = AsyncModbusTcpClient(host=host, port=port)
        _LOGGER.info(f"DanfossModbusHub initialized (Async): {host}:{port}")

    async def connect(self):
        """Connect to the Modbus device."""
        if not self._client.connected:
            await self._client.connect()

    def close(self):
        """Closes the connection."""
        if self._client.connected:
            self._client.close()
            _LOGGER.debug("Modbus connection closed.")

    async def _execute_read(self, func, address, count, slave_id):
        """
        Versucht robust zu lesen. Probiert nacheinander slave, unit und ohne ID.
        """
        # Versuch 1: Modern (Pymodbus v3.x) -> slave als Keyword
        try:
            return await func(address, count=count, slave=slave_id)
        except TypeError:
            pass

        # Versuch 2: Legacy (Pymodbus v2.x) -> unit als Keyword
        try:
            return await func(address, count=count, unit=slave_id)
        except TypeError:
            pass

        # Versuch 3: Ohne ID (Fallback)
        try:
            return await func(address, count=count)
        except Exception as e:
            # Wenn alles fehlschlägt, Fehler werfen
            raise e

    async def read_register(self, address, slave_id, input_type="holding"):
        """Liest ein Register aus."""
        if not self._client.connected:
            await self.connect()
            
        try:
            if input_type == "input":
                result = await self._execute_read(self._client.read_input_registers, address, 1, slave_id)
            else:
                result = await self._execute_read(self._client.read_holding_registers, address, 1, slave_id)
            
            if result.isError():
                _LOGGER.debug(f"Read Error on {address}: {result}")
                return None
            
            # Prüfen ob Daten da sind
            if hasattr(result, 'registers') and len(result.registers) > 0:
                raw_val = result.registers[0]
                final_val = raw_val
                
                # Vorzeichen behandeln (Signed 16-bit)
                # Alles über 32767 ist negativ (z.B. 65530 -> -6)
                if raw_val > 32767:
                    final_val = raw_val - 65536
                return final_val
            else:
                return None
                
        except Exception as e:
            _LOGGER.error(f"Read Exception on {address}: {e}")
            return None

    async def write_register(self, address, value, slave_id):
        """Schreibt ein Register."""
        if not self._client.connected:
            await self.connect()

        try:
            value = int(value)
            
            # Negative Werte umrechnen für Modbus (z.B. -10 -> 65526)
            if value < 0:
                value = value + 65536
            
            # Auch beim Schreiben nutzen wir die robuste Logik
            try:
                result = await self._client.write_register(address, value, slave=slave_id)
            except TypeError:
                try:
                    result = await self._client.write_register(address, value, unit=slave_id)
                except TypeError:
                    result = await self._client.write_register(address, value)
            
            if result.isError():
                _LOGGER.error(f"Write Error on {address}: {result}")
                return False
            
            _LOGGER.info(f"Write Success: {address} = {value}")
            return True
            
        except Exception as e:
            _LOGGER.error(f"Write Exception on {address}: {e}")
            return False