import logging
from abc import abstractmethod
from collections.abc import Iterable

import nats

from .config import ConfigurableBase, OptionalConfigEntity, ConfigEntity, ConfigEntityBase

CHECKING_STATUS_INTERVAL = 10
CONNECTOR_MODE_WORKER = 0
CONNECTOR_MODE_CONTROLLER = 1


class RoleBase(ConfigurableBase):
    TYPE = NotImplemented

    def __init__(self, config, nats_addr="nats://localhost:4222"):
        super(RoleBase, self).__init__(config)
        self.name = self.config.name
        self.nc_addr = nats_addr
        self.nc = None
        self.sub = None

    @classmethod
    def config_entities(cls) -> Iterable[ConfigEntityBase]:
        yield from super(RoleBase, cls).config_entities()
        conf_type = ConfigEntity("type", "Type of the plugin.")
        yield OptionalConfigEntity("name", conf_type, "Name of the plugin.")
        yield conf_type

    @classmethod
    @abstractmethod
    def role_description(cls) -> str:
        pass

    @property
    def subscribe_topic(self):
        return f"karez.{self.TYPE}.{self.name}"

    @property
    def subscribe_queue(self):
        return f"{self.TYPE}.{self.name}"

    @staticmethod
    def connector_topic(name):
        return f"karez.connector.{name}"

    @staticmethod
    def converter_topic(name):
        return f"karez.converter.{name}"

    async def error_cb(self, e):
        logging.error(f'{self.name}: {str(e)}!')

    async def disconnected_cb(self):
        logging.warning(f'{self.name}: Got disconnected!')
        self.sub = None

    async def reconnected_cb(self):
        logging.info(f'{self.name}: Got reconnected to {self.nc.connected_url.netloc}')

    async def async_ensure_init(self):
        conn_options = dict(
            servers=self.nc_addr,
            name=self.name,
            error_cb=self.error_cb,
            disconnected_cb=self.disconnected_cb,
            reconnected_cb=self.reconnected_cb
        )
        try:
            if not self.nc:
                self.nc = await nats.connect(**conn_options)
            elif not self.nc.is_connected:
                await self.nc.connect(**conn_options)
        except Exception as e:
            logging.error(str(e))
        return self.nc and self.nc.is_connected

    async def _subscribe_handler(self, msg):
        pass

    async def subscribe(self):
        if await self.async_ensure_init():
            if self.sub:
                await self.sub.unsubscribe()
                self.sub = None
            print(self.name, self.subscribe_topic, self.subscribe_queue)
            self.sub = await self.nc.subscribe(self.subscribe_topic,
                                               queue=self.subscribe_queue,
                                               cb=self._subscribe_handler)

