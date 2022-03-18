import asyncio
import json
from abc import abstractmethod
from typing import Union

from .role import KarezRoleBase, CHECKING_STATUS_INTERVAL


class ConverterBase(KarezRoleBase):
    async def run(self):
        while True:
            if not (self.nc and self.nc.is_connected and self.sub):
                await self.subscribe(f"converter.{self.name}")
            await asyncio.sleep(CHECKING_STATUS_INTERVAL)

    async def _subscribe_handler(self, msg):
        reply = msg.reply
        data = json.loads(msg.data.decode("utf-8"))
        result = self.convert(data)
        if result is None:
            return
        next_converters = data.get("_next", None)
        if next_converters:
            topic = f"karez.converter.{next_converters.pop(0)}"
            reply = reply
        else:
            if "_next" in data:
                del data["_next"]
            if next_converters is []:
                del data["_next"]
            topic = reply
            reply = ""
        await self.nc.publish(topic, json.dumps(result).encode("utf-8"), reply=reply)

    @abstractmethod
    def convert(self, payload) -> Union[None, dict]:
        pass
