import asyncio
import logging
from pathlib import Path

import typer
from dynaconf import Dynaconf
from rich import print

from .common import search_plugins


def launch_role(role, plugin_path, config, event_loop, nats_addr):
    role_lib = search_plugins(plugin_path, role)
    count = 0
    for role_config in config.get(f"{role}s", []):
        cls = role_lib.get(role_config.type)
        if not cls:
            raise RuntimeError(
                f"Cannot find {role.capitalize()} plugin: {role_config.type}"
            )
        ins = cls(role_config, nats_addr=nats_addr)
        event_loop.create_task(ins.run())
        count += 1
    print(f"[bold][KAREZ][/bold] Launched {count} {role.capitalize()}s.")


def deploy_cmd(
    config_files: list[Path] = typer.Option(None, "--config", "-c"),
    plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
    nats_addr: str = typer.Option("nats://localhost:4222", "--nats-addr", "-a"),
    logging_level: str = typer.Option("WARNING", "--logging-level", "-l"),
    launch_dispatcher: bool = typer.Option(False, "--dispatcher", "-d"),
    launch_connector: bool = typer.Option(False, "--connector", "-n"),
    launch_converter: bool = typer.Option(False, "--converter", "-v"),
    launch_aggregator: bool = typer.Option(False, "--aggregator", "-g"),
):
    logging.getLogger().setLevel(getattr(logging, logging_level))

    print(
        f"[bold][KAREZ][/bold] Configurations: {[str(p) for p in config_files] if config_files else './config/*'}."
    )
    print(f"[bold][KAREZ][/bold] NATS address: {nats_addr}.")

    if config_files:
        config = Dynaconf(settings_files=config_files, envvar_prefix="KAREZ")
    else:
        config = Dynaconf(includes=["./config/*"], envvar_prefix="KAREZ")
    event_loop = asyncio.new_event_loop()
    args = plugin_path, config, event_loop, nats_addr

    if not (
        launch_dispatcher or launch_connector or launch_converter or launch_aggregator
    ):
        launch_dispatcher = True
        launch_connector = True
        launch_converter = True
        launch_aggregator = True

    if launch_converter:
        launch_role("converter", *args)

    if launch_connector:
        launch_role("connector", *args)

    if launch_dispatcher:
        launch_role("dispatcher", *args)

    if launch_aggregator:
        launch_role("aggregator", *args)

    event_loop.run_forever()
