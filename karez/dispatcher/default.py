from .base import DispatcherBase
from ..config import OptionalConfigEntity


class DefaultDispatcher(DispatcherBase):
    @classmethod
    def role_description(cls):
        return "Default dispatcher."

    @classmethod
    def config_entities(cls):
        yield from super(DefaultDispatcher, cls).config_entities()
        yield OptionalConfigEntity("entities", None, "Entities")
        yield OptionalConfigEntity("entity_file", None, "Entity file")

    def load_entities(self):
        if self.is_configured("entities"):
            entities = self.config.entities
        elif self.is_configured("entity_file"):
            with open(self.config.entity_file, "r") as f:
                entities = json.load(f)
        else:
            raise RuntimeError("Cannot load entities.")
        return entities
