from ..restful import RestfulConnectorBase
from ...utils import sub_dict


class Connector(RestfulConnectorBase):
    @classmethod
    def role_description(cls):
        return "Connector for Eaton DCIM."

    async def fetch_data(self, client, entities):
        r = await client.post("/mtemplates/resources/v3/list",
                              json={
                                  "level_id": 6,
                                  "target_ids": entities,
                              })
        data = []
        for item in r.json()["data"]:
            dev_info = sub_dict(item, id="dev_id", name="dev_name")
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