import logging
_LOGGER = logging.getLogger(__name__)

from .const import (
    SENSOR,
    DOMAIN,
    CONF_PHONE_NUMBER,
    CONF_PASSWORD,
)

try:
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry

    from .sensor import async_setup_entry as async_setup_sensors
    from .ho_mobile_device import HoMobileDevice
    from .coordinator import HoMobileCoordinator

    async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:

        phone_number = config_entry.data[CONF_PHONE_NUMBER]
        password = config_entry.data[CONF_PASSWORD]

        device = HoMobileDevice(params={
            CONF_PASSWORD: password,
            CONF_PHONE_NUMBER: phone_number
        })

        # Inizializza il coordinatore
        coordinator = HoMobileCoordinator(hass, device)

        # Memorizza il coordinatore nel registro dei dati di Home Assistant
        hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

        await coordinator.async_config_entry_first_refresh()

        await hass.config_entries.async_forward_entry_setups(config_entry, [SENSOR])

        return True


    async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
        await hass.config_entries.async_forward_entry_unload(config_entry, SENSOR)
        hass.data[DOMAIN].pop(config_entry.entry_id)

        return True

except ModuleNotFoundError:
    print("Execution outside the Home Assistant environment")