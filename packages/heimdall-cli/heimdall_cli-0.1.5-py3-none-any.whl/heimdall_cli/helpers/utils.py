import click
from .api_service import APIService, File
from functools import wraps


def finder(api_service: APIService, identifier: str) -> File:
    files = api_service.list()
    matching = []
    for file in files:
        if str(file.id).startswith(identifier) and len(identifier) > 2:
            matching.append(file)
        elif file.name == identifier:
            matching.append(file)
    if len(matching) == 1:
        return matching[0]
    raise FileNotFoundError("failed to find the file")


def login_required(f):
    @wraps(f)
    def inner(obj, *args, **kwargs):
        access = obj["config"]["CloudService"].get("Access-Token")
        refresh = obj["config"]["CloudService"].get("Refresh-Token")
        if (access is None) and (refresh is None):
            raise Exception("No login credentials")
        api_service: APIService = obj["api_service"]
        api_service.authenticate(access, refresh)
        return f(obj, *args, **kwargs)

    return inner


def error_handling(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
        except Exception as e:
            click.secho(e, err=True)
            exit(1)
        else:
            return res

    return wrapper
