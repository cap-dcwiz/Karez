from abc import ABC, abstractmethod

from karez.config import ConfigEntity, OptionalConfigEntity
from karez.connector import ListenConnectorBase
import paho.mqtt.client as mqtt
import asyncio


class MQTTConnectorBase(ListenConnectorBase, ABC):
    """
    Connector for listening from a MQTT broker.
    """

    def __init__(self, *args, **kwargs):
        super(MQTTConnectorBase, self).__init__(*args, **kwargs)
        self.client = None
        self.background_task = set()
        self.loop = None
        self.stop = False

    @classmethod
    def config_entities(cls):
        yield from super(MQTTConnectorBase, cls).config_entities()
        yield ConfigEntity("host", "Host of the MQTT broker.")
        yield OptionalConfigEntity("port", 1883, "Port of the MQTT broker.")
        yield OptionalConfigEntity("topic", "#", "Topics to subscribe.")
        yield OptionalConfigEntity("qos", 0, "QoS level")
        yield OptionalConfigEntity("keep_alive", 60, "The keep alive time in seconds.")

    def on_connect(self, client, userdata, flags, rc):
        if isinstance(self.config.topic, list):
            topic_args = [(t, self.config.qos) for t in self.config.topic]
        else:
            topic_args = self.config.topic, self.config.qos
        client.subscribe(topic_args)

    def parse_payload(self, topic, payload) -> dict:
        return payload

    def finish_testing(self, result):
        super(MQTTConnectorBase, self).finish_testing(result)
        self.stop = True

    def on_message(self, client, userdata, msg):
        task = asyncio.run_coroutine_threadsafe(
            self.async_on_message(client, userdata, msg), self.loop
        )
        self.background_task.add(task)
        task.add_done_callback(self.background_task.discard)

    async def async_on_message(self, client, userdata, msg):
        publish = not self.testing_mode
        res = await asyncio.gather(
            *[
                self.postprocess_item(item, publish=publish, flush=False)
                for item in self.parse_payload(msg.topic, msg.payload)
            ]
        )
        if publish:
            await self.flush()
        else:
            return self.finish_testing(res)

    async def register_listener(self):
        if not self.client:
            self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect_async(
            self.config.host, self.config.port, self.config.keep_alive
        )

    async def wait_forever(self):
        self.loop = asyncio.get_event_loop()
        self.stop = False
        # run asyncio loop forever
        self.client.loop_start()
        while True:
            await self.async_ensure_init()
            await asyncio.sleep(1)
            if self.stop:
                break
        self.client.loop_stop()
