try:
    from homeassistant.const import (CONF_PASSWORD, CONF_SCAN_INTERVAL)
    from homeassistant.helpers import config_validation as cv
    from homeassistant.helpers.event import async_track_time_interval

    from threading import Thread

    from datetime import timedelta
    import logging

    import voluptuous as vol

    # This is needed, it impacts on the name to be called in configurations.yaml
    # Ref: https://developers.home-assistant.io/docs/en/creating_integration_manifest.html
    DOMAIN = 'ho_mobile_account'

    # Setting log
    _LOGGER = logging.getLogger(DOMAIN)
    _LOGGER.setLevel(logging.DEBUG)

    REQUIREMENTS = ['beautifulsoup4']

    CONF_PHONE_NUMBERS = 'phone_numbers'

    # Default scan interval = 15 minutes = 900 seconds
    DEFAULT_SCAN_INTERVAL = timedelta(seconds=900)

    CONFIG_SCHEMA = vol.Schema({
        DOMAIN: vol.Schema({
            vol.Required(CONF_PASSWORD): cv.string,
            vol.Required(CONF_PHONE_NUMBERS): [cv.string],
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
        })
    }, extra=vol.ALLOW_EXTRA)


    # ----------------------------------------------------------------------------------------------------------------------
    #
    # ASYNC SETUP
    #
    # ----------------------------------------------------------------------------------------------------------------------


    async def async_setup(hass, config):

        # create the HoMobile Platform object
        hass.data[DOMAIN] = HoMobilePlatform(hass, config, DOMAIN)

        return True

    # ----------------------------------------------------------------------------------------------------------------------
    #
    # HO.MOBILE PLATFORM
    #
    # ----------------------------------------------------------------------------------------------------------------------


    class HoMobilePlatform(HoMobileCrawler):

        def __init__(self, hass, config, domain):

            self._hass = hass
            self._config = config
            self._domain = domain
            self._name = 'HoMobile'

            super().__init__(
                password = self.config[self.domain][CONF_PASSWORD],
            )

            self._update_status_interval = self.config[self.domain][CONF_SCAN_INTERVAL]

            self.hass.async_create_task(self.async_update_credits())

            self.hass.async_create_task(self.async_start_timer())

        @property
        def hass(self):
            return self._hass

        @property
        def name(self):
            return self._name

        @property
        def domain(self):
            return self._domain

        @property
        def config(self):
            return self._config

        @property
        def update_status_interval(self):
            return self._update_status_interval

        async def async_start_timer(self):

            # This is used to update the status periodically
            self.info(self.name + ' credit will be updated each ' + str(self.update_status_interval))

            # Do not put "self.async_update_credits()", with the parenthesis,
            # otherwise you will pass a Coroutine, not a Coroutine function!
            # and get "Coroutine not allowed to be passed to HassJob"
            # Put "self.async_update_credits" without the parenthesis
            async_track_time_interval(
                self.hass,
                self.async_update_credits,
                self.update_status_interval
            )

        # Do not remove now=None, since when async_track_time_interval()
        # calls async_update_credits(), it passes to the function the time!
        async def async_update_credits(self, now=None):

            self.debug('Updating ' + self._name + ' account credit...')

            threads = []

            for phone_number in self.config[self.domain][CONF_PHONE_NUMBERS]:
                thread = Thread(
                    target=self.get_phone_number_credit,
                    args=[phone_number]
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

        def debug(self, msg):
            _LOGGER.debug(msg)

        def info(self, msg):
            _LOGGER.info(msg)

        def error(self, msg):
            _LOGGER.error(msg)

        def save_info(self, pnk, v, attributes):
            self.hass.states.async_set(self.domain + "." + pnk, v['value'], attributes)

except ModuleNotFoundError:
    print("Execution outside the Home Assistant environment")