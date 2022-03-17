import logging

import nats

CHECKING_STATUS_INTERVAL = 10
CONNECTOR_MODE_WORKER = 0
CONNECTOR_MODE_CONTROLLER = 1


class KarezRoleBase:
    def __init__(self, config, nats_addr="nats://localhost:4222"):
        self.config = config
        self.name = config.get("name", config.type)
        self.nc_addr = nats_addr
        self.nc = None
        self.sub = None

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

    async def subscribe(self, name):
        if await self.async_ensure_init():
            if self.sub:
                await self.sub.unsubscribe()
                self.sub = None
            self.sub = await self.nc.subscribe(f"karez.{name}",
                                               queue=name,
                                               cb=self._subscribe_handler)

