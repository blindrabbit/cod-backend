import requests
import mysql.connector
from enum import unique
from functools import partial
from peewee import *
# from app.OSM import user
from openstack import identity
from openstack.exceptions import OpenStackCloudException
from peewee import DateField, Model, PeeweeException
import requests
import openstack
from openstack.config import loader
import sys
from openstack import connection
import mysql.connector
import secrets
from openstack import exceptions
from openstack.identity.v3._proxy import *
import yaml
import json
from app.VIO.clouds.Openstack.connection.connection import *
from keystoneauth1 import loading
from keystoneauth1 import session as session
# from keystoneclient.v3 import client as client
from keystoneauth1.identity import v3
import bios
import os
import subprocess
import peewee
from openstack.identity.v3.domain import *
import json
import yaml
from flask import jsonify

# payload = {'project_name': 'casacasa',
#            }
# a = requests.request(
#     method="DELETE", url='http://192.168.0.109:8010/laboratory/', json=payload, verify=False)

# print(a.text)

# json pra criar usuario
# payload = {'username': 'nometeste9',
#            'password': 'nometeste',
#            'token': '4f0b281fa3473d187b9271e9a75f07',
#            'name': 'nometeste'
#            }


# a = requests.request(
#     method="POST", url='http://192.168.0.109:8010/user/', json=payload, verify=False)

# print(a.text)

# payload = {'username': 'test10',
#            'password': 'test10',
#            'project_name': 'lab_python',
#            'security_group_name': 'sg_serra-lab_python',
#            'project_id': 'df59761b78f84b6b8c6c91d52996a22d',
#            'description': 'kakakakakakak'
#            }


# payload = {
#     "vim_name": "Teste_VIM",
#     "description": "lllkkkkkk",
#     "laboratory_name": "lab_python",
#     "tipo_nuvem": "openstack",
#     "token": "kkkkkkoksa"
# }

# payload = {'project_name': 'lab_python',
#
# }

# --------------------------------token --------------


# headers = {
#     'Content-Type': 'application/json'
# }
# payload = {
#     "username": 'admin',
#     "password": 'admin',
#     "project_id": 'admin'
# }

# response = requests.request(method="POST", url='https://10.50.1.127:9999/osm/admin/v1/tokens', headers=headers,
#                             json=payload, verify=False)

# print(response.text)

# ---------------------token---------------------

# ----------------------------NS-----------------------------

# payload = {
#     "nsd:nsd-catalog": {
#         "nsd": [
#             {
#                 "short-name": "lab_nsd_teste",
#                 "vendor": "OSM",
#                 "description": "lab padrao",
#                 "vld": [{'id': 'dataNet', 'ip-profile-ref': 'IP-t1', 'name': 'dataNet', 'short-name': 'dataNet', 'type': 'ELAN', 'vnfd-connection-point-ref': [{'member-vnf-index-ref': 1, 'ip-address': '10.10.10.11', 'vnfd-connection-point-ref': 'vnf-data',
#                                                                                                                                                                 'vnfd-id-ref': 'desktop_padrao_vnfd'},
#                                                                                                                                                                {'member-vnf-index-ref': 101, 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd'}]}],

#                 'ip-profiles': [{'description': 'Rede de acesso dos desktops', 'ip-profile-params': {'dhcp-params': {'count': 100, 'enabled': True, 'start-address': '10.10.10.10'}, 'dns-server': [{'address': '8.8.8.8'}], 'ip-version': 'ipv4', 'gateway-address': '10.10.10.1', 'subnet-address': '10.10.10.0/24'}, 'name': 'IP-t1'}],
#                 'vnffgd': [{'id': 'vnffg1', 'name': 'vnffg1-name', 'short-name': 'vnffg1-sname', 'description': 'vnffg1-description', 'vendor': 'vnffg1-vendor', 'version': '1.0', 'classifier': [{'id': 'class1', 'member-vnf-index-ref': 1, 'name': 'class1name', 'rsp-id-ref': 'rsp101', 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'desktop_padrao_vnfd', 'match-attributes': [{'id': 'match1', 'ip-proto': 17, 'source-ip-address': '10.10.10.11', 'destination-port': '5001:5011'}]}],
#                             'rsp': [{'id': 'rsp101', 'name': 'rsp101name', 'vnfd-connection-point-ref': [{'member-vnf-index-ref': 101, 'order': 0, 'vnfd-egress-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd', 'vnfd-ingress-connection-point-ref': 'vnf-data'}]}]}],
#                 "constituent-vnfd": [{'member-vnf-index': 1, 'vnfd-id-ref': 'desktop_padrao_vnfd'}, {'member-vnf-index': 101, 'vnfd-id-ref': 'openwrt_vnfd'}],
#                 "version": "1.0",
#                 "id": "lab_nsd_teste",
#                 "name": "lab_nsd_teste"
#             }
#         ]
#     }
# }

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     "Authorization": 'Bearer RDyqp8dajJXkPJljfIOSOVdmw0703AAP'
# }

# response = requests.request(
#     method="POST", url='https://10.50.1.127:9999/osm/nsd/v1/ns_descriptors_content', headers=headers, json=payload, verify=False)

# print(response.text)


# ----------------------------------NS--------------------------------------------------


# -------------------------------------------ns schedule------------------------
# payload = {
#     "nsdId": "f1baa006-5695-401c-a1a5-6ffe058b7fe2",
#     "nsName": "lab_nsd_teste",
#     "nsDescription": "lab padrao",
#     "vimAccountId": "a466b6d6-70b7-4ee8-86e8-3d42da1bb7fb"
# }

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     "Authorization": 'Bearer s6HH4xQmp8BR351N3iK6ie4gtWHJvLjd'
# }

# response = requests.request(
#     method="POST", url='https://10.50.1.127:9999/osm/nslcm/v1/ns_instances', headers=headers, json=payload, verify=False)

# print(response.text)

# id_json = response.json()
# id = id_json['id']


# -------------------------------------------ns schedule------------------------


# --------------------------NS INSTANTIATE -------------------------------

# payload = {
#     "nsName": "lab_nsd_teste",
#     "nsdId": id,
#     "vimAccountId": "a466b6d6-70b7-4ee8-86e8-3d42da1bb7fb"
# }

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     "Authorization": 'Bearer s6HH4xQmp8BR351N3iK6ie4gtWHJvLjd'
# }

# response = requests.request(
#     method="POST", url='https://10.50.1.127:9999/osm/nslcm/v1/ns_instances/'+id+'/instantiate', headers=headers, json=payload, verify=False)

# print(response.text)


# -------------------------------NS INSTANTIATE -------------------------------


# -------------------------------NS STATUS -----------------------------------

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     "Authorization": 'Bearer s6HH4xQmp8BR351N3iK6ie4gtWHJvLjd'
# }

# finished = False
# while finished == False:
#     response = requests.request(
#         method="GET", url='https://10.50.1.127:9999/osm/nslcm/v1/ns_instances/'+id, headers=headers, verify=False)
#     status = response.json()
#     print("------------->", status['nsState'])
#     if status['nsState'] == 'READY':
#         finished = True


# -----------------------------------------------NS STATUS ---------------------------------

# connection_openstack = create_connection_openstack("https://200.137.75.159:5000/identity/",
#                                                    'RegionOne', 'PRJ_HARRISONSM',
#                                                    'harrisomsm', '$Andra101417', 'RegionOne', 'Default')

connection_openstack = create_connection_openstack("http://172.16.112.60:5000/v3",
                                                   'RegionOne', 'admin',
                                                   'admin', 'keystoneadmin', 'RegionOne', 'Default')

resp = connection_openstack.list_projects()

print(resp)

# image = connection_openstack.compute.find_image('cirros-0.5.1-x86_64')
# flavor = connection_openstack.compute.find_flavor('m1.large')
# network = connection_openstack.network.find_network('rede-data')
# server = connection_openstack.compute.create_server(
#     name='TESTE', image_id=image.id, flavor_id=flavor.id,
#     networks=[{"uuid": network.id}])

# print("meu server -> ",  server)

# server_test = connection_openstack.compute.wait_for_server(server)

# print(server_test)


# d = bios.read(
#     '/home/sanches/projects/Campus-ON-Demand/files/lab_nsdteste.yaml')


# d = bios.read(
#     '/home/sanches/projects/Campus-ON-Demand/files/lab_nsdteste.yaml')


# print(type(d))
# teste = json.dumps(d)
# print(type(teste))

# teste2 = json.loads(teste)
# print(type(teste2))


# a = requests.request(
#     method="POST", url='https://10.50.1.127:9999/osm/vnfpkgm/v1/vnf_packages', json=payload, headers=headers, verify=False)


# {'nsd:nsd-catalog':
#     {'nsd': [
#         {'constituent-vnfd':
#             [], 'description': 'Laboratorio Padrao',
#             'id': 'lab_nsd', 'name': 'lab_nsd',
#             'short-name': 'lab_nsd',
#             'vendor': 'OSM',
#             'version': '1.0',
#             'ip-profiles': [{'description': 'Rede de acesso dos desktops', 'ip-profile-params': {'dhcp-params': {'count': 100, 'enabled': True, 'start-address': '10.10.10.10'}, 'dns-server': [{'address': '8.8.8.8'}], 'ip-version': 'ipv4', 'gateway-address': '10.10.10.1', 'subnet-address': '10.10.10.0/24'}, 'name': 'IP-t1'}],
#          'vld': [{'id': 'dataNet', 'ip-profile-ref': 'IP-t1', 'name': 'dataNet', 'short-name': 'dataNet', 'type': 'ELAN',
#                   'vnfd-connection-point-ref': [{'member-vnf-index-ref': 1, 'ip-address': '10.10.10.11', 'vnfd-connection-point-ref': 'vnf-data',
#                                                  'vnfd-id-ref': 'desktop_padrao_vnfd'},
#                                                 {'member-vnf-index-ref': 101, 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd'}]}],
#          'vnffgd': [{'id': 'vnffg1', 'name': 'vnffg1-name', 'short-name': 'vnffg1-sname', 'description': 'vnffg1-description', 'vendor': 'vnffg1-vendor', 'version': '1.0', 'classifier': [{'id': 'class1', 'member-vnf-index-ref': 1, 'name': 'class1name', 'rsp-id-ref': 'rsp101', 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'desktop_padrao_vnfd', 'match-attributes': [{'id': 'match1', 'ip-proto': 17, 'source-ip-address': '10.10.10.11', 'destination-port': '5001:5011'}]}], 'rsp': [{'id': 'rsp101', 'name': 'rsp101name', 'vnfd-connection-point-ref': [{'member-vnf-index-ref': 101, 'order': 0, 'vnfd-egress-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd', 'vnfd-ingress-connection-point-ref': 'vnf-data'}]}]}]}]}}


# headers = {
#     'Content-Type': 'application/zip',
#     'Accept': 'application/zip',
#     "Authorization": 'Bearer Nq1Lv7Q9ZKRDhxoVnKUMQZU1utMaIy2l'
# }

# d = bios.read(
#     '/home/sanches/projects/Campus-ON-Demand/files/lab_nsdteste.yaml')

# teste = yaml.load(
#     '/home/sanches/projects/Campus-ON-Demand/files/lab_nsdteste.yaml')


# arq = open(
#     '/home/sanches/projects/Campus-ON-Demand/files/lab_nsdteste.yaml', 'rb')
# payload = {}


# response = requests.request(
#     method="POST", url='https://10.50.1.127:9999/osm/nsd/v1/ns_descriptors_content', headers=headers, data=payload, verify=False)

# print(response.text)


# {'n


# payload = {'username': 'test10',
#            'laboratory_name': 'projeto_test_front4',
#            'token': "269add21e1b01a62f8854b6e2a0e38"
#            }

# payload = {}

# a = requests.request(
#     method="POST", url='http://192.168.0.109:8010/NS/', json=payload)

# print(a.text)

# connection_openstack = create_connection_openstack("http://10.50.1.61/identity", 'RegionOne', 'admin',
#                                                    'admin', 'stack', 'default', 'default')

# connection_openstack.delete_project(
#     "HDUISADSIAOHDSASDAOIHSDAASDUIADSISASQSQJDSOIQHUIQOIQHUISADAS")

# data = tokens.create_token()
# token = data.split()[2].strip()

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     "Authorization": 'Bearer ' + token
# }


# print("----------->", data)
# print("token ", token)

# payload = {
#     "remove_project_role_mappings": [
#         {
#             "project": 'hsteste',
#             "role": 'project_admin'
#         }]
# }

# c = requests.request('PATCH', 'https://10.50.1.142:9999/osm/admin/v1/users/admin', headers=headers,
#                      json=payload, verify=False)

# print(c.text)


# print("REMOVI ROLE VOU DELETAR")

# payload = {}

# d = requests.request(
#     method="DELETE", url='https://10.50.1.142:9999/osm/admin/v1/projects/42c6badb-e498-469a-97db-8de2875f9d4d', headers=headers, data=payload, verify=False)

# print(d.text)
