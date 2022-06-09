import openstack
from openstack .config import loader
import sys
from database.models import User
from database.models import Services
import mysql.connector


from peewee import PeeweeException


def create_user_in_openstack(username, password, conn):

    user = conn.create_user(
        name=username, password=password, domain_id='default')

    # print(user)
    return user


def save_user_db(name, username, password, id_openstack):

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="odb"
    )

    id_user = id_openstack

    # procurar pelo token posteriormente
    fk_service = Services.select(Services.id_service).where(
        Services.name == "service_test")

    for item in fk_service:
        fk_service_id = item

    User.insert(id_user=id_user, name=name, username=username, password=password,
                creation_date='2021-04-03',
                fk_service=str(1),
                token_OSM='none'
                ).execute()


def get_user(username, conn):
    user = conn.get_user(username)
    return user
