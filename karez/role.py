import asyncio
import json
import logging
from abc import abstractmethod
from copy import copy
from typing import Generator

import nats

from .config import (
    ConfigurableBase,
    OptionalConfigEntity,
    ConfigEntity,
    ConfigEntityBase,
)

CHECKING_STATUS_INTERVAL = 10
CONNECTOR_MODE_WORKER = 0
CONNECTOR_MODE_CONTROLLER = 1


class RoleBase(ConfigurableBase):
    """
    Base class for Roles (Dispatcher, Connector and Converter).
    """

    TYPE = NotImplemented

    def __init__(self, config, nats_addr="nats://localhost:4222"):
        super(RoleBase, self).__init__(config)
        self.name = self.config.name
        self.nc_addr = nats_addr
        self.nc = None
        self.sub = None

    @classmethod
    def config_entities(cls) -> Generator[ConfigEntityBase, None, None]:
        yield from super(RoleBase, cls).config_entities()
        conf_type = ConfigEntity("type", "Type of the plugin.")
        yield OptionalConfigEntity("name", conf_type, "Name of the plugin.")
        yield conf_type

    @classmethod
    @abstractmethod
    def role_description(cls) -> str:
        pass

    @property
    def subscribe_topic(self):
        return f"karez.{self.TYPE}.{self.name}"

    @property
    def subscribe_queue(self):
        return f"{self.TYPE}.{self.name}"

    @staticmethod
    def connector_topic(name):
        return f"karez.connector.{name}"

    @staticmethod
    def converter_topic(name):
        return f"karez.converter.{name}"

    def aggregator_topic(self, data, default_category="telemetry"):
        # if isinstance(data, dict):
        category = self.get_meta(data, "category", default_category)
        # else:
        #     category = default_category
        return f"karez.{category}.{self.name}"

    async def error_cb(self, e):
        logging.error(f"{self.name}: {str(e)}!")

    async def disconnected_cb(self):
        logging.warning(f"{self.name}: Got disconnected!")
        self.sub = None

    async def reconnected_cb(self):
        logging.info(f"{self.name}: Got reconnected to {self.nc.connected_url.netloc}")

    async def async_ensure_init(self):
        conn_options = dict(
            servers=self.nc_addr,
            name=self.name,
            error_cb=self.error_cb,
            disconnected_cb=self.disconnected_cb,
            reconnected_cb=self.reconnected_cb,
        )
        try:
            if not self.nc:
                self.nc = await nats.connect(**conn_options)
            elif not self.nc.is_connected:
                await self.nc.connect(**conn_options)
        except Exception as e:
            logging.error(str(e))
        return self.nc and self.nc.is_connected

    async def _subscribe_handler(self, msg):
        # Do stuff when received msg, can be empty (for most dispatchers).
        pass

    @abstractmethod
    async def process(self, payload):
        pass

    async def subscribe(self):
        if await self.async_ensure_init():
            if self.sub:
                await self.sub.unsubscribe()
                self.sub = None
            self.sub = await self.nc.subscribe(
                self.subscribe_topic,
                queue=self.subscribe_queue,
                cb=self._subscribe_handler,
            )

    async def run(self):
        while True:
            if not (self.nc and self.nc.is_connected and self.sub):
                await self.subscribe()
            await asyncio.sleep(CHECKING_STATUS_INTERVAL)

    @staticmethod
    def get_meta(data, key, default=None):
        return data.get("_karez", {}).get(key, default)

    @staticmethod
    def pop_meta(data, key, default=None):
        if "_karez" in data:
            res = data.pop(key, default)
            if not data["_karez"]:
                data.pop("_karez")
            return res
        else:
            return default

    @staticmethod
    def update_meta(data, **kwargs):
        for key, value in kwargs.items():
            meta = data.get("_karez", {})
            meta[key] = value
            data["_karez"] = meta
        return data

    @staticmethod
    def copy_meta(new_data, old_data, clear_old=False):
        new_data = copy(new_data)
        # if isinstance(new_data, dict) and \
        #         isinstance(old_data, dict) and \
        #         "_karez" in old_data:
        new_data["_karez"] = old_data.get("_karez", {}) | new_data.get("_karez", {})
        if clear_old:
            RoleBase.clear_meta(old_data)
        return new_data

    @staticmethod
    def clear_meta(data):
        data.pop("_karez", None)

    async def publish(self, topic, payload, **kwargs):
        if "_as_is" in payload:
            payload = payload["_as_is"]
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        payload = payload.encode("utf-8")
        return await self.nc.publish(topic, payload, **kwargs)

    async def flush(self):
        return await self.nc.flush()
