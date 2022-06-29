from karez.config import OptionalConfigEntity
from karez.connector import RestfulConnectorBase
from karez.utils import extract_dict, generator_to_list


class Connector(RestfulConnectorBase):
    @classmethod
    def role_description(cls):
        return "Connector for Eaton DCIM."

    @classmethod
    def config_entities(cls):
        yield from super(Connector, cls).config_entities()
        yield OptionalConfigEntity("output_format", "full", "output format (full or simple).")

    @generator_to_list
    async def fetch_data(self, client, entities: list[dict]):
        entities = {item["device"]: item["metrics"] for item in entities}
        r = await client.post("/mtemplates/resources/v3/list",
                              json={
                                  "level_id": 6,
                                  "target_ids": list(entities.keys()),
                              })
        for item in r.json()["data"]:
            dev_info = extract_dict(item, id="dev_id", name="dev_name")
            for child in item["children"]:
                if child["value"] is not None and child["ma_id"] in entities[dev_info["dev_id"]]:
                    if self.config.output_format == "full":
                        yield extract_dict(child,
                                           "ma_id", "ma_name",
                                           "unit", "value", "value_type",
                                           last_time="timestamp"
                                           ) | dev_info
                    elif self.config.output_format == "simple":
                        yield dict(name=f'{dev_info["dev_id"]}/{child["ma_id"]}',
                                   value=child["value"])
