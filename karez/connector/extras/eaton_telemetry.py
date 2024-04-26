from ..restful import RestfulConnectorBase
from ...utils import extract_dict, generator_to_list


class Connector(RestfulConnectorBase):
    @classmethod
    def role_description(cls):
        return "Connector for Eaton DCIM."

    @generator_to_list
    async def fetch_data(self, client, entities):
        r = await client.post(
            "/mtemplates/resources/v3/list",
            json={
                "level_id": 6,
                "target_ids": entities,
            },
        )
        for item in r.json()["data"]:
            dev_info = extract_dict(item, id="dev_id", name="dev_name")
            for child in item["children"]:
                if child["value"] is not None:
                    yield (
                        extract_dict(
                            child,
                            "ma_id",
                            "ma_name",
                            "unit",
                            "value",
                            "value_type",
                            last_time="timestamp",
                        )
                        | dev_info
                    )
