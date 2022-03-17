import asyncio
import json

from .base import KarezRoleBase


class DispatcherBase(KarezRoleBase):
    def __init__(self, *args, **kwargs):
        super(DispatcherBase, self).__init__(*args, **kwargs)
        self.interval = self.config.interval
        self.target = self.config.connector

    def divide_tasks(self, devices):
        return [devices]

    async def run(self):
        while True:
            if await self.async_ensure_init():
                for devices in self.divide_tasks(self.config.devices):
                    await self.nc.publish(f"karez.connector.{self.target}",
                                          json.dumps(devices).encode("utf-8"))
            await asyncio.sleep(self.interval)
