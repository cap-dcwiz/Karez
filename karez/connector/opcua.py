from numbers import Number

from asyncua import Client

from karez.connector.base import PullConnectorBase


class OPCUAPullConnector(PullConnectorBase):
    def __init__(self, *args, **kwargs):
        super(OPCUAPullConnector, self).__init__(*args, **kwargs)
        self.url = self.config.url

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
