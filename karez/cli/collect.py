import asyncio
import json
from pathlib import Path
from pprint import pprint
from typing import Union

import sys
import typer
from dynaconf import Dynaconf

from karez.connector import ConnectorBase
from karez.dispatcher import DispatcherBase
from .common import search_plugins


async def _async_collect(roles, payload, verbose):
    async def noop_d(data):
        return [data]

    async def noop_n(data):
        return data

    if isinstance(roles[0], DispatcherBase):
        dispatcher_process = roles.pop(0).process
    else:
        dispatcher_process = noop_d

    if isinstance(roles[0], ConnectorBase):
        connector_process = roles.pop(0).process
    else:
        connector_process = noop_n

    res = []
    for r1 in await dispatcher_process(payload):
        if verbose and dispatcher_process is not noop_d:
            typer.echo(f"Dispatcher result received.")
        for r2 in await connector_process(r1):
            if verbose and connector_process is not noop_n:
                typer.echo(f"Connector result received.")
            r3 = r2
            for role in roles:
                r3 = await role.process(r3)
                if r3 is None:
                    break
                if verbose:
                    typer.echo(f"Applied converter: {role.name}")
            if r3 is not None:
                res.append(r3)
    return res


def collect_cmd(config_files: list[Path] = typer.Option(None, "--config", "-c"),
                plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
                input_json: Union[str, None] = typer.Option(None, "--input", "-i"),
                output_json: Union[str, None] = typer.Option(None, "--output", "-o"),
                verbose: bool =
                False,
                ):
    if config_files:
        config = Dynaconf(settings_files=config_files)
    else:
        config = Dynaconf(includes=["./config/*"])

    disp_lib = search_plugins(plugin_path, "dispatcher")

    if len(config.dispatchers) > 1:
        typer.secho(f"FAIL: Mulitple dispatcher found.", err=True)
        sys.exit(1)
    else:
        sub_config = config.dispatchers[0]
        dispatcher = disp_lib[sub_config.type](sub_config, nats_addr=None)

    conn_lib = search_plugins(plugin_path, "connector")
    connector_name = dispatcher.config.connector

    connector = None
    for sub_config in config.connectors:
        if sub_config.get("name", sub_config.type) == connector_name:
            if sub_config.type in conn_lib:
                connector = conn_lib[sub_config.type](sub_config, nats_addr=None)
                break
            else:
                typer.secho(f"Cannot find Connector type {connector_name}.", err=True)
                sys.exit(1)
    if not connector:
        typer.secho(f"Cannot find config for Connector {connector_name}")
        sys.exit(1)

    roles = [dispatcher, connector]
    conv_lib = search_plugins(plugin_path, "converter")
    for converter_name in (connector.config.converter or []):
        for sub_config in config.converters:
            if sub_config.get("name", sub_config.type) == converter_name:
                if sub_config.type in conv_lib:
                    converter = conv_lib[sub_config.type](sub_config, nats_addr=None)
                    roles.append(converter)
                    break
                else:
                    typer.secho(f"Cannot find Converter type {sub_config.type}.", err=True)
                    sys.exit(1)

    if input_json:
        with open(input_json, "r") as f:
            payload = json.load(f)
    else:
        payload = None
    payload = asyncio.run(_async_collect(roles, payload, verbose))

    if output_json:
        with open(output_json, "w") as f:
            json.dump(payload, f, indent=2)
    else:
        pprint(payload)
