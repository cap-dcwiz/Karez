# Get Started

## Docker compose

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
