from ...config import ConfigEntity
from ..restful import RestfulConnectorBase
from ...utils import generator_to_list


class Connector(RestfulConnectorBase):
    @classmethod
    def role_description(cls):
        return "Connector for DCWiz virtual generator."

    @classmethod
    def config_entities(cls):
        yield from super(Connector, cls).config_entities()
        yield ConfigEntity("generator_name", "Generator Name")

    @generator_to_list
    async def fetch_data(self, client, entities):
        gen_name = self.config.generator_name
        r = await client.post(
            "/measurements",
            json=entities,
            params=dict(generator_name=gen_name),
            timeout=120,
        )
        for dev_id, dev in r.json()["result"].items():
            dev_name = dev["name"]
            for ma_name, ma in dev["metrics"].items():
                yield {
                    "dev_id": dev_id,
                    "dev_name": dev_name,
                    "ma_id": f"{dev_name}_{ma_name}",
                    "ma_unit": ma["unit"],
                    ma_name: int(ma["value"])
                    if ma["type"] == "int"
                    else float(ma["value"]),
                    "timestamp": ma["timestamp"],
                }
