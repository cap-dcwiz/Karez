from enum import Enum
from pathlib import Path

import sys
import typer

from karez.role import RoleBase
from .common import search_plugins


class PluginType(str, Enum):
    dispatcher = "dispatcher"
    connector = "connector"
    converter = "converter"


def search_role_for_help(role: str, role_name, plugin_path) -> RoleBase:
    role_lib = search_plugins(plugin_path, role)
    return role_lib.get(role_name)


def config_cmd(plugin_type: PluginType,
               plugin_name: str,
               plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
               ):
    role = search_role_for_help(role=plugin_type.value,
                                role_name=plugin_name,
                                plugin_path=plugin_path)
    if role is None:
        typer.echo(f"Cannot find {plugin_type} called {plugin_name}.", err=True)
        sys.exit(1)
    typer.secho(f"\n[{plugin_type}] {plugin_name}: {role.role_description()}\n")
    typer.secho(f"Configuration Options:\n", bold=True)
    role.print_config_docs(4)
