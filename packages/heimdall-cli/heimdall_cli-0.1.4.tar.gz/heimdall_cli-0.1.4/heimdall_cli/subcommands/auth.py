import os
import click
from ..helpers.api_service import APIService
from ..helpers.utils import error_handling


@click.command()
@click.option("--username")
@click.option("--password")
@click.pass_obj
@error_handling
def login(obj, username: str = None, password: str = None):
    api_service: APIService = obj["api_service"]
    if username is None:
        click.echo("username: ", nl=False)
        username = input()
    if password is None:
        click.echo("password: ", nl=False)
        password = input()

    access, refresh = api_service.login(username, password)
    obj["config"].set(section="CloudService", option="Access-Token", value=access)
    obj["config"].set(section="CloudService", option="Refresh-Token", value=refresh)
    obj["config"].update()
