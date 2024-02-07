from pathlib import Path

import sys
import typer
import rich

from .common import PluginType, search_plugins


def list_plugin(
    plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
):
    for plugin_type in PluginType:
        plugin_type = plugin_type.value
        rich.print(f"[bold][{plugin_type.capitalize()}][/bold]")
        role_lib = search_plugins(plugin_path, plugin_type)
        for role_name, role_cls in role_lib.items():
            rich.print(f"   [green]{role_name}[/green]: {role_cls.role_description()}")
        rich.print("\n")


def plugin_doc(
    plugin_type: PluginType,
    plugin_name: str,
    plugin_path: Path = typer.Option("plugins", "--plugin-directory", "-p"),
):
    plugin_type = plugin_type.value
    role_lib = search_plugins(plugin_path, plugin_type)
    plugin_type = plugin_type.capitalize()
    role = role_lib.get(plugin_name)
    if role is None:
        rich.print(f"[red]Cannot find {plugin_type} called {plugin_name}.[/red]")
        sys.exit(1)
    rich.print(f"[bold][{plugin_type}] {plugin_name}[/bold]: {role.role_description()}")
    rich.print(f"[bold]Configuration Options:[/bold]")
    role.print_config_docs(4)
