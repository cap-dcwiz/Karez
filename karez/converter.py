import asyncio
import json
import logging
from abc import abstractmethod
from typing import Union

from .common import KarezRoleBase


class ConverterBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(ConverterBase, self).__init__(*args, **kwargs)
        self.next = self.config.get("next", None)
        self.sub = None

    async def disconnected_cb(self):
        await super(ConverterBase, self).disconnected_cb()

    async def subscribe(self):
        try:
            await self.async_ensure_init()
        except Exception as e:
            logging.error(str(e))
        if self.nc.is_connected:
            if self.sub is not None:
                await self.sub.unsubscribe()
            self.sub = await self.nc.subscribe(f"karez.converter.{self.name}",
                                               queue=f"converter.{self.name}",
                                               cb=self._handler)

    async def run(self):
        while True:
            if not self.nc or not self.nc.is_connected:
                await self.subscribe()
            await asyncio.sleep(10)

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
