from enum import unique
from functools import partial
from peewee import *
from database.connection_db import *

db = create_connection_db('odb',
                          'root', 'root', '127.0.0.1', 3306)


class BaseModel(Model):
    class Meta:
        database = db

class Services(BaseModel):
    id_service = AutoField(primary_key=True)
    name = CharField(max_length=100)
    token = CharField(max_length=100)
    creation_date = DateField()

    class Meta:
        table_name = 'service'

class User(BaseModel):
    id_user = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100)
    username = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    creation_date = DateField(formats=None)
    fk_service = ForeignKeyField(
        Services, db_column='id_service')

    # fk_service = ForeignKeyField(Services, to_field='idservice')
    token_OSM = CharField()

    class Meta:
        table_name = 'user'

class Project(BaseModel):
    id_project = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()
    fk_user = ForeignKeyField(User, db_column='id_user')
    id_openstack = CharField(max_length=100, unique=True)
    id_OSM = CharField(max_length=100, unique=True)
    id_vim_OSM = CharField(max_length=100, unique=True)
    descricao = CharField(max_length=100)

    class Meta:
        table_name = 'project'

class Server(BaseModel):
    id_server = BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    id_server_openstack = CharField(max_length=100, unique=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField()
    fk_project = CharField(max_length=100)
    state = CharField(max_length=100)
    cookie = CharField(max_length=100)
    testecampo = CharField(max_length=100)

    class Meta:
        table_name = 'server'

db.create_tables([Services, User, Project, Server])
