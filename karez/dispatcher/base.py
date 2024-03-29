import asyncio
from abc import abstractmethod
from collections.abc import Iterable
from random import uniform, shuffle
from typing import Generator

from karez.config import ConfigEntity, OptionalConfigEntity
from karez.role import RoleBase

DISPATCH_MODE_BURST = "burst"
DISPATCH_MODE_RAND = "rand"
DISPATCH_MODE_EVEN = "even"
DISPATCH_MODE_RAND_MIXED = "rand_mixed"
DISPATCH_MODE_EVEN_MIXED = "even_mixed"


class DispatcherBase(RoleBase):
    """
    Base class of dispatchers. A dispatcher is a role that dispatches tasks to connectors.
    """

    TYPE = "dispatcher"

    def __init__(self, *args, **kwargs):
        super(DispatcherBase, self).__init__(*args, **kwargs)
        self.interval = self.config.interval
        self.target = self.config.connector

    @classmethod
    def config_entities(cls):
        yield from super(DispatcherBase, cls).config_entities()
        yield ConfigEntity("interval", "Collection interval.")
        yield ConfigEntity("connector", "Connector to use.")
        yield OptionalConfigEntity("batch_size", 1, "Batch Size")
        yield OptionalConfigEntity(
            "mode",
            DISPATCH_MODE_BURST,
            "Task dispatching mode. "
            "1) burst: all at once. "
            "2) rand: randomised time inside the interval. "
            "3) even: evenly distributed inside the interval. "
            "4) rand_mixed: first round burst, then rand. "
            "5) even_mixed: first round burst, then even. ",
        )
        yield OptionalConfigEntity(
            "shuffle", False, "Shuffle the list of batches before dispatching?"
        )

    def divide_tasks(self, entities: list) -> Generator[dict, None, None]:
        batch_size = self.config.batch_size
        for i in range(0, len(entities), batch_size):
            yield dict(tasks=entities[i : i + batch_size])

    @abstractmethod
    async def load_entities(self) -> list:
        """
        Load entities from somewhere. It can be a local file, a database, or a remote API.
        Returns:
            A list of entities. An entity can be anything that can be passed to a connector, for example, a device ID.
        """
        pass

    async def process(self, _) -> Iterable:
        return self.divide_tasks(await self.load_entities())

    def _decide_wait_time(self, entity_list, is_first_time):
        if entity_list:
            sub_interval = self.config.interval / len(entity_list)
        else:
            sub_interval = NotImplemented
        for i, entities in enumerate(entity_list):
            mode = self.config.mode.lower()
            if mode == DISPATCH_MODE_BURST:
                wait_time = 0
            elif mode == DISPATCH_MODE_RAND:
                wait_time = uniform(0, self.config.interval)
            elif mode == DISPATCH_MODE_EVEN:
                wait_time = sub_interval * i
            elif mode in (DISPATCH_MODE_EVEN_MIXED, DISPATCH_MODE_RAND_MIXED):
                if is_first_time:
                    wait_time = 0
                elif mode == DISPATCH_MODE_EVEN_MIXED:
                    wait_time = sub_interval * i
                elif mode == DISPATCH_MODE_RAND_MIXED:
                    wait_time = uniform(0, self.config.interval)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
            yield wait_time, entities

    async def run(self):
        topic = self.connector_topic(self.target)

        _is_first_time = True
        while True:
            if await self.async_ensure_init():
                try:
                    entity_list = list(await self.process(None))
                    if self.config.shuffle:
                        shuffle(entity_list)
                except Exception as e:
                    self.log_exception(e)
                    entity_list = []
                for wait_time, entities in self._decide_wait_time(
                    entity_list, _is_first_time
                ):
                    asyncio.create_task(
                        self.wait_and_publish(topic, entities, wait_time=wait_time)
                    )
            await asyncio.sleep(self.interval)
            _is_first_time = False

    async def wait_and_publish(self, topic, content, wait_time=0.0):
        await asyncio.sleep(wait_time)
        await self.publish(topic, content)
        self.log("info", f"{len(content)} tasks published: {str(content)[:36]}...")
