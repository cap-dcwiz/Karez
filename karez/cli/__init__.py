import typer

from . import collect
from . import plugin
from . import deploy
from . import test

app = typer.Typer()
app.command("deploy")(deploy.deploy_cmd)
app.command("plugin-doc")(plugin.plugin_doc)
app.command("plugins")(plugin.list_plugin)
app.command("test")(test.test_cmd)
app.command("collect")(collect.collect_cmd)
