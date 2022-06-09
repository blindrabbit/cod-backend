# from app.database.models import Services, User
# # from app.OSM import user
# from openstack import identity
# from openstack.exceptions import OpenStackCloudException
# from peewee import DateField, Model, PeeweeException
import requests
# import openstack
# from openstack.config import loader
# import sys
# from openstack import connection
# import mysql.connector
# # from database.connection_db import create_connection_db
# # from database.models import *
# # from VIO.clouds.Openstack.connection.connection import create_connection_openstack
# import secrets
# from openstack import exceptions
# # cnx = create_connection_db('orchestrator_database', 'root', 'root', '127.0.0.1', 3306)

# from openstack.identity.v3._proxy import *
# import yaml
# import json
# from app.VIO.clouds.Openstack.connection.connection import *
# from keystoneauth1 import loading
# from keystoneauth1 import session as session
# from keystoneclient.v3 import client as client
# from keystoneauth1.identity import v3
# import bios
# import os
# import subprocess
# import peewee
# from openstack.identity.v3.domain import *
# from database.models import Services

# json para criar token
# payload = {
#          'name': 'test_servidor_serra',
#         }
print("TESTE")
payload = {
          'nome': 'admin',
         }
# payload = {}

header = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

a = requests.request(
    method="POST", url='http://127.0.0.1:5000/authentication/', json=payload, headers=header)

print(a.text)


# json pra criar usuario
# payload = { 'username': 'test123',
#         'password': 'test123',
#         'name': 'fulano',
#         'token': '89d6a604bdb69cff1dee1fa0db93a3'
#     }

# return example
# {"default_project_id":null,"description":null,"domain_id":"default","email":null,"enabled":true,"id":"47866e9361bf48f1a9e85c78569cb015","name":"test123","username":null}


# json para criar projeto
# payload={'username': 'test123',
#         'laboratory_name': 'test_test',
#         'token': "89d6a604bdb69cff1dee1fa0db93a3"
#     }

# security groups json

# payload = { 'username': 'test',
#             'password': 'test123',
#             'project_name': 'projeto_test',
#             'security_group_name': 'test_security_groups1',
#             'project_id': '0f9ffee851ac4d47af8c7edd66afce4a',
#             'description': 'kakakakakakak'
#         }

# json rules
# payload = {
#     'username': 'test',
#     'password': 'test123',
#     'project_name': 'projeto_test',
#     'security_group_id': '81153892-395f-41d2-aeea-a6efe454642a',
#     'direction':'ingress',
#     'remote_ip_prefix':'0.0.0.0/0',
#     'protocol': 'tcp',
#     'port_range_max':'443',
#     'port_range_min':'443',
#     'ethertype':'IPv4'
#     }


# network json
# payload = {
#     'username': 'test',
#     'password': 'test123',
#     'project_name': 'projeto_test',
#     'name_network': "teste_net"
#     }

# subnet json
# payload = {
#     'username': 'test',
#     'password': 'test123',
#     'project_name': 'projeto_test',
#     'name_subnet': 'subnet_test',
#     'network_id': "cf1a21f8-151d-4c08-ad17-9ca38238237f",
#     'ip_version':'4',
#     'cidr':'10.0.2.0/24',
#     'gateway_ip':'10.0.2.1'
#     }

# flavor json

# payload = {
#         'laboratory_id': "0f9ffee851ac4d47af8c7edd66afce4a",
#         'name': "test_flavor",
#         'vcpus':'4',
#         'disk': '40',
#         'ram': 1024,
#         'ephemeral':0,
# }


# vim json

# payload = {
#     "vim_name": "test_test",
#     "description": "lllkkkkkk",
#     "laboratory_name": "projeto_test70",
#     "tipo_nuvem": "openstack",
#     "token": "kkkkkkoksa"
#     }


# # json pra criar usuario
# payload = {'username': 'test456',
#            'password': 'test456',
#            'name': 'Nome teste',
#            'token': '123abc'
#            }

# # payload = {}

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json'
# }

# a = requests.request(
#     method="POST", url='http://192.168.0.109:8010/user/', json=payload)

# print(a)

# id = Services.select(Services.idservice).where(Services.name == "service_test")
# for item in id:
#     print(item)

# connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
#                                                    'RegionOne', 'admin',
#                                                    'admin', 'stack', 'default', 'default')

# resp = connection_openstack.get("projeto_test70")

# print(resp)

# payload={}


# import requests

# url = "https://10.50.1.142:9999/osm/admin/v1/tokens"

# headers = {
# 'Content-Type': 'application/json'
# }
# payload = {
#     "username": 'admin',
#     "password": 'admin',
#     "project_id": 'admin'
# }

# import requests

# url = "http://10.50.1.142:8010/vim/"
# payload={}

# headers = {
#                 'Content-Type': 'application/json',
#                 'Accept': 'application/json',
#             }

# response = requests.request('POST', url, headers=headers, json=payload,verify=False)
# print(response.text)

# payload={
#          'name': 'harrison_sanches',
#          }

# a = requests.request(method="POST", url='http://10.50.1.142:8010/projects/',
#                      json=payload)
# print(a.text)


# url = "https://192.168.0.115:9999/osm/vnfpkgm/v1/vnf_packages"
# A = open('/home/sanches/cirros_alarm_vnf/cirros_alarm_vnfd.yaml')
# B= yaml.full_load(A)
# dc = yaml.dump(B, sort_keys=False)

# d = bios.read('/home/sanches/cirros_alarm_vnf/cirros_alarm_vnfd.yaml')
# print(d)

# payload = d
# with open("/home/sanches/cirros_alarm_vnf/cirros_alarm_vnfd.yaml", 'r') as yaml_in, open("example.json", "w") as json_out:
#     yaml_object = yaml.safe_load(yaml_in) # yaml_object will be a list or a dict
#     json.dump(yaml_object, json_out)

# b = open('/home/sanches/projects/Campus-ON-Demand/example.json',)
# c = json.load(b)


# ---------------------------------------aqui

# payload = {}

# headers = {
#   'Content-Type': 'application/json',
#   'Accept': 'application/json'
# }

# a = requests.request(method="POST", url='http://127.0.0.1:8000/VNF/', json=payload)

# print(a)


# a = connection_openstack.create_flavor(name="test1",ram=1024,vcpus=4,
#                                    disk=40,ephemeral=0,is_public=False)


# print(a.id)


# atts = connection_openstack.image.create_image(**image_attrs)
# image = connection_openstack.image.import_image(atts, method="web-download", uri=url)

# connection_openstack.add_flavor_access(flavor_id="9c4cbef6-a24b-4ed7-822d-4d11488091bc",
#                                        project_id="0f9ffee851ac4d47af8c7edd66afce4a")

# a = connection_openstack.create_image(name="test", disk_format='qcow2', container_format='bare',
#                                       filename='https://download.cirros-cloud.net/0.5.0/cirros-0.5.0-aarch64-disk.img')


# connection_openstack.image.ceate_image(name="test", )
# print(image)
#
# a = connection_openstack.image.import_image(image, method="web-download", uri=url)
# print(a)

# connection_openstack.create_subnet()

# a = requests.request(method="POST", url='http://127.0.0.1:8000/subnet/', json=payload)
# print(a.text)
# url = 'https://192.168.0.115:9999/osm/admin/v1/projects'
# token_osm = 'SxAZEuYlSkGoAIVJpljr7lRUuhodoDRx'


# payload={}
# headers = {
#     'Content-Type': ' application/json',
#     'Accept': ' application/json',
#     "Authorization": 'Bearer ' + token_osm
# }

# response = requests.request("GET", url, headers=headers, json=payload)

# print(response.json())

# payload={
#     "username": "admin",
#     "password": "admin",
#     "project_id": "admin"
#         #  token pro admin do osm
#     }

# headers = {
#   'Content-Type': 'application/json'
# }

# response = requests.request("POST", url, headers=headers, json=payload, verify=False)
# print(response.text)
# token = secrets.token_hex(15)
# # print(str(token))

# connection_openstack = create_connection_openstack("http://192.168.1.108/identity", 'RegionOne', 'test',
#                                                 'test','test123','default','default')

# connection_openstack.list_projects()

# a = connection_openstack.get_project("test")
# print(a.name)

# with open("/home/sanches/Downloads/yaml-validator.yaml", 'r') as yaml_in, open("example.json", "w") as json_out:
#     yaml_object = yaml.safe_load(yaml_in) # yaml_object will be a list or a dict
#     json.dump(yaml_object, json_out)

# b = open('/home/sanches/projects/Campus-ON-Demand/example.json',)
# c = json.load(b)

# for item in c:
#     item['prices'][0]['price'] = 200

# print(c)


# sys.stdout.write(yaml.dump(json.load(b)))
# print(b)
# print('saída')
# print()

# a = open("/home/sanches/Downloads/yaml-validator.yaml",)

# b = yaml.full_load(a)

# b[0]['prices'][0]['price'] = 200
# b[1]['prices'][0]['price'] = 550

# sys.stdout.write(yaml.dump(b))

# try:s
# a = connection_openstack.create_user(name="username", password="password", domain_id='default')
# except identity. as e:
#     print("HUIASHSASAHDSA")
#     print(e)
# print(a)

# print("AAAA")
# print(a)
# print()
# print("sadASADSADSA")
# for item in connection_openstack.list_security_groups():
#     print(item.name)

# security_group = connection_openstack.network.create_security_group(
#         name='test4')
# print()
# print("AAASDAAS")
# print(security_group.name)

# print()
# print("result")
# print(security_group)
# test = connection_openstack.get_security_group('default')

# print()
# print("results")
# print(test.name, test.id)

# test = Services.select(Services.name)
# for item in test:
#     name = item.name
# # print(name)
# connection_openstack = create_connection_openstack("http://192.168.1.108/identity", 'RegionOne', 'admin', 'admin','stack','default','default')
# connection_openstack.create_group(name, "description", domain='default')


# cnx = create_connection_db('127.0.0.1', 3306, 'root','root','orchestrator_database')
# cnx = create_connection_db('orchestrator_database', 'root', 'root', '127.0.0.1', 3306)

# q = ((Services.insert(name="Campus ON Demand", token='abc123',creation_date='2021-04-03')).execute())

# test = Services.select(Services.name)

# for service in test:
#     print(service.name)

# url = "https://192.168.0.125:9999/osm/admin/v1/users"
# token = 'zKTzCn5a3cajfeI2psKjKF4tao2KpgNF'
# headers = {
# "Authorization": 'Bearer zKTzCn5a3cajfeI2psKjKF4tao2KpgNF'
# }

# user = {
#     "username": "teste",
#     "password": "123456",
# }

# response = requests.request("POST", url, headers=headers, json = user)
# print(response.status_code)


# openstack.enable_logging(True, stream=sys.stdout)
# config = loader.OpenStackConfig()


# def create_connection(auth_url, region, project_name, username, password,
#                       user_domain, project_domain):
#     return openstack.connect(
#         auth_url=auth_url,
#         project_name=project_name,
#         username=username,
#         password=password,
#         region_name=region,
#         user_domain_name=user_domain,
#         project_domain_name=project_domain,
#         app_name='examples',
#         app_version='1.0',
#     )

# connection = connection.Connection(auth_url = "http://192.168.1.108/identity", project_name= 'admin', username= 'admin', password='stack', user_domain_id='default', project_domain_id='default')


# projeto_teste = connection.identity.create_project(name="projeto_teste2",
#     description='projeto de teste')

# role = connection.identity.find_role("member")
# user = connection.identity.find_user("admin")
# project = connection.identity.find_project("projeto_teste2")

# connection.identity.assign_project_role_to_user(project, user, role)

# for projects in connection.identity.projects():
# print(projects.name)
# teste = connection.compute.


# ASSOCIANDO UM PROJETO A UM USUÁRIO E SUA DETERMINADA FUNÇÃO
# connection.identity.a('projeto_teste', 'admin', 'member')

#   auth_url: http://192.168.1.108/identity
#   password: stack
#   project_domain_id: default
#   project_name: alt_demo
#   user_domain_id: default
#   username: alt_demo
# identity_api_version: '3'
# region_name: RegionOne
# volume_api_version: '3'

# url = "http://127.0.0.1:5000/projects"
# headers = {
#     'Content-Type': 'application/json'
# }
# payload = {
#     "username": "admin",
#     "password": "admin",
#     "project_id": "admin",
#     "token": 'kkkkkkkkkkkkkkkkkkkkkk',
#     "name": "projeto teste",
#     "admin": False
# }

# response = requests.request('GET', url, headers=headers, json=payload, verify=False)
