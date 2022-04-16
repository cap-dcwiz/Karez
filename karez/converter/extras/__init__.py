from . import fix_timestamp, update_info, influx_line_protocol, influx_json_format, eaton_telemetry, \
    filter_and_update_meta

PLUGINS = dict(
    fix_timestamp=fix_timestamp.Converter,
    update_info=update_info.Converter,
    influx_line_protocol=influx_line_protocol.Converter,
    influx_json_format=influx_json_format.Converter,
    eaton_telemetry=eaton_telemetry.Converter,
    filter_and_update_meta=filter_and_update_meta.Converter,
)
