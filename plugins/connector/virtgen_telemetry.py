from karez.utils import sub_dict
from karez.connector import RestfulConnectorForTelemetries


class Connector(RestfulConnectorForTelemetries):
    async def fetch_data(self, client, entities):
        gen_name = self.config.generator_name
        r = await client.post("/measurements",
                              json=entities,
                              params=dict(generator_name=gen_name),
                              timeout=120)
        data = []
        for dev_id, dev in r.json()["result"].items():
            dev_name = dev["name"]
            for ma_name, ma in dev["metrics"].items():
                data.append(dict(
                    dev_id=dev_id,
                    dev_name=dev_name,
                    ma_id=f"{dev_name}_{ma_name}",
                    ma_name=ma_name,
                    ma_unit=ma["unit"],
                    ma_value=int(ma["value"]) if ma["type"] == "int" else float(ma["value"]),
                    timestamp=ma["timestamp"]
                ))
        return data
