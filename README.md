# Karez

Data Collection Module of DCWiz

## Architecture

<img src="doc/arch.svg" alt="Architecture" width="600"/>

There are three types roles in the system:

1. `Dispatcher`: dispatcher triggers data collection tasks and divides the data points to be fetched to small batches.
1. `Connector`: connecter connects to a data source through specific communication protocol.
1. `Converter`: converter processes and transforms the data fetched by the connectors to data format that can be
   accepted by storages. Multiple converters can be applied sequentially. For example, there can be one converter to
   append timestamps and another converter to add additional meta information.
   
There can be multiple instances for each role types, and they can communicate with each other through a NATS message bus. 
Each role instance subscribes the topic of `karez.{role_type}.{role_name}` in the queue `{role_type}.{role_name}`.
For example, a connector named "virtgen_conn" will subscribe the topic `karez.connector.virtgen_conn` in the queue `connector.virtgen_coon`.

Theoretically, one can also put all the data post-processing work in the connectors. 
There is no compulsive rule for which work must be implemented as converters.
However, it would be a good practice to keep a connector as simple as possible to maximise the data retrieving performances.
Also, it is easy to set up multiple converters to parallelise some heavy data processing procedures.

Users can implement own dispatchers, connectors, and/or converters. 
The system will automatically search for all required plugins in the `plugins` directories.

## Get Started

### Docker compose
A docker compose file has been provided in the `sample` directory. It will launch
1. A InfluxDB instance to receive time-series data
1. A telegraf instance to collect time-series data from NATS bus and send them to InfluxDB. 
   (It works as a `Aggregator` as shown in the architecture diagram.)
1. A container contains dispatchers (can be scaled to multiple instances).
1. A container contains dispatchers (can be scaled to multiple instances).
1. A container contains converters (can be scaled to multiple instances).

Note that, a `.env` file is required to provide necessary configurations.

```dotenv
INFLUXDB_USERNAME=XXX
INFLUXDB_PASSWORD=XXX
INFLUXDB_ORG=XXX
INFLUXDB_PLATFORM_BUCKET=XXX
INFLUXDB_TOKEN=XXX

KAREZ_CONFIG=virtgen.yaml
```

### Commands

Two executives are provides:

1. `karez`: run dispatchers, connectors or converters. 
   It will search the used dispatchers, connectors and converters in a given configuration file. 
   If none of `-d`, `-n` or `-v` is provided. It will launch all types of roles. 
   Otherwise, only roles of the specified type(s) will be launched.

   ```shell
   $ poetry run karez -c config/opcua.yaml -p ../plugins/ -l INFO
   INFO:root:Configurations: [PosixPath('config/opcua.yaml')].
   INFO:root:NATS address: nats://localhost:4222.
   INFO:root:Launched 3 Converters.
   INFO:root:Launched 1 Connectors.
   INFO:root:Launched 1 Dispatchers.
   INFO:asyncua.client.client:connect
   INFO:asyncua.client.ua_client.UaClient:opening connection
   INFO:asyncua.client.ua_client.UASocketProtocol:open_secure_channel
   INFO:asyncua.client.ua_client.UaClient:create_session
   ```   

   Run `karez --help` for more information.
   ```shell
   $ poetry run karez --help
   Usage: karez [OPTIONS]

   Options:
     -c, --config PATH
     -p, --plugin-directory PATH     [default: plugins]
     -a, --nats-addr TEXT            [default: nats://localhost:4222]
     -l, --logging-level TEXT        [default: WARNING]
     -d, --dispatcher
     -n, --connector
     -v, --converter
     --install-completion [bash|zsh|fish|powershell|pwsh]
                                     Install completion for the specified shell.
     --show-completion [bash|zsh|fish|powershell|pwsh]
                                     Show completion for the specified shell, to
                                     copy it or customize the installation.
     --help                          Show this message and exit.
   ```
1. `karez-config-help`: list all configuration items for a particular plugin.
   ```shell
   $ poetry run karez-config-help connector eaton_telemetry -p ../plugins/

   [connector] eaton_telemetry: Connector for Eaton DCIM.

   Configuration Options:

        - type: Type of the plugin.

        - base_url: Base URL of the RESTful server.

        - name: [Optional] Name of the plugin.
           default: Same as type

        - converter: [Optional] Converters to be used.
           default: None

        - security: [Optional] Security configuration.
           default: None

        - connection_args: [Optional] Additional connection args to passed to httpx.AsyncClient.
           default: {}
   ```