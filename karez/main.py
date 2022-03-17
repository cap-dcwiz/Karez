import asyncio
import logging
from pathlib import Path

import sys
import typer
from dynaconf import Dynaconf

from karez.common import search_plugins


def main(config_files: list[Path],
         plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
         nats_addr: str = typer.Option("nats://localhost:4222", "--nats-addr", "-n"),
         logging_level: str = typer.Option("WARNING", "--logging-level", "-l"),
         ):
    logging.basicConfig()
    logging.getLogger().setLevel(getattr(logging, logging_level))

    event_loop = asyncio.new_event_loop()

    config = Dynaconf(settings_files=config_files)
    conn_lib = search_plugins([Path(plugin_path, "connector")], "Connector")
    for conn_config in config.get("connectors", []):
        connector = conn_lib.get(conn_config.type)(conn_config, nats_addr=nats_addr)
        event_loop.create_task(connector.run())

    conv_lib = search_plugins([Path(plugin_path, "converter")], "Converter")
    for conv_config in config.get("converters", []):
        converter = conv_lib.get(conv_config.type)(conv_config, nats_addr=nats_addr)
        # event_loop.run_until_complete(converter.subscribe())
        event_loop.create_task(converter.run())

    event_loop.run_forever()


def run():
    typer.run(main)
