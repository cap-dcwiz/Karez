import json
import logging
from abc import abstractmethod, ABC
from collections.abc import Iterable

from ..config import OptionalConfigEntity
from ..role import RoleBase


class ConnectorBase(RoleBase, ABC):
    """
    Base class of connectors
    """

    def __init__(self, *args, **kwargs):
        super(ConnectorBase, self).__init__(*args, **kwargs)

    @classmethod
    def config_entities(cls):
        yield from super(ConnectorBase, cls).config_entities()
        yield OptionalConfigEntity("converter", None, "First Converters to be used.")


class PullConnectorBase(ConnectorBase):
    TYPE = "connector"

    async def _subscribe_handler(self, msg):
        payload = json.loads(msg.data.decode("utf-8"))
        for item in await self.process(payload["tasks"]):
            self.update_meta(item, category=self.get_meta(item, "category", "telemetry"))
            if self.config.converter:
                for converter in self.config.converter:
                    if converter:
                        await self.publish(self.converter_topic(converter), item)
                    else:
                        await self.publish(self.aggregator_topic(item), item)
            else:
                await self.publish(self.aggregator_topic(item), item)
        await self.flush()

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
