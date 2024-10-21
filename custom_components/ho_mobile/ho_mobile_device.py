from .ho_mobile import HoMobile

from .const import *

import logging
_LOGGER = logging.getLogger(__name__)


class HoMobileDevice(HoMobile):

    def debug(self, msg):
        _LOGGER.debug(msg)

    def info(self, msg):
        _LOGGER.info(msg)

    def warning(self, msg):
        _LOGGER.warning(msg)

    def error(self, msg):
        _LOGGER.error(msg)

    async def get_id(self):
        name = await self.get_name()
        return name.lower().replace(" ","_").replace("-","_")

    async def get_name(self):
        return f"{DEVICE_MANUFACTURER} {self.phone_number}"

    async def get_title(self):
        return await self.get_name()
