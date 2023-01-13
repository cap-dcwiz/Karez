from urllib.parse import quote

from karez.config import ConfigEntity
from karez.connector import RestfulConnectorBase
from karez.utils import generator_to_list


class RestSmartConnector(RestfulConnectorBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    @classmethod
    def role_description(cls):
        return "Connector for Schneider SmartConnector."

    @classmethod
    def config_entities(cls):
        yield from super(RestSmartConnector, cls).config_entities()
        yield ConfigEntity("auth", "username and password to get token")

    async def get_token(self, client):
        data = dict(grant_type="password", **self.config.auth)
        response = await client.post("GetToken", data=data)
        self.token = response.json()["access_token"]

    async def _fetch_entity(self, client, entity):
        entity = quote(quote(entity, safe=""))
        url = f"Containers/{entity}/Children"
        r = await client.get(url, headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401:
            await self.get_token(client)
            return await self._fetch_entity(client, entity)
        else:
            r.raise_for_status()

    @generator_to_list
    async def fetch_data(self, client, entities: list[str]):
        if not self.token:
            await self.get_token(client)
        for entity in entities:
            r = await self._fetch_entity(client, entity)
            for child in r:
                if "Value" in child:
                    yield dict(name=child["Id"], value=child["Value"])
