import click
from .helpers.api_service import APIService
from .helpers.utils import error_handling
from .helpers.config_manager import ConfigManager
from . import subcommands
import os
from pathlib import Path

CONFIG_PATH = os.path.expanduser("~/.config")
path = Path(CONFIG_PATH + "/heimdall_config.ini")


@click.group()
@error_handling
@click.pass_context
def cli(ctx: click.Context):
    # click.echo("Hi there")
    # handel file configuration and password management
    config = ConfigManager(file_addr=path.as_posix())
    if not path.is_file():
        config["Encryption"] = {"scheme": "AES", "block-size": 128}
        config["CloudService"] = {"url": "heimdall.amcsui.ir:8000"}
        config.update()
    config.read()
    access = config["CloudService"].get("Access-Token")
    refresh = config["CloudService"].get("Refresh-Token")

    ctx.obj = {
        "config": config,
        "api_service": APIService(host=config["CloudService"]["host"]),
    }


cli.add_command(subcommands.upload)
cli.add_command(subcommands.download)
cli.add_command(subcommands.list)
cli.add_command(subcommands.delete)
cli.add_command(subcommands.login)
