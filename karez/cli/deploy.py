import asyncio
from socket import gethostname
import re

import sys

from loguru import logger
from pathlib import Path

import typer
from dynaconf import Dynaconf

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
    logger.info(f"Launched {count} {role.capitalize()}s.")


def deploy_cmd(
    config_files: list[Path] = typer.Option(None, "--config", "-c"),
    plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
    nats_addr: str = typer.Option("nats://localhost:4222", "--nats-addr", "-a"),
    logging_level: str = typer.Option("WARNING", "--logging-level", "-l"),
    logging_rotation: str = typer.Option("90 day", "--logging-rotation", "-r"),
    launch_dispatcher: bool = typer.Option(False, "--dispatcher", "-d"),
    launch_connector: bool = typer.Option(False, "--connector", "-n"),
    launch_converter: bool = typer.Option(False, "--converter", "-v"),
    launch_aggregator: bool = typer.Option(False, "--aggregator", "-g"),
    loadbalance_mode: bool = typer.Option(
        False,
        "--loadbalance",
        "-b",
        help="Run in load balance mode. This only works when used with k8s StatefulSet. "
             "In this mode, each deploy pod with use <config-files>/<pod-index>.yaml as configuration file.",
    ),
):
    # Set logging level for loguru
    logging_level = logging_level.upper()
    common_opts = dict(
        level=logging_level,
        backtrace=logging_level == "DEBUG",
        diagnose=logging_level == "DEBUG",
        enqueue=True,
    )
    logger.remove()
    logger.add(sys.stderr, colorize=True, **common_opts)
    logger.add(
        f"logs/{logging_level.lower()}.log", rotation=logging_rotation, **common_opts
    )
    logger.info(f"Logging to stderr and file {logging_level.lower()}.log.")

    logger.info(
        f"Configurations: {[str(p) for p in config_files] if config_files else './config/*'}."
    )
    logger.info(f"NATS address: {nats_addr}.")

    if config_files:
        if loadbalance_mode:
            logger.info("Running in load balance mode.")
            hostname = gethostname()
            match = re.search(r'-([0-9]+)$', hostname)
            if match:
                index = int(match.group(1))
                config_files = [p / f"{index}.yaml" for p in config_files]
            else:
                raise RuntimeError(f"Cannot find pod index from hostname: {hostname}")
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
