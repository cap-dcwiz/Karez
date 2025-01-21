from abc import ABC
from karez.config import ConfigEntity, OptionalConfigEntity
from karez.connector import ListenConnectorBase
from uvicorn import Config, Server
from .fast_api_app import FastAPIApp
import asyncio
import yaml
from pathlib import Path

class RestfulListenerConnector(ListenConnectorBase, ABC):
    """
    Connector for listening with fast api
    """

    def __init__(self, *args, **kwargs):
        super(RestfulListenerConnector, self).__init__(*args, **kwargs)
        self.background_task = set()
        self.app = FastAPIApp(self).create_app()
        self._reference = None


    @classmethod
    def role_description(cls) -> str:
        return "Restful Listener using fast api"

    @classmethod
    def config_entities(cls):
        yield from super(RestfulListenerConnector, cls).config_entities()
        yield ConfigEntity("host", "Host of the fastapi.")
        yield OptionalConfigEntity("port", 1883, "Port of the MQTT broker.")
        # reference
        yield ConfigEntity("reference", "Reference file path")
        yield ConfigEntity("tz_infos", "time zone infos")
        yield ConfigEntity("secret_key", "Secret key for JWT")
        yield ConfigEntity("algorithm", "Algorithm for JWT")
        yield ConfigEntity("access_token_expire_minutes", "Access token expiration time in minutes")
        yield ConfigEntity("username", "Username for authentication")
        yield ConfigEntity("bcrypt_hashed_password", "Bcrypt hashed password for authentication")

    @property
    def reference(self):
        if self._reference is None:
            path = Path(self.config.reference)
            self._reference = yaml.safe_load(path.open())
        return self._reference

    async def run(self):
        await self.async_ensure_init()
        if not self.is_listening:
            await self.register_listener()
            self.is_listening = True
        await self.wait_forever()
        loop = asyncio.get_event_loop()
        loop.stop()

    async def register_listener(self):
        config = Config(app=self.app, host="127.0.0.1", port=8000, log_level="info")
        self.server = Server(config)

    async def wait_forever(self):
        await self.server.serve()