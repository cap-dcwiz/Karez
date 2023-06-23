from abc import ABC, abstractmethod

from karez.config import ConfigEntity, OptionalConfigEntity
from karez.connector import ListenConnectorBase
import paho.mqtt.client as mqtt


class MQTTConnectorBase(ListenConnectorBase, ABC):
    """
    Connector for listening from a MQTT broker.
    """
    def __init__(self, *args, **kwargs):
        super(MQTTConnectorBase, self).__init__(*args, **kwargs)
        self.client = None

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

    def on_message(self, client, userdata, msg):
        for item in self.parse_payload(msg.topic, msg.payload):
            self.postprocess_item(item, flush=False)
        self.flush()

    async def register_listener(self):
        if not self.client:
            self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(
            self.config.host,
            self.config.port,
            self.config.keep_alive
        )

    async def start(self):
        self.client.loop_forever()
