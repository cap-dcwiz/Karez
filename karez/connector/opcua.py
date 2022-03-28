from numbers import Number

from asyncua import Client

from .base import PullConnectorBase
from ..config import ConfigEntity


class OPCUAPullConnector(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(OPCUAPullConnector, self).__init__(*args, **kwargs)
        self.url = self.config.url

    @classmethod
    def config_entities(cls):
        yield from super(OPCUAPullConnector, cls).config_entities()
        yield ConfigEntity("url", "OPC-UA server url.")

    @classmethod
    def role_description(cls):
        return "Connector for OPCUA."

    def create_client(self):
        return Client(url=self.url)

    async def fetch_data(self, client: Client, entities):
        nodes = [client.get_node(node_id) for node_id in entities]
        data = []
        values = await client.read_values(nodes)
        for node_id, value in zip(entities, values):
            if not isinstance(value, Number):
                value = str(value)
            data.append(dict(
                ma_id=node_id,
                value=value
            ))
        return data