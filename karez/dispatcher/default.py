from .base import DispatcherBase


class DefaultDispatcher(DispatcherBase):
    @classmethod
    def role_description(cls):
        return "Default dispatcher."

    def divide_tasks(self, entities: list) -> list[list]:
        batch_size = self.config.batch_size
        for i in range(0, len(entities), batch_size):
            yield entities[i: i + batch_size]