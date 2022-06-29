from . import default, eaton, modbus, opcua

PLUGINS = dict(
    default=default.Dispatcher,
    eaton=eaton.Dispatcher,
    modbus=modbus.Dispatcher,
    opcua=opcua.Dispatcher,
)