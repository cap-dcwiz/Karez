import typer

from . import collect
from . import config
from . import deploy
from . import test

app = typer.Typer()
app.command("deploy")(deploy.deploy_cmd)
app.command("config")(config.config_cmd)
app.command("test")(test.test_cmd)
app.command("collect")(collect.collect_cmd)
