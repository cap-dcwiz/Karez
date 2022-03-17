import asyncio
import logging
from pathlib import Path

import typer
from dynaconf import Dynaconf

from karez.utils import search_plugins


def launch_role(role, plugin_path, config, event_loop, nats_addr):
    role_lib = search_plugins([Path(plugin_path, role.lower())], role)
    for role_config in config.get(f"{role.lower()}s", []):
        ins = role_lib.get(role_config.type)(role_config, nats_addr=nats_addr)
        event_loop.create_task(ins.run())


def main(config_files: list[Path],
         plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
         nats_addr: str = typer.Option("nats://localhost:4222", "--nats-addr", "-n"),
         logging_level: str = typer.Option("WARNING", "--logging-level", "-l"),
         launch_dispatcher: bool = typer.Option(False, "--dispatcher", "-d"),
         launch_connector: bool = typer.Option(False, "--connector", "-c"),
         launch_converter: bool = typer.Option(False, "--converter", "-v"),
         ):
    logging.basicConfig()
    logging.getLogger().setLevel(getattr(logging, logging_level))

    event_loop = asyncio.new_event_loop()
    config = Dynaconf(settings_files=config_files)
    args = plugin_path, config, event_loop, nats_addr

    if not (launch_dispatcher or launch_connector or launch_converter):
        launch_dispatcher = True
        launch_connector = True
        launch_converter = True

    if launch_converter:
        launch_role("Converter", *args)

    if launch_connector:
        launch_role("Connector", *args)

    if launch_dispatcher:
        launch_role("Dispatcher", *args)

    event_loop.run_forever()


def run():
    typer.run(main)
