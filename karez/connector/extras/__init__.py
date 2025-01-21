from . import opcua, eaton_telemetry, virtgen_telemetry, modbus, eaton, schneider, mqtt, restful_listener

PLUGINS = dict(
    opcua=opcua.Connector,
    eaton_telemetry=eaton_telemetry.Connector,
    virtgen_telemetry=virtgen_telemetry.Connector,
    modbus=modbus.Connector,
    eaton=eaton.Connector,
    schneider_smart_connector=schneider.RestSmartConnector,
    mqtt_sparkplug_b_connector=mqtt.SparkplugConnector,
    restful_listener=restful_listener.RestfulListenerConnector,
)
