import asyncio
import json

from .base import KarezRoleBase


class DispatcherBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(DispatcherBase, self).__init__(*args, **kwargs)
        self.interval = self.config.interval
        self.target = self.config.connector

    def divide_tasks(self, entities):
        batch_size = self.config.get("batch_size", 1)
        for i in range(0, len(entities), batch_size):
            yield entities[i: i + batch_size]

    def _read_entities(self):
        if "entities" in self.config:
            entities = self.config.entities
        elif "entity_file" in self.config:
            with open(self.config.entity_file, "r") as f:
                entities = json.load(f)
        else:
            raise RuntimeError("Cannot load entities.")
        return entities

    async def run(self):
        while True:
            if await self.async_ensure_init():
                entities = self._read_entities()
                for _e in self.divide_tasks(entities):
                    await self.nc.publish(f"karez.connector.{self.target}",
                                          json.dumps(_e).encode("utf-8"))
            await asyncio.sleep(self.interval)
