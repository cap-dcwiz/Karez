from karez.utils import sub_dict
from karez.connector import RestfulConnectorForTelemetries


class Connector(RestfulConnectorForTelemetries):
    def divide_requests(self, devices):
        devs = []
        for dev_type, ds in devices.items():
            for dev in ds:
                devs.append((dev, dev_type))
        batch_size = self.config.get("batch_size", 50)
        for i in range(0, len(devs), batch_size):
            yield devs[i: i+batch_size]

    async def fetch_data(self, client, devices):
        devices = {dev: dev_type for dev, dev_type in devices}
        r = await client.post("/mtemplates/resources/v3/list",
                              json={
                                  "level_id": 6,
                                  "target_ids": list(devices.keys()),
                              })
        data = []
        for item in r.json()["data"]:
            dev_info = sub_dict(item, id="dev_id", name="dev_name")
            dev_info["dev_type"] = devices[dev_info["dev_id"]]
            for child in item["children"]:
                if child["value"] is not None:
                    data.append(
                        sub_dict(child,
                                 "ma_id", "ma_name",
                                 "unit", "value", "value_type",
                                 last_time="timestamp")
                        | dev_info
                    )
        return data
