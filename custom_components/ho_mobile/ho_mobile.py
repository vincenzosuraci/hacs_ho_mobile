import asyncio
import aiohttp
import async_timeout
import time
from datetime import datetime
from .const import CONF_PHONE_NUMBER, CONF_PASSWORD, SENSOR_THRESHOLD, SENSOR_RESIDUAL, SENSOR_RENEWAL

# ----------------------------------------------------------------------------------------------------------------------
#
# 1nce
#
# ----------------------------------------------------------------------------------------------------------------------

class HoMobile:

    # Minimo tempo che deve trascorre tra due interrogazioni successive al cloud
    MIN_INTERVAL_S = 2

    def __init__(
        self,
        params = {}
    ):
        self._phone_number = params.get(CONF_PHONE_NUMBER)
        self._password = params.get(CONF_PASSWORD)

        self._session = None
        self._last_update_timestamp = None

        self._account_id = None
        self._product_id = None

        self._sim_data = None



    @property
    def phone_number(self):
        return self._phone_number

    def debug(self, msg):
        print(msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    async def fetch_data(self):
        return await self._get_sim_data()

    async def _get_sim_data(self):

        if self._last_update_timestamp is None or time.time() > self._last_update_timestamp + self.MIN_INTERVAL_S:

            self._last_update_timestamp = time.time()

            if await self._step_1_landing_page():
                if await self._step_2_account_id():
                    if await self._step_3_do_login():
                        if await self._step_4_get_catalog_info_activation():
                            self._sim_data = await self._step_5_get_sim_data()

        return self._sim_data

    async def _step_1_landing_page(self):

        url = "https://www.ho-mobile.it/"

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.get(url) as response:
                    if response.status == 200:
                        self.debug("Step 1 - Landing page loaded")
                        return True
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 102
                        await self._async_close_session()
                        raise HoMobileError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 101
            await self._async_close_session()
            raise HoMobileError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 100
            await self._async_close_session()
            raise HoMobileError(msg, code)

        return False

    async def _step_2_account_id(self):

        # login url
        url = 'https://www.ho-mobile.it/leanfe/restAPI/LoginService/checkAccount'

        # set POST https params
        json = {
            "email": None,
            "phoneNumber": self._phone_number,
            "channel": "WEB"
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "HomeAssistant",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.ho-mobile.it/",
        }

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.post(url, json=json, headers=headers) as response:
                    if response.status == 200:
                        json = await response.json()
                        status = json["operationStatus"]["status"]
                        if status != "OK":
                            diagnostic = json['operationStatus']['diagnostic']
                            error_code = json['operationStatus']['errorCode']
                            msg = (f"Phone number {str(self._phone_number)} "
                                   f"errorCode: {error_code} - "
                                   f"diagnostic: {diagnostic}")
                            self.debug(msg)
                            code = 203
                            await self._async_close_session()
                            raise HoMobileError(msg, code)
                        else:
                            self.debug("Step 2 - Account enabled")
                            return True
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 202
                        await self._async_close_session()
                        raise HoMobileError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 201
            await self._async_close_session()
            raise HoMobileError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 200
            await self._async_close_session()
            raise HoMobileError(msg, code)

        return False

    async def _step_3_do_login(self):

        # login url
        url = 'https://www.ho-mobile.it/leanfe/restAPI/LoginService/login'

        # set POST https params
        json = {
            'accountId': self._account_id,
            'email': None,
            'phoneNumber': self._phone_number,
            'password': self._password,
            'channel': "WEB",
            'isRememberMe': False
        }

        headers = {
            'Referer': 'https://www.ho-mobile.it/',
            'Content-Type': 'application/json'
        }

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.post(url, json=json, headers=headers) as response:
                    if response.status == 200:
                        self.debug("Step 3 - Login successful")
                        return True
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 302
                        await self._async_close_session()
                        raise HoMobileError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 301
            await self._async_close_session()
            raise HoMobileError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 300
            await self._async_close_session()
            raise HoMobileError(msg, code)

        return False

    async def _step_4_get_catalog_info_activation(self):

        # login url
        url = 'https://www.ho-mobile.it/leanfe/restAPI/CatalogInfoactivationService/getCatalogInfoactivation'

        # set POST https params
        json = {
            "channel": "WEB",
            "phoneNumber": self._phone_number
        }

        headers = {
            'Referer': 'https://www.ho-mobile.it/',
            'Content-Type': 'application/json'
        }

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.post(url, json=json, headers=headers) as response:
                    if response.status == 200:
                        self.debug("Step 4 - Product id retrieved")
                        json = await response.json()
                        self._product_id = json['activeOffer']['productList'][0]['productId']
                        return True
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 402
                        await self._async_close_session()
                        raise HoMobileError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 401
            await self._async_close_session()
            raise HoMobileError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 400
            await self._async_close_session()
            raise HoMobileError(msg, code)

        return False

    async def _step_5_get_sim_data(self):

        # login url
        url = 'https://www.ho-mobile.it/leanfe/restAPI/CountersService/getCounters'

        # set POST https params
        json = {
            "channel": "WEB",
            "phoneNumber": self._phone_number,
            "productId": self._product_id
        }

        headers = {
            'Referer': 'https://www.ho-mobile.it/',
            'Content-Type': 'application/json'
        }

        try:
            async with async_timeout.timeout(10):  # Timeout di 10 secondi
                await self._async_init_session()
                async with self._session.post(url, json=json, headers=headers) as response:
                    if response.status == 200:
                        json = await response.json()
                        residual = None
                        threshold = None
                        for item in json['countersList'][0]['countersDetailsList']:
                            uom = item['residualUnit']
                            if uom in ['GB', 'MB']:
                                # ------------------------------------------------------------------------------
                                # Recupero dei M/Gbyte residui
                                # ------------------------------------------------------------------------------
                                residual = item['residual']
                                # ------------------------------------------------------------------------------
                                # Recupero dei M/Gbyte totali
                                # ------------------------------------------------------------------------------
                                threshold = item['threshold']

                        # Current Epoch Unix Timestamp (ad es. 1698184800000)
                        renewal_ts = json['countersList'][0]['productNextRenewalDate'] / 1000

                        # Converte il timestamp in un oggetto datetime
                        renewal = datetime.fromtimestamp(renewal_ts).date()

                        await self._async_close_session()

                        if residual is not None and threshold is not None and renewal is not None:
                            data = {
                                SENSOR_THRESHOLD: threshold,
                                SENSOR_RESIDUAL: residual,
                                SENSOR_RENEWAL: renewal
                            }
                            self.debug(f"Step 5 - Data retreived: {data}")
                            return data
                        else:
                            msg = f"Residual: {residual}, Threshold: {threshold}, Renewal: {renewal}"
                            code = 503
                            raise HoMobileError(msg, code)
                    else:
                        msg = f"Request error {url}: {response.status}"
                        code = 502
                        await self._async_close_session()
                        raise HoMobileError(msg, code)
        except aiohttp.ClientError as err:
            msg = f"Connection error {url}: {err}"
            code = 501
            await self._async_close_session()
            raise HoMobileError(msg, code)
        except asyncio.TimeoutError:
            msg = f"Connection timeout {url}"
            code = 500
            await self._async_close_session()
            raise HoMobileError(msg, code)

        return None

    async def test_connection(self):
        data = await self.fetch_data()
        return data is not None

    # ------------------------------------------------------------------------------------------------------------------
    # Session related methods
    # ------------------------------------------------------------------------------------------------------------------

    async def _async_init_session(self):
        """ Init session """
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def _async_close_session(self):
        """ Close session """
        if self._session:
            await self._session.close()
            self._session = None


class HoMobileAuthError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[Ho-mobile Authentication Error {self.code}]: {self.args[0]}"


class HoMobileError(Exception):
    """Eccezione personalizzata che accetta un messaggio e un codice di errore."""

    def __init__(self, message, code):
        # Chiama il costruttore della classe base (Exception) con il messaggio di errore
        super().__init__(message)
        self.code = code

    def __str__(self):
        # Ritorna una rappresentazione stringa dell'errore, includendo il codice
        return f"[Ho-mobile Error {self.code}]: {self.args[0]}"