import pandas as pd

from karez.config import ConfigEntity
from karez.dispatcher import DispatcherBase
from karez.utils import generator_to_list


class Dispatcher(DispatcherBase):
    @classmethod
    def role_description(cls) -> str:
        return "Reading entities from a eaton device/monitor attributes list file."

    @classmethod
    def config_entities(cls):
        yield from super(Dispatcher, cls).config_entities()
        yield ConfigEntity("file", "CSV file containing data point information.")

    @generator_to_list
    def load_entities(self):
        df = pd.read_csv(self.config.file)
        for dev_id, group in df[~df.data_points.isna()].groupby("dev_id"):
            yield dict(device=dev_id, metrics=list(group.ma_id.unique()))
