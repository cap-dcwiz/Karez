import asyncio
import json
import logging
from abc import abstractmethod
from copy import copy

from httpx import AsyncClient, Limits

from .base import KarezRoleBase, CHECKING_STATUS_INTERVAL


class ConnectorBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(ConnectorBase, self).__init__(*args, **kwargs)
        self.converter = self.config.get("converter", None)


class PullConnectorBase(ConnectorBase):
    async def _subscribe_handler(self, msg):
        entities = json.loads(msg.data.decode("utf-8"))
        for item in await self.pull(entities):
            converter = copy(self.converter)
            if self.converter:
                next_step = converter.pop(0)
                item["_next"] = converter
                topic = f"karez.converter.{next_step}"
                reply = f"karez.telemetry.{self.name}"
            else:
                topic = f"karez.telemetry.{self.name}"
                reply = ""
            await self.nc.publish(topic, json.dumps(item).encode("utf-8"), reply=reply)
        await self.nc.flush()

    async def run(self):
        while True:
            if not (self.nc and self.nc.is_connected and self.sub):
                await self.subscribe(f"connector.{self.name}")
            await asyncio.sleep(CHECKING_STATUS_INTERVAL)

    @abstractmethod
    async def pull(self, entities):
        pass


class RestfulConnectorForTelemetries(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(RestfulConnectorForTelemetries, self).__init__(*args, **kwargs)
        self.base_url = self.config.base_url

    async def _try_fetch_data(self, client, entities):
        try:
            res = await self.fetch_data(client, entities)
            return [r for r in res if r is not None]
        except Exception as e:
            logging.error(str(e))
            return []

    @abstractmethod
    async def fetch_data(self, client, entities):
        pass

    def _create_client(self):
        security_conf = self.config.security
        auth = None
        if security_conf:
            if security_conf.type == "basic":
                auth = security_conf.username, security_conf.password
            else:
                raise NotImplementedError
        client = AsyncClient(base_url=self.base_url,
                             auth=auth,
                             limits=Limits(max_keepalive_connections=10,
                                           max_connections=20),
                             **self.config.connection_args or {},
                             )
        return client

    async def pull(self, entities):
        data = []
        async with self._create_client() as client:
            data.extend(await self._try_fetch_data(client, entities))
        return data
