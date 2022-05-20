from numbers import Number

from asyncua import Client

from ...config import ConfigEntity, OptionalConfigEntity
from ..base import PullConnectorBase


class Connector(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(Connector, self).__init__(*args, **kwargs)
        self.url = self.config.url

    @classmethod
    def config_entities(cls):
        yield from super(Connector, cls).config_entities()
        yield ConfigEntity("url", "OPC-UA server url.")
        yield OptionalConfigEntity("timeout", 60, "Request timeout")

    @classmethod
    def role_description(cls):
        return "Connector for OPCUA."

    def create_client(self):
        return Client(url=self.url, timeout=self.config.timeout)

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
