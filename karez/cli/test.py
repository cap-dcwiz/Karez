import asyncio
import json
from pathlib import Path
from pprint import pprint
from types import GeneratorType
from typing import Union

import typer
from dynaconf import Dynaconf

from karez.connector import ConnectorBase
from karez.dispatcher import DispatcherBase
from .common import search_plugins


def get_test_roles(role, plugin_path, config, role_names):
    role_lib = search_plugins(plugin_path, role)
    config_lib = {c.get("name", c.type): c for c in config.get(f"{role}s", [])}
    for name in role_names:
        if name == "":
            continue
        try:
            role_config = config_lib[name]
            cls = role_lib[role_config.type]
        except KeyError:
            typer.echo(f"Cannot find {role.capitalize()} named {name}", err=True)
            continue
        yield cls(role_config, nats_addr=None)


async def _async_test_roles(roles, payload, verbose=False):
    for role in roles:
        payload = await role.process(payload)
        if isinstance(role, DispatcherBase) or isinstance(role, ConnectorBase):
            payload = list(payload)[0]
        if verbose:
            typer.secho(f"After {role.TYPE.upper()} {role.name}:\n", bold=True)
            pprint(payload)
            typer.echo("\n")
    return payload


def test_cmd(config_files: list[Path] = typer.Option(None, "--config", "-c"),
             plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
             dispatcher: str = typer.Option("", "--dispatcher", "-d"),
             connector: str = typer.Option("", "--connector", "-n"),
             converter: str = typer.Option("", "--converter", "-v"),
             input_json: Union[str, None] = typer.Option(None, "--input", "-i"),
             output_json: Union[str, None] = typer.Option(None, "--output", "-o"),
             verbose: bool = False,
             ):
    if config_files:
        config = Dynaconf(settings_files=config_files)
    else:
        config = Dynaconf(includes=["./config/*"])

    roles = []
    roles.extend(get_test_roles("dispatcher", plugin_path, config, dispatcher.split(",")))
    roles.extend(get_test_roles("connector", plugin_path, config, connector.split(",")))
    roles.extend(get_test_roles("converter", plugin_path, config, converter.split(",")))

    if input_json:
        with open(input_json, "r") as f:
            payload = json.load(f)
    else:
        payload = None

    payload = asyncio.run(_async_test_roles(roles, payload, verbose))
    if isinstance(payload, GeneratorType):
        payload = list(payload)

    if output_json:
        with open(output_json, "w") as f:
            json.dump(payload, f, indent=2)
    else:
        pprint(payload)
