import click
import os
from ..encryption import AESEncryption
from ..helpers.utils import finder, login_required, error_handling
from ..helpers.api_service import APIService, File


@click.command()
@click.argument("file_name")
@click.option("--encrypt", type=bool, default=True)
@click.option("--password", type=str)
@click.pass_obj
@error_handling
@login_required
def upload(obj, file_name: str, encrypt: bool, password: str):
    """Upload a new file"""
    
    # find the file
    if not os.path.exists(file_name):
        raise FileNotFoundError("File does not exists")

    if password is None:
        password = \
            obj["config"]["Credentials"].get("password") or \
            input("encryption key: ")
    # read the file
    with open(file_name, "br+") as file:
        file = file.read()
            
    # encrypt the file
    aes = AESEncryption(password)
    file = aes.encrypt(file)

    # upload the encrypted file
    file = File(name=file_name, content=file.hex())
    api_service: APIService = obj["api_service"]
    id, _ = api_service.create(file)
    click.echo("ID\t\tNAME")
    click.secho(f"{id}\t\t{file_name}")
    

@click.command()
@click.argument("identifier")
@click.pass_obj
@login_required
@click.option("--password", type=str)
def download(obj, identifier:int, password:str):
    click.echo("[Starting]")
    api_service: APIService = obj["api_service"]
    try:
        click.echo("[Searching]")
        id = finder(api_service, identifier).id
        click.echo("[Downloading]")
        file_data = api_service.retrieve(id)

        if password is None:
            password = \
                obj["config"]["Credentials"].get("password") or \
                input("decryption key: ")

        click.echo("[Decrypting]")
    # decrypt the file
        aes = AESEncryption(password)
        file_data.content = aes.decrypt(bytes.fromhex(file_data.content))

    except FileNotFoundError as e:
        click.secho(e, fg="red", err=True)
        exit(1)
    except Exception as e:
        # raise Exception("an error") from e
        raise e

    click.echo("[Saving]")
    with open(file_data.name, "bw") as file:
        file.write(file_data.content)
    click.echo("ID\t\tNAME")
    click.echo(f"{file_data.id}\t\t{file_data.name}")
    
    
@click.command()
@click.pass_obj
@login_required
def list(obj):
    api_service: APIService = obj["api_service"]
    data = api_service.list()
    click.echo("ID\t\tNAME")
    for record in data:
        click.secho(f"{record.id}",nl=False, fg="green")
        click.echo(f"\t\t{record.name}")

@click.command()
@click.argument("identifier")
@click.pass_obj
@login_required
def delete(obj, identifier: int):
    api_service: APIService = obj["api_service"]    
    try:
        file = finder(api_service, identifier)
    except FileNotFoundError as e:
        click.secho(e, fg="red", err=True)
        exit(1)
    click.echo("ID\t\tNAME")
    click.echo(f"{file.id}\t\t{file.name}")
    click.secho("Are you sure you want to delete this file??[y/N]", fg="red", bold=True)
    answer = input()
    if not ((answer =="y") or (answer == "yes")):
        exit(0)
    api_service.delete(file.id)

