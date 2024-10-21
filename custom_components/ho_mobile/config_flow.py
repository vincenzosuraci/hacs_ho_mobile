import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow, CONN_CLASS_CLOUD_POLL
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_PHONE_NUMBER, CONF_PASSWORD
from .ho_mobile_device import HoMobileDevice

import logging
_LOGGER = logging.getLogger(__name__)

class HoMobileConfigFlow(ConfigFlow, domain=DOMAIN):
    """Gestisce il flusso di configurazione per la SIM 1nce"""

    VERSION = 1
    CONNECTION_CLASS = CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Primo passo: richiedi username, password dell'account e iccid della SIM"""
        errors = {}

        if user_input is not None:

            # Verifica se l'input è valido (opzionale: potresti fare un controllo sulla connessione qui)
            phone_number = user_input[CONF_PHONE_NUMBER]
            password = user_input[CONF_PASSWORD]

            if phone_number and password:

                device = HoMobileDevice(params={
                    CONF_PASSWORD: password,
                    CONF_PHONE_NUMBER: phone_number
                })

                try:

                    if await device.test_connection():

                        data = {
                            CONF_PHONE_NUMBER: phone_number,
                            CONF_PASSWORD: password
                        }

                        title = await device.get_title()

                        return self.async_create_entry(
                            title=title,
                            data=data
                        )

                    else:
                        errors["base"] = "Connection test failed"

                except Exception as err:
                    errors["base"] = f"Cannot connect {err}"

            else:
                errors["base"] = "Missing input"

        # Se non ci sono input o ci sono errori, mostra il form
        data_schema = vol.Schema({
            vol.Required(CONF_PHONE_NUMBER): cv.string,
            vol.Required(CONF_PASSWORD): cv.string,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HoMobileOptionsFlow(config_entry)

class HoMobileOptionsFlow(OptionsFlow):
    """Gestione delle opzioni aggiuntive per ZyXEL Modem."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Gestisci le opzioni aggiuntive."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Mostra il form delle opzioni."""
        data_schema = vol.Schema({
            vol.Optional(CONF_PHONE_NUMBER, default=self.config_entry.data.get(CONF_PHONE_NUMBER)): cv.string,
            vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD)): cv.string,
        })

        if user_input is not None:
            self.hass.config_entries.async_update_entry(self.config_entry, data=user_input)
            return self.async_create_entry(title="", data=None)

        return self.async_show_form(step_id="user", data_schema=data_schema)