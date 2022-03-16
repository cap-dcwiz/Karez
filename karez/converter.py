import json
import logging
from abc import abstractmethod
from typing import Union

from .common import KarezRoleBase


class ConverterBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(ConverterBase, self).__init__(*args, **kwargs)
        self.next = self.config.get("next", None)

    async def subscribe(self):
        await self.async_init()
        await self.nc.subscribe(f"karez.converter.{self.name}",
                                queue=f"converter.{self.name}",
                                cb=self._handler)

    async def _handler(self, msg):
        reply = msg.reply
        data = msg.data.decode("utf-8")
        result = self.convert(json.loads(data))
        if result is None:
            return
        if self.next:
            topic = f"karez.converter.{self.next}"
            reply = reply
        else:
            topic = reply
            reply = ""
        await self.nc.publish(topic, json.dumps(result).encode("utf-8"), reply=reply)

    @abstractmethod
    def convert(self, payload) -> Union[None, dict]:
        pass
