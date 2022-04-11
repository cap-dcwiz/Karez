import asyncio
import json
import logging
from abc import abstractmethod, ABC
from collections.abc import Iterable
from copy import copy

from ..config import OptionalConfigEntity
from ..role import RoleBase, CHECKING_STATUS_INTERVAL


class ConnectorBase(RoleBase, ABC):
    """
    Base class of connectors
    """
    def __init__(self, *args, **kwargs):
        super(ConnectorBase, self).__init__(*args, **kwargs)
        self.converter = self.config.converter

    @classmethod
    def config_entities(cls):
        yield from super(ConnectorBase, cls).config_entities()
        yield OptionalConfigEntity("converter", None, "Converters to be used.")

    def reply_topic(self, point_type="telemetry"):
        return f"karez.{point_type}.{self.name}"


class PullConnectorBase(ConnectorBase):
    TYPE = "connector"

    async def _subscribe_handler(self, msg):
        payload = json.loads(msg.data.decode("utf-8"))
        for item in await self.process(payload):
            converter = copy(self.converter)
            if self.converter:
                next_step = converter.pop(0)
                item["_next"] = converter
                topic = self.converter_topic(next_step)
                reply = self.reply_topic("telemetry")
            else:
                topic = self.reply_topic("telemetry")
                reply = ""
            await self.nc.publish(topic, json.dumps(item).encode("utf-8"), reply=reply)
        await self.nc.flush()

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
    async def fetch_data(self, client, entities: Iterable) -> Iterable:
        pass

    async def process(self, payload: Iterable) -> Iterable[Iterable]:
        data = []
        async with self.create_client() as client:
            data.extend(await self._try_fetch_data(client, payload))
        return data
