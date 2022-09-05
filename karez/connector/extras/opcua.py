from numbers import Number

from asyncua import Client

from ...config import ConfigEntity, OptionalConfigEntity
from ..base import PullConnectorBase
from ...utils import generator_to_list


class Connector(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(Connector, self).__init__(*args, **kwargs)
        self.url = self.config.url

    @classmethod
    def config_entities(cls):
        yield from super(Connector, cls).config_entities()
        yield ConfigEntity("url", "OPC-UA server url.")
        yield OptionalConfigEntity("timeout", 60, "Request timeout")
        yield OptionalConfigEntity("num_only", True, "Only accept number values")

    @classmethod
    def role_description(cls):
        return "Connector for OPCUA."

    def create_client(self):
        return Client(url=self.url, timeout=self.config.timeout)

    @generator_to_list
    async def fetch_data(self, client: Client, entities):
        nodes = [client.get_node(node_id) for node_id in entities]
        values = await client.read_values(nodes)
        for node_id, value in zip(entities, values):
            if not isinstance(value, Number):
                if self.config.num_only:
                    continue
                else:
                    value = str(value)
            yield dict(name=node_id, value=value)
