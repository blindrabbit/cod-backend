from databases import Database
from database.models import Services
from database import *
import secrets
from peewee import PeeweeException
from datetime import datetime


def verify_service_authentication(token):
    tokens = Services.select(Services.token)
    authentication = -1
    for item in tokens:
        if item.token == token:
            authentication = 1

    if authentication == -1:
        return authentication
    else:
        names = Services.select(Services.name)
        for item in names:
            name = item.name
            print(name)
        return str(name)


def create_authentication(name):
    token = str(secrets.token_hex(15))

    try:
        now = datetime.now()
        Services.insert(name=name, token=token,
                        creation_date=now).execute()
    except PeeweeException as e:
        return (str(e))

    return str(token)
