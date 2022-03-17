import asyncio
import logging
from pathlib import Path
from typing import Union

import typer
from dynaconf import Dynaconf

from karez.utils import search_plugins


def launch_role(role, plugin_path, config, event_loop, nats_addr):
    role_lib = search_plugins([Path(plugin_path, role.lower())], role)
    count = 0
    for role_config in config.get(f"{role.lower()}s", []):
        cls = role_lib.get(role_config.type)
        if not cls:
            raise RuntimeError(f"Cannot find {role} plugin: {role_config.type}")
        ins = cls(role_config, nats_addr=nats_addr)
        event_loop.create_task(ins.run())
        count += 1
    logging.info(f"Launched {count} {role}s.")


def main(config_files: list[Path] = typer.Option(None, "--config", "-c"),
         plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
         nats_addr: str = typer.Option("nats://localhost:4222", "--nats-addr", "-a"),
         logging_level: str = typer.Option("INFO", "--logging-level", "-l"),
         launch_dispatcher: bool = typer.Option(False, "--dispatcher", "-d"),
         launch_connector: bool = typer.Option(False, "--connector", "-n"),
         launch_converter: bool = typer.Option(False, "--converter", "-v"),
         ):
    logging.basicConfig()
    logging.getLogger().setLevel(getattr(logging, logging_level))

    logging.info(f"Configurations: {config_files or './config/*'}.")
    logging.info(f"NATS address: {nats_addr}.")

    if config_files:
        config = Dynaconf(settings_files=config_files)
    else:
        config = Dynaconf(includes=["./config/*"])
    event_loop = asyncio.new_event_loop()
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
