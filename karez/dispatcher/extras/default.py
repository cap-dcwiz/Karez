import json

from ...config import OptionalConfigEntity
from ..base import DispatcherBase


class Dispatcher(DispatcherBase):
    @classmethod
    def role_description(cls):
        return "Default dispatcher."

    @classmethod
    def config_entities(cls):
        yield from super(Dispatcher, cls).config_entities()
        yield OptionalConfigEntity("entities", None, "Entities")
        yield OptionalConfigEntity("entity_file", None, "Entity file")

    async def load_entities(self):
        if self.is_configured("entities"):
            entities = self.config.entities
        elif self.is_configured("entity_file"):
            with open(self.config.entity_file, "r") as f:
                entities = json.load(f)
        else:
            raise RuntimeError("Cannot load entities.")
        return entities
