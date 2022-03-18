import asyncio
import json
import logging
from abc import abstractmethod
from copy import copy

from ..base import KarezRoleBase, CHECKING_STATUS_INTERVAL


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

    async def _try_fetch_data(self, client, entities):
        try:
            res = await self.fetch_data(client, entities)
            return [r for r in res if r is not None]
        except Exception as e:
            logging.error(str(e))
            return []

    @abstractmethod
    def create_client(self):
        pass

    @abstractmethod
    async def fetch_data(self, client, entities):
        pass

    async def pull(self, entities):
        data = []
        async with self.create_client() as client:
            data.extend(await self._try_fetch_data(client, entities))
        return data
