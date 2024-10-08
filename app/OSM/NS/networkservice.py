from itertools import count
import time
from flask import jsonify
import requests
# from sqlalchemy import false, null
from urls import *
from operator import itemgetter


def get_compute_info():
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'}
        url = "http://10.50.0.161:5000/psutil"
        payload = {}
        response = requests.request(
            method="GET", url=url, headers=headers, json=payload, verify=False)

    except Exception as error:
        response = None
        # print(error)
    # +str(vimAccountId) eita carai!
    return response


def get_ns_resource(token, nsInstanceId):
    # /nslcm/v1/ns_instances/{nsInstanceId} Delete an individual NS instance resource
    # /nslcm/v1/ns_instances/{nsInstanceId}/terminate

    if type(token) is dict:
        tokenId = token['id']
    else:
        tokenId = token.replace('\r', '')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nslcm/v1/ns_instances/" + nsInstanceId
    url = url_osm + method_osm

    payload = {
    }

    response = requests.request(
        method="GET", url=url, headers=headers, data=payload, verify=False)

    return response.json()


def delete_ns_instantiate(token, nsdId_instance):
    # /nslcm/v1/ns_instances/{nsInstanceId} Delete an individual NS instance resource
    # /nslcm/v1/ns_instances/{nsInstanceId}/terminate
    if type(token) is dict:
        tokenId = token['id']
    else:
        tokenId = token.replace('\r', '')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nslcm/v1/ns_instances/" + nsdId_instance + "/terminate"
    url = url_osm + method_osm

    payload = {
        "autoremove": True
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    method_osm = "/nslcm/v1/ns_instances/" + nsdId_instance
    url = url_osm + method_osm

    finished = False
    while finished == False:
        response = requests.request(
            method="GET", url=url, headers=headers, verify=False)
        status = response.json()
        if 'code' in status:
            if status['code'] == 'NOT_FOUND':
                finished = True

    method_osm = "/nslcm/v1/ns_instances/" + nsdId_instance
    url = url_osm + method_osm

    payload = {
    }

    response = requests.request(
        method="DELETE", url=url, headers=headers, data=payload, verify=False)

    return response.text


def get_ns_info(token, ns_id):
    if type(token) is dict:
        token_id = token['id']
    else:
        token_id = token.replace('\r', '')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + token_id
    }
    method_osm = "/nslcm/v1/ns_instances/" + ns_id
    url = url_osm + method_osm
    response = requests.request(method="GET", url=url, headers=headers, verify=False)
    return response.json()


def get_instance_vnf(token):
    if type(token) is dict:
        tokenId = token['id']
    else:
        tokenId = token.replace('\r', '')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + str(tokenId)
    }
    method_osm = "nslcm/v1/vnf_instances/"
    url = url_osm + method_osm
    response = requests.request(method="GET", url=url, headers=headers, verify=False)
    return response.json()


def instantiate_ns(token, nsName, nsdId, vimAccountId):
    ns_description = 'incluir uma descrição?'
    if type(token) is dict:
        token_id = token['id']
    else:
        token_id = token.replace('\r', '')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + token_id
    }

    # print('1')
    method_osm = "/nslcm/v1/ns_instances/"
    url = url_osm + method_osm

    payload = {
        "nsName": nsName,
        "nsdId": nsdId,
        "vimAccountId": vimAccountId,
        "nsDescription": ns_description
    }
    # print(payload)
    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    # print(response.json())
    json = response.json()

    method_osm = "/nslcm/v1/ns_instances/" + json['id'] + "/instantiate/"
    url = url_osm + method_osm

    payload = {
        "nsName": nsName,
        "nsdId": json['id'],
        "vimAccountId": vimAccountId,
        "vld": [{
            "name": "dataNet",
            "vim-network-name": nsName + "rede-data"
        }]
    }

    # print(payload)
    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    # print('2')
    method_osm = "/nslcm/v1/ns_instances/" + json['id']
    url = url_osm + method_osm

    finished = False
    while not finished:
        # print('3')
        time.sleep(1)
        status = get_ns_info(token_id, json['id'])
        # print('4')
        # status = response.json()
        # print(status)
        # try:
        #     if status['deploymentStatus'] is not None:
        #         if 'vnfs' in status['deploymentStatus']:
        #             print(status['deploymentStatus']['vnfs'])
        #             print(len(status['deploymentStatus']['vnfs']))
        #         else:
        #             print(status['deploymentStatus'])
        #     else:
        #         print('sem indice deploymentStatus')
        # except Exception as error:
        #     print(error)

        # try:
        #     # print('')
        #     try:
        #         with open('helloworld_5vm_1vnf.txt', 'a') as filehandle:
        #             filehandle.write('\n' + str(status) + '\n')
        #     except Exception as error:
        #         print(error)
        # except Exception as error:
        #     print(error)

        # response = requests.request(
        #     method="GET", url=url, headers=headers, verify=False)
        # status = response.json()
        #
        # try:
        #     # try:
        #     #     with open('helloworld.txt', 'a') as filehandle:
        #     #         filehandle.write('\n'+str(status)+'\n')
        #     # except Exception as error:
        #     #     print(error)
        #
        #     log_ns_state = status['nsState']
        #     log_current_operation = status['currentOperation']
        #     log_operational_status = status['operational-status']
        #     log_orchestration_progress = status['orchestration-progress']
        #     log_config_status = status['config-status']
        #     log_detailed_status = status['detailed-status']
        #     print(log_ns_state, log_current_operation, log_operational_status,
        #           log_orchestration_progress,
        #           log_config_status, log_detailed_status)
        # except Exception as error:
        #     print('-')

        # print(status)

        if 'nsState' in status:
            if status['nsState'] == 'READY':
                finished = True

    return json


def delete_nsd(token, nsd_id):
    # /nsd/v1/ns_descriptors_content/{nsdInfoId} Delete an individual NS package resource

    if type(token) is dict:
        token_id = token['id']
    else:
        token_id = token.replace('\r', '')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + token_id
    }

    method_osm = "/nsd/v1/ns_descriptors_content/" + nsd_id
    url = url_osm + method_osm

    payload = {
    }

    response = requests.request(
        method="DELETE", url=url, headers=headers, data=payload, verify=False)

    return response.text


def compose_ns(token, json):
    if type(token) is dict:
        token_id = token['id']
    else:
        token_id = token.replace('\r', '')

    payload = json

    method_osm = "/nsd/v1/ns_descriptors_content/"
    url = url_osm + method_osm

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + token_id
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    id_json = response.json()
    if 'id' in id_json.keys():
        # id = id_json['id']
        return id_json['id']
    else:
        return id_json['code']


def create_vnffgd(json, cidr):
    payload = json

    vnffgd = {"name": "vnffg1-name",
              "short-name": "vnffg1-sname",
              "vendor": "vnffg1-vendor",
              "description": "vnffg1-description",
              "id": "vnffg1",
              "version": "1.0",
              "rsp": [],
              "classifier": []}

    rsp = {'id': 'rsp',
           'name': 'rspname',
           'vnfd-connection-point-ref': []}

    for vnf in sorted(payload.values(), key=itemgetter('order')):
        rsp_element = {}
        rsp_element["vnfd-id-ref"] = vnf["image"]
        rsp_element["member-vnf-index-ref"] = 100 + vnf["order"]
        rsp_element["vnfd-ingress-connection-point-ref"] = "vnf-data"
        rsp_element["vnfd-egress-connection-point-ref"] = "vnf-data"
        rsp_element["order"] = vnf["order"]
        rsp['vnfd-connection-point-ref'].append(rsp_element)

    # TODO - ATENÇÃO - ASSIM QUE CRIAR OS OBJETOS, VOU TER DE REESCREVER ESTE TRECHO,
    # POIS CADA DESKTOP DEVE TER SEU PROPRIO CLASSIFICADOR, NO CASO DESTE TESTBED A DISTINÇÃO SERÁ PELO
    #  source-ip-address, QUE TAMBEM NECESSITA ALTERAÇÃO NO member-vnf-index-ref, CONSIDERANDO O APENAS O FLUXO DE SAIDA
    # DOS DESKTOPS

    classifier = {}

    classifier["name"] = "class1name"
    classifier["vnfd-id-ref"] = "desktop_padrao_vnfd"
    classifier["vnfd-connection-point-ref"] = "vnf-data"
    classifier["member-vnf-index-ref"] = 11
    classifier["id"] = "class1"
    classifier["rsp-id-ref"] = "rsp"
    classifier["match-attributes"] = []

    classifier_match_att = {}
    classifier_match_att["destination-port"] = "5001:5011"
    classifier_match_att["id"] = "match1"
    classifier_match_att["ip-proto"] = 6  # TCP
    # classifier_match_att["ip-proto"]=17 # UDP
    # classifier_match_att["source-ip-address"]="10.10.10.11"
    classifier_match_att["source-ip-address"] = cidr.replace('.0/24', '.11')

    classifier["match-attributes"].append(classifier_match_att)

    vnffgd["rsp"].append(rsp)
    vnffgd["classifier"].append(classifier)

    return vnffgd


def create_nsd(nsd_name, cidr, json):
    payload = json

    d = {}
    d['nsd:nsd-catalog'] = {}

    nsd = {}
    nsd["id"] = "ID_" + nsd_name  # usar o ID que vai ser criado no BANCO
    nsd["name"] = nsd_name  # nsd["name"]="lab_nsd"
    nsd["short-name"] = nsd_name  # nsd["short-name"]="lab_nsd"
    nsd["vendor"] = "LABVER"
    nsd["description"] = payload["description"]  # nsd["description"]="Laboratorio Padrao"
    nsd["version"] = "1.0"

    vld = {}
    vld["short-name"] = "dataNet"
    vld["name"] = "dataNet"
    vld["type"] = "ELAN"
    vld["ip-profile-ref"] = "IP-t1"
    vld["id"] = "dataNet"
    vld["vnfd-connection-point-ref"] = []

    # Aqui é onde haverá dinamicidade da criação dos desktops, repetição do bloco de texto
    # para representar a quantidade de estações que serão disponibilizadas
    # os desktops dos alunos tem endereçamento IP, importante resgatar do BANCO DE DADOS qual
    # bloco de IP (rede) será usado
    # já as funções de rede virtualizadas, não possuem enredeços de IP predeterminados neste
    # momento ainda.

    for x in range(1, (payload["instances"] + 1)):
        vnfd_connection_point_ref = {"vnfd-connection-point-ref": "vnf-data",
                                     "vnfd-id-ref": payload["image"],
                                     "member-vnf-index-ref": 10 + x,
                                     "ip-address": cidr.replace('.0/24', '.' + str(10 + x))}
        # vnfd_connection_point_ref["ip-address"]="10.10.10."+str(10+x) #
        vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

    if payload["networkfunctions"]:
        vnf_id = 1
        for vnf in payload["networkfunctions"]:
            vnfd_connection_point_ref = {"vnfd-connection-point-ref": "vnf-data",
                                         "vnfd-id-ref": payload["networkfunctions"][vnf]["image"],
                                         "member-vnf-index-ref": 100 + payload["networkfunctions"][vnf]["order"],
                                         "ip-address": cidr.replace('.0/24', '.' + str(100 + vnf_id))}
            vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)
            vnf_id = vnf_id + 1

    # vnfd_connection_point_ref={}
    # vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
    # vnfd_connection_point_ref["vnfd-id-ref"]="desktop_padrao_vnfd"
    # vnfd_connection_point_ref["ip-address"]="10.10.10.11" # se for desktop, tem IP, se for VNF não

    # vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

    # já as funções de rede virtualizadas, não possuem enredeços de IP predeterminados neste
    # momento ainda.

    nsd["vld"] = []
    nsd["vld"].append(vld)

    ip_profiles = {}
    ip_profiles["description"] = "Descricao do perfil de IP"
    ip_profiles["name"] = "IP-t1"
    ip_profiles["ip-profile-params"] = {}

    dhcp_params = {}
    dhcp_params["count"] = 100
    dhcp_params["enabled"] = True
    # dhcp_params["start-address"]="10.10.10.10"
    dhcp_params["start-address"] = cidr.replace('.0/24', '.10')

    ip_profiles["ip-profile-params"]["dhcp-params"] = dhcp_params
    ip_profiles["ip-profile-params"]["dns-server"] = []
    dns_server = {}
    dns_server["address"] = "8.8.8.8"
    ip_profiles["ip-profile-params"]["dns-server"].append(dns_server)

    # ip_profiles["ip-profile-params"]["gateway-address"]="10.10.10.1"
    ip_profiles["ip-profile-params"]["gateway-address"] = cidr.replace('.0/24', '.1')
    ip_profiles["ip-profile-params"]["ip-version"] = "ipv4"
    # ip_profiles["ip-profile-params"]["subnet-address"]="10.10.10.0/24"
    ip_profiles["ip-profile-params"]["subnet-address"] = cidr

    constituent_vnfd = []
    cvnfd = {}
    # loop e append, quantas instances e funções de rede virtualizadas houverem

    for x in range(1, (payload["instances"] + 1)):
        cvnfd = {}
        cvnfd["member-vnf-index"] = 10 + x
        cvnfd["vnfd-id-ref"] = payload["image"]
        constituent_vnfd.append(cvnfd)

    if payload["networkfunctions"]:
        for vnf in payload["networkfunctions"]:
            cvnfd = {}
            cvnfd["member-vnf-index"] = 100 + payload["networkfunctions"][vnf]["order"]
            cvnfd["vnfd-id-ref"] = payload["networkfunctions"][vnf]["image"]
            constituent_vnfd.append(cvnfd)

    nsd["ip-profiles"] = []
    nsd["ip-profiles"].append(ip_profiles)

    nsd["constituent-vnfd"] = constituent_vnfd
    # nsd["constituent_vnfd"].append()

    sfc_enable = False
    # DESABILITANDO A UTILIZAÇÃO DO SFC NESTE MOMENTO
    if sfc_enable:
        if payload["networkfunctions"]:
            vnffgd = create_vnffgd(payload["networkfunctions"], cidr)
            nsd["vnffgd"] = []
            nsd["vnffgd"].append(vnffgd)
    # DESABILITANDO A UTILIZAÇÃO DO SFC NESTE MOMENTO

    d['nsd:nsd-catalog']["nsd"] = []
    d['nsd:nsd-catalog']["nsd"].append(nsd)

    # response = requests.request("POST", url, headers=headers, data=payload,verify=False)
    # print(response.text.encode('utf8'))
    # return response.text.encode('utf8')
    return d
