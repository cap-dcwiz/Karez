import asyncio
import json
import logging
from abc import abstractmethod

from httpx import AsyncClient, Limits

from .common import KarezRoleBase


class ConnectorBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(ConnectorBase, self).__init__(*args, **kwargs)
        self.converter = self.config.get("converter", None)


class PullConnectorBase(ConnectorBase):
    def __init__(self, *args, **kwargs):
        super(PullConnectorBase, self).__init__(*args, **kwargs)
        self.interval = self.config.interval

    async def run(self):
        await self.async_init()
        while True:
            count = 0
            for item in await self.pull():
                if self.converter:
                    topic = f"karez.converter.{self.converter}"
                    reply = f"karez.telemetry.{self.name}"
                else:
                    topic = f"karez.telemetry.{self.name}"
                    reply = ""
                await self.nc.publish(topic, json.dumps(item).encode("utf-8"), reply=reply)
                count += 1
            logging.info(f"Connector[{self.name}]: publishing {count} items")
            await asyncio.sleep(self.interval)

    @abstractmethod
    def pull(self):
        pass


class RestfulConnectorForTelemetries(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(RestfulConnectorForTelemetries, self).__init__(*args, **kwargs)
        self.base_url = self.config.base_url

    def partition_devices(self, devices):
        return [devices]

    @abstractmethod
    async def fetch_data(self, client, devices):
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

    async def pull(self):
        data = []
        async with self._create_client() as client:
            tasks = [self.fetch_data(client, group)
                     for group in self.partition_devices(self.config.devices)]
            for res in await asyncio.gather(*tasks):
                data.extend(res)
        return data
