from abc import ABC

from httpx import AsyncClient, Limits

from .base import PullConnectorBase
from ..config import ConfigEntity, OptionalConfigEntity


class RestfulConnectorBase(PullConnectorBase, ABC):
    def __init__(self, *args, **kwargs):
        super(RestfulConnectorBase, self).__init__(*args, **kwargs)
        self.base_url = self.config.base_url

    @classmethod
    def config_entities(cls):
        yield from super(RestfulConnectorBase, cls).config_entities()
        yield ConfigEntity("base_url", "Base URL of the RESTful server.")
        yield OptionalConfigEntity("security", None, "Security configuration.")
        yield OptionalConfigEntity(
            "connection_args",
            {},
            "Additional connection args to passed to httpx.AsyncClient.",
        )

    def create_client(self):
        security_conf = self.config.security
        auth = None
        if security_conf:
            if security_conf.type == "basic":
                auth = security_conf.username, security_conf.password
            else:
                raise NotImplementedError
        client = AsyncClient(
            base_url=self.base_url,
            auth=auth,
            limits=Limits(max_keepalive_connections=10, max_connections=20),
            **self.config.connection_args,
        )
        return client
