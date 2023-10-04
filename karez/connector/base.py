import json
from loguru import logger as logging
from abc import abstractmethod, ABC
from collections.abc import Iterable

from ..config import OptionalConfigEntity
from ..role import RoleBase


class ConnectorBase(RoleBase, ABC):
    """
    Base class of connectors
    """

    TYPE = "connector"

    def __init__(self, *args, **kwargs):
        super(ConnectorBase, self).__init__(*args, **kwargs)

    @classmethod
    def config_entities(cls):
        yield from super(ConnectorBase, cls).config_entities()
        yield OptionalConfigEntity("converter", None, "First Converters to be used.")

    async def postprocess_item(self, item, publish=True, flush=False):
        self.update_meta(item, category=self.get_meta(item, "category", "telemetry"))
        if publish:
            if self.config.converter:
                for converter in self.config.converter:
                    if converter:
                        await self.publish(self.converter_topic(converter), item)
                    else:
                        await self.publish(self.aggregator_topic(item), item)
            else:
                await self.publish(self.aggregator_topic(item), item)
            if flush:
                await self.flush()
        return item


class PullConnectorBase(ConnectorBase):
    """
    Base class of connectors that pull data from external sources.
    """

    async def _subscribe_handler(self, msg):
        payload = json.loads(msg.data.decode("utf-8"))
        for item in await self.process(payload["tasks"]):
            await self.postprocess_item(item, publish=True, flush=False)
        await self.flush()

    async def _try_fetch_data(self, client, entities):
        try:
            res = await self.fetch_data(client, entities)
            return [r for r in res if r is not None]
        except Exception as e:
            logging.error(f"Error in {self.name}: {e}")
            return []

    @abstractmethod
    def create_client(self):
        pass

    @abstractmethod
    async def fetch_data(self, client, entities: Iterable) -> Iterable:
        """
        Fetch data from external sources.
        Args:
            client: a client object that can be used to fetch data, e.g. a https client. Can be None if not needed.
            entities: a list of entities to be fetched. It can be in any format, e.g. a list of ids, a list of dicts, etc.
        Returns:
            a list of fetched data. Each item will be passed to the next converter or aggregator.
        """
        pass

    async def process(self, payload: Iterable) -> Iterable[Iterable]:
        data = []
        async with self.create_client() as client:
            data.extend(await self._try_fetch_data(client, payload))
        return data


class ListenConnectorBase(ConnectorBase, ABC):
    """
    Base class of connectors that listen to external sources. Using this connector does not require a dispatcher.
    """

    def __init__(self, *args, **kwargs):
        super(ListenConnectorBase, self).__init__(*args, **kwargs)
        self.is_listening = False
        self._testing_mode = False
        self.testing_result = None

    async def run(self):
        await self.async_ensure_init()
        if not self.is_listening:
            await self.register_listener()
            self.is_listening = True
        await self.wait_forever()

    async def register_listener(self):
        """
        For example, register a listener to a mqtt topic.
        """
        pass

    @abstractmethod
    def wait_forever(self):
        """
        Start listening.
        """
        pass

    @property
    def testing_mode(self):
        return self._testing_mode

    def finish_testing(self, result):
        self.testing_result = result

    async def process(self, _):
        # For listen connectors, the process method for testing tool only.
        # If possible, it should wait for the connector to receive any message and return the post-processed data.
        self._testing_mode = True
        await self.run()
        return self.testing_result
