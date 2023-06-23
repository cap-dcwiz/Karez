from abc import ABC

from .base import PullConnectorBase
from ..role import RestfulRoleMixin


class RestfulConnectorBase(PullConnectorBase, RestfulRoleMixin, ABC):
    """
    Base class of connectors that pull data from RESTful servers.
    A https client will be created for each batch of tasks.
    """

    def create_client(self):
        return RestfulRoleMixin.create_client(self)
