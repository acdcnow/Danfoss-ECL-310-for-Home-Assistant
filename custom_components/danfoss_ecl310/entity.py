"""Base entity."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

class ECL310BaseEntity(CoordinatorEntity):
    """Base for all entities."""
    def __init__(self, coordinator, entry, description):
        super().__init__(coordinator)
        self.entry = entry
        self.desc = description
        self._attr_unique_id = f"{entry.entry_id}_{description['key']}"
        self._attr_translation_key = description["key"]
        self._attr_has_entity_name = True
        if "category" in description:
            self._attr_entity_category = description["category"]

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.data.get("name", "ECL 310"),
            manufacturer="Danfoss",
            model="ECL Comfort 310",
        )
