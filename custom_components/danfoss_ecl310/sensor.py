from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN, SENSORS_60S, SENSORS_300S, SENSORS_600S

async def async_setup_entry(hass, entry, async_add_entities):
    """Sets up sensors for a specific Config Entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    entities = []

    # Create sensors
    for conf in SENSORS_60S:
        entities.append(DanfossSensor(data["coord_60"], conf, entry))
    for conf in SENSORS_300S:
        entities.append(DanfossSensor(data["coord_300"], conf, entry))
    for conf in SENSORS_600S:
        entities.append(DanfossSensor(data["coord_600"], conf, entry))

    # Create Movement Sensors
    entities.append(DanfossMovementSensor(data["coord_60"], "M1 Movement", "valve_m1_opening", "valve_m1_closing", entry))
    entities.append(DanfossMovementSensor(data["coord_60"], "M2 Movement", "valve_m2_opening", "valve_m2_closing", entry))
    entities.append(DanfossMovementSensor(data["coord_60"], "M3 Movement", "valve_m3_opening", "valve_m3_closing", entry))

    async_add_entities(entities)


class DanfossSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, config, entry):
        super().__init__(coordinator)
        self._config = config
        self._entry = entry
        self._key = config["key"]
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._scale = config.get("scale", 1)
        
        self._attr_device_class = config.get("device_class")
        self._attr_native_unit_of_measurement = config.get("unit")
        self._attr_icon = config.get("icon")
        self._attr_translation_key = config.get("trans_key")
        self._attr_suggested_display_precision = config.get("precision")
        self._attr_entity_category = config.get("entity_category")

        # SYSTEM INFO SENSORS:
        # Diese sind "versteckt" (disabled), da sie nur die Device Info aktualisieren sollen.
        if self._key in ["system_serial_number", "system_app_key", "system_firmware", "system_hardware", "system_modbus_addr"]:
            self._attr_entity_registry_enabled_default = False

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
            configuration_url=f"http://{self._entry.data['host']}",
        )

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._key)
        if val is None:
            return None
        
        # --- UPDATE DEVICE REGISTRY LOGIC ---
        # Sobald Daten kommen, aktualisieren wir die Geräte-Karte oben.

        if self._key == "system_firmware":
            val_int = int(val)
            formatted = f"{val_int >> 8}.{val_int & 0xFF:02d}"
            self._update_device_registry(sw_version=formatted)
            return formatted

        if self._key == "system_hardware":
            val_str = str(val)
            self._update_device_registry(hw_version=f"Rev {val_str}")
            return val_str

        if self._key == "system_serial_number":
            val_str = str(val)
            self._update_device_registry(serial_number=val_str)
            return val_str

        if self._key == "system_app_key":
            val_str = str(val)
            # App Key gibt es nicht als Feld, wir hängen es ans Modell an
            self._update_device_registry(model_suffix=f"Key: {val_str}")
            return val_str

        if self._key == "system_modbus_addr":
            val_str = str(val)
            # Modbus Addr gibt es nicht als Feld, wir hängen es ans Modell an
            self._update_device_registry(model_suffix=f"Addr: {val_str}")
            return val_str

        # --- STANDARD SCALING ---
        if self._scale != 1:
            return float(val) * self._scale
        
        if self._attr_translation_key:
            return str(val)
            
        return val

    def _update_device_registry(self, sw_version=None, hw_version=None, serial_number=None, model_suffix=None):
        """Helper: Schreibt Infos direkt in die HA Device Registry."""
        dev_reg = dr.async_get(self.hass)
        device = dev_reg.async_get_device(identifiers={(DOMAIN, self._entry.entry_id)})
        
        if not device:
            return

        update_data = {}
        
        # Standard Felder
        if sw_version:
            update_data["sw_version"] = sw_version
        if hw_version:
            update_data["hw_version"] = hw_version
        if serial_number:
            update_data["serial_number"] = serial_number
            
        # Modell Erweiterung (für App Key und Addr)
        if model_suffix:
            current_model = device.model or "ECL 310"
            # Verhindern, dass wir es doppelt anhängen
            if model_suffix not in current_model:
                update_data["model"] = f"{current_model} | {model_suffix}"

        if update_data:
            dev_reg.async_update_device(device.id, **update_data)


class DanfossMovementSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, name, open_key, close_key, entry):
        super().__init__(coordinator)
        self._open_key = open_key
        self._close_key = close_key
        self._entry = entry
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_move_{open_key}"
        self._attr_translation_key = "movement_state"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.title,
            manufacturer="Danfoss",
            model="ECL 310",
        )

    @property
    def native_value(self):
        is_opening = self.coordinator.data.get(self._open_key) == 1
        is_closing = self.coordinator.data.get(self._close_key) == 1
        if is_opening: return "opening"
        elif is_closing: return "closing"
        return "stop"