from .dispatcher.extras import PLUGINS as BUILTIN_DISPATCHER_PLUGINS
from .connector.extras import PLUGINS as BUILTIN_CONNECTOR_PLUGINS
from .converter.extras import PLUGINS as BUILTIN_CONVERTER_PLUGINS
from .aggregator.extras import PLUGINS as BUILTIN_AGGREGATOR_PLUGINS

BUILTIN_PLUGINS = dict(
    dispatcher=BUILTIN_DISPATCHER_PLUGINS,
    connector=BUILTIN_CONNECTOR_PLUGINS,
    converter=BUILTIN_CONVERTER_PLUGINS,
    aggregator=BUILTIN_AGGREGATOR_PLUGINS,
)