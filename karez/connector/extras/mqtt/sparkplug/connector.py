from typing import Iterable

from ..base import MQTTConnectorBase
from .sparkplug_b import sparkplug_b_pb2, MetricDataType


class SparkplugConnector(MQTTConnectorBase):
    @classmethod
    def role_description(cls) -> str:
        return "Connector for MQTT broker that uses Sparkplug B protocol."

    def parse_payload(self, topic, payload) -> Iterable[dict]:
        inner_payload = sparkplug_b_pb2.Payload()
        inner_payload.ParseFromString(payload)
        for metric in inner_payload.metrics:
            if MetricDataType.Int8 <= metric.datatype <= MetricDataType.UInt64:
                value_field = "int_value"
            elif metric.datatype == MetricDataType.Float:
                value_field = "float_value"
            else:
                continue
            yield dict(
                name=f"{topic.split('/')[-1]}-{metric.name}",
                value=getattr(metric, value_field),
                timestamp=metric.timestamp,
            )
