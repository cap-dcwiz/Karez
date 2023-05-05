import pandas as pd

from karez.config import ConfigEntity
from karez.dispatcher import DispatcherBase
from karez.utils import generator_to_list


class Dispatcher(DispatcherBase):
    @classmethod
    def role_description(cls) -> str:
        return "Reading entities from a modbus data point list file."

    @classmethod
    def config_entities(cls):
        yield from super(Dispatcher, cls).config_entities()
        yield ConfigEntity("file", "CSV file containing modbus point information.")

    @generator_to_list
    async def load_entities(self) -> list:
        for _, row in pd.read_csv(self.config.file).iterrows():
            yield row.to_dict()
