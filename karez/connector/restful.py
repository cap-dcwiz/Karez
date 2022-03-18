from abc import ABC

from httpx import AsyncClient, Limits

from .base import PullConnectorBase


class RestfulConnectorForTelemetries(PullConnectorBase, ABC):
    def __init__(self, *args, **kwargs):
        super(RestfulConnectorForTelemetries, self).__init__(*args, **kwargs)
        self.base_url = self.config.base_url

    def create_client(self):
        security_conf = self.config.get("security", None)
        auth = None
        if security_conf:
            if security_conf.type == "basic":
                auth = security_conf.username, security_conf.password
            else:
                raise NotImplementedError
        client = AsyncClient(base_url=self.base_url,
                             auth=auth,
                             limits=Limits(max_keepalive_connections=10,
                                           max_connections=20),
                             **self.config.connection_args or {},
                             )
        return client

