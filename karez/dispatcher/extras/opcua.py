from karez.config import ConfigEntity
from karez.dispatcher import DispatcherBase
import pandas as pd


class Dispatcher(DispatcherBase):
    @classmethod
    def role_description(cls) -> str:
        return "Reading entities from space address file exported from Matrikon OPC UA Exporter."

    @classmethod
    def config_entities(cls):
        yield from super(Dispatcher, cls).config_entities()
        yield ConfigEntity(
            "space_address_file", "CSV file exported from Matrikon OPC UA Exporter."
        )

    async def load_entities(self) -> list:
        return pd.read_csv(self.config.space_address_file)["NodeId"].tolist()
