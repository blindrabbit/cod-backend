from email.policy import default
from enum import unique
from functools import partial
from turtle import back
from peewee import *
from datetime import datetime
from database.connection_db import *

db = create_connection_db('odb',
                          'root2', "root2", '10.50.1.122', 3306)

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


class Laboratory(BaseModel):
    id_laboratory = BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    name = CharField(max_length=100)
    classroom = CharField(max_length=100)
    description = CharField(max_length=100)
    instances = IntegerField()
    creation_date = DateTimeField(default=datetime.now)
    removal_date = DateTimeField(default=datetime.now)
    # fk_network_service = ForeignKeyField(Networkservice, backref='laboratory')
    fk_user = ForeignKeyField(User, backref='laboratories')

    class Meta:
        table_name = 'laboratory'


class Project(BaseModel):
    id_project = CharField(max_length=100, primary_key=True)
    name = CharField(max_length=100, unique=True)
    creation_date = DateField(default=datetime.now)
    fk_user = ForeignKeyField(User, db_column='id_user')
    fk_laboratory = ForeignKeyField(Laboratory, db_column='id_laboratory')
    description = CharField(max_length=100)
    cidr = CharField(max_length=100)
    gateway = CharField(max_length=100)
    openstack_id_network = CharField(max_length=100)
    openstack_id_subnet = CharField(max_length=100)
    openstack_id_router_gateway_port = CharField(max_length=100)
    openstack_id_router = CharField(max_length=100)
    osm_id_vim = CharField(max_length=100)


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


class Vnffgd(BaseModel):
    id_vnffgd = BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    ip_proto = CharField(max_length=100)
    destination_port = CharField(max_length=100)
    source_port = CharField(max_length=100)
    creation_date = DateTimeField(default=datetime.now)

    class Meta:
        table_name = 'vnffgd'


class Constituent_vnfd(BaseModel):
    id_constituent_vnfd = BigIntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    id_constituent_vnfd = CharField(max_length=100)
    type = CharField(max_length=100)
    order = IntegerField()
    creation_date = DateTimeField(default=datetime.now)
    fk_user = ForeignKeyField(Server, db_column='id_server')
    # fk_networkservice = ForeignKeyField(Networkservice, db_column='id_networkservice')

    class Meta:
        table_name = 'constituent_vnfd'


class Networkservice(BaseModel):
    id_networkservice = IntegerField(primary_key=True, unique=True,
            constraints=[SQL('AUTO_INCREMENT')])
    id_osm_ns_instance = CharField(max_length=100)
    id_osm_nsd = CharField(max_length=100)
    id_osm_vim = CharField(max_length=100)
    creation_date = DateTimeField(default=datetime.now)
    fk_project = ForeignKeyField(Project, db_column='id_project')
    fk_vnffgd = ForeignKeyField(Vnffgd, db_column='id_vnffgd', null=True)
    fk_Constituent_vnfd = ForeignKeyField(Constituent_vnfd, db_column='id_constituent_vnfd', null=True)

    class Meta:
        table_name = 'networkservice'
db.create_tables([Services, User, Project, Server, Laboratory, Vnffgd, Constituent_vnfd, Networkservice])
