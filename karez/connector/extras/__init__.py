from . import opcua, eaton_telemetry, virtgen_telemetry, modbus

PLUGINS = dict(
    opcua=opcua.Connector,
    eaton_telemetry=eaton_telemetry.Connector,
    virtgen_telemetry=virtgen_telemetry.Connector,
    modbus=modbus.Connector
)
