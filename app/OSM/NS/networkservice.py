import requests
# from sqlalchemy import false, null
from urls import *
from operator import itemgetter


def get_ns_resource(token, nsInstanceId):
# /nslcm/v1/ns_instances/{nsInstanceId} Delete an individual NS instance resource
# /nslcm/v1/ns_instances/{nsInstanceId}/terminate

    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nslcm/v1/ns_instances/"+nsInstanceId
    url = url_osm+method_osm    

    payload = {
    }

    response = requests.request(
        method="GET", url=url, headers=headers, data=payload, verify=False)

    return response.json()


def delete_ns_instantiate(token, nsdId_instance):
# /nslcm/v1/ns_instances/{nsInstanceId} Delete an individual NS instance resource
# /nslcm/v1/ns_instances/{nsInstanceId}/terminate
    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nslcm/v1/ns_instances/"+nsdId_instance+"/terminate"
    url = url_osm+method_osm    

    payload = {
        "autoremove": True
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    method_osm = "/nslcm/v1/ns_instances/"+nsdId_instance
    url = url_osm+method_osm

    finished = False
    while finished == False:
        response = requests.request(
            method="GET", url=url, headers=headers, verify=False)
        status = response.json()
        if 'code' in status:
            if status['code'] == 'NOT_FOUND':
                finished = True

    method_osm = "/nslcm/v1/ns_instances/"+nsdId_instance
    url = url_osm+method_osm    

    payload = {
    }

    response = requests.request(
        method="DELETE", url=url, headers=headers, data=payload, verify=False)

    return response.text


def instantiate_ns(token, nsName, nsdId, vimAccountId):
    nsDescription = 'incluir uma descrição?'
    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nslcm/v1/ns_instances/"
    url = url_osm+method_osm    

    payload = {
        "nsdId": nsdId,
        "nsName": nsName,
        "nsDescription": nsDescription,
        "vimAccountId": vimAccountId
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    # print('Before Instantiate +++++++++++++++++++++++++++++++++++++++++')
    # print(response.json())
    json = response.json()
    print('---------------------------\n',json)

    method_osm = "/nslcm/v1/ns_instances/"+json['id']+"/instantiate/"
    url = url_osm+method_osm

    payload = {
        "nsName": nsName,
        "nsdId": json['id'],
        "vimAccountId": vimAccountId
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    # print('After Instantiate +++++++++++++++++++++++++++++++++++++++++')
    # print('nsdId ',json['id'])
    # print(response.json())
    method_osm = "/nslcm/v1/ns_instances/"+json['id']
    url = url_osm+method_osm    

    finished = False
    while finished == False:
        response = requests.request(
            method="GET", url=url, headers=headers, verify=False)
        status = response.json()
        if status['nsState'] == 'READY':
            finished = True

    return json

def delete_nsd(token, nsdId):
# /nsd/v1/ns_descriptors_content/{nsdInfoId} Delete an individual NS package resource    

    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    method_osm = "/nsd/v1/ns_descriptors_content/"+nsdId
    url = url_osm+method_osm    

    payload = {
    }

    response = requests.request(
        method="DELETE", url=url, headers=headers, data=payload, verify=False)

    return response.text

def compose_ns(token, json):
    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    payload = json

    method_osm = "/nsd/v1/ns_descriptors_content/"
    url = url_osm+method_osm

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer ' + tokenId
    }

    response = requests.request(
        method="POST", url=url, headers=headers, json=payload, verify=False)

    id_json = response.json()
    if 'id' in id_json.keys():
        # id = id_json['id']
        return id_json['id']
    else:            
        return id_json['code']

def create_vnffgd(json):
    payload = json

    vnffgd={}
    vnffgd["name"]= "vnffg1-name"
    vnffgd["short-name"]= "vnffg1-sname"
    vnffgd["vendor"]= "vnffg1-vendor"
    vnffgd["description"]= "vnffg1-description"
    vnffgd["id"]= "vnffg1"
    vnffgd["version"]= "1.0"
    vnffgd["rsp"]=[]
    vnffgd["classifier"]=[]

    rsp={}
    rsp['id'] = 'rsp'
    rsp['name'] = 'rspname'
    rsp['vnfd-connection-point-ref'] = []

    for vnf in sorted(payload.values(),key=itemgetter('order')):
        rsp_element={}
        rsp_element["vnfd-id-ref"]=vnf["image"]    
        rsp_element["member-vnf-index-ref"]=100+vnf["order"]
        rsp_element["vnfd-ingress-connection-point-ref"]="vnf-data"
        rsp_element["vnfd-egress-connection-point-ref"]="vnf-data"
        rsp_element["order"]=vnf["order"]
        rsp['vnfd-connection-point-ref'].append(rsp_element)

#TODO - ATENÇÃO - ASSIM QUE CRIAR OS OBJETOS, VOU TER DE REESCREVER ESTE TRECHO, 
# POIS CADA DESKTOP DEVE TER SEU PROPRIO CLASSIFICADOR, NO CASO DESTE TESTBED A DISTINÇÃO SERÁ PELO 
#  source-ip-address, QUE TAMBEM NECESSITA ALTERAÇÃO NO member-vnf-index-ref, CONSIDERANDO O APENAS O FLUXO DE SAIDA
# DOS DESKTOPS

    classifier={}

    classifier["name"]="class1name"
    classifier["vnfd-id-ref"]="desktop_padrao_vnfd"
    classifier["vnfd-connection-point-ref"]="vnf-data"
    classifier["member-vnf-index-ref"]=11
    classifier["id"]="class1"
    classifier["rsp-id-ref"]="rsp"
    classifier["match-attributes"]=[]

    classifier_match_att={}
    classifier_match_att["destination-port"]="5001:5011"
    classifier_match_att["id"]="match1"
    classifier_match_att["ip-proto"]=17
    classifier_match_att["source-ip-address"]="10.10.10.11"

    classifier["match-attributes"].append(classifier_match_att)

    vnffgd["rsp"].append(rsp)
    vnffgd["classifier"].append(classifier)

    return vnffgd

def create_nsd(nsd_name, json):
    payload = json

    d={}
    d['nsd:nsd-catalog']={}

    nsd={}    
    nsd["id"]="ID_"+nsd_name # usar o ID que vai ser criado no BANCO
    nsd["name"]=nsd_name #nsd["name"]="lab_nsd"
    nsd["short-name"]=nsd_name #nsd["short-name"]="lab_nsd"
    nsd["vendor"]="LABVER"
    nsd["description"]=payload["description"] #nsd["description"]="Laboratorio Padrao"
    nsd["version"]="1.0"

    vld={}
    vld["short-name"]="dataNet"
    vld["name"]="dataNet"    
    vld["type"]="ELAN"
    vld["ip-profile-ref"]="IP-t1"
    vld["id"]="dataNet"
    vld["vnfd-connection-point-ref"]=[]

    # Aqui é onde haverá dinamicidade da criação dos desktops, repetição do bloco de texto
    # para representar a quantidade de estações que serão disponibilizadas
    # os desktops dos alunos tem endereçamento IP, importante resgatar do BANCO DE DADOS qual
    # bloco de IP (rede) será usado
    # já as funções de rede virtualizadas, não possuem enredeços de IP predeterminados neste
    # momento ainda.

    for x in range(1, (payload["instances"]+1)):
        vnfd_connection_point_ref={}
        vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
        vnfd_connection_point_ref["vnfd-id-ref"]=payload["image"]
        vnfd_connection_point_ref["member-vnf-index-ref"]=10+x
        vnfd_connection_point_ref["ip-address"]="10.10.10."+str(10+x) #
        vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

    for vnf in payload["networkfunctions"]:
        vnfd_connection_point_ref={}
        vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
        vnfd_connection_point_ref["vnfd-id-ref"]=payload["networkfunctions"][vnf]["image"]    
        vnfd_connection_point_ref["member-vnf-index-ref"]=100+payload["networkfunctions"][vnf]["order"]
        vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

    # vnfd_connection_point_ref={}
    # vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
    # vnfd_connection_point_ref["vnfd-id-ref"]="desktop_padrao_vnfd"
    # vnfd_connection_point_ref["ip-address"]="10.10.10.11" # se for desktop, tem IP, se for VNF não

    # vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

    # já as funções de rede virtualizadas, não possuem enredeços de IP predeterminados neste
    # momento ainda.
 
    nsd["vld"]=[]
    nsd["vld"].append(vld)

    ip_profiles={}
    ip_profiles["description"]="Descricao do perfil de IP"
    ip_profiles["name"]="IP-t1"
    ip_profiles["ip-profile-params"]={}
 
    dhcp_params={}
    dhcp_params["count"]=100
    dhcp_params["enabled"]=True
    dhcp_params["start-address"]="10.10.10.10"

    ip_profiles["ip-profile-params"]["dhcp-params"]=dhcp_params
    ip_profiles["ip-profile-params"]["dns-server"]=[]
    dns_server={}
    dns_server["address"]="8.8.8.8"
    ip_profiles["ip-profile-params"]["dns-server"].append(dns_server)
    
    ip_profiles["ip-profile-params"]["gateway-address"]="10.10.10.1"
    ip_profiles["ip-profile-params"]["ip-version"]="ipv4"
    ip_profiles["ip-profile-params"]["subnet-address"]="10.10.10.0/24"
    
    constituent_vnfd=[]
    cvnfd={}
    #loop e append, quantas instances e funções de rede virtualizadas houverem

    for x in range(1, (payload["instances"]+1)):
        cvnfd={}
        cvnfd["member-vnf-index"]=10+x
        cvnfd["vnfd-id-ref"]=payload["image"]
        constituent_vnfd.append(cvnfd)

    for vnf in payload["networkfunctions"]:
        cvnfd={}
        cvnfd["member-vnf-index"]=100+payload["networkfunctions"][vnf]["order"]
        cvnfd["vnfd-id-ref"]=payload["networkfunctions"][vnf]["image"]
        constituent_vnfd.append(cvnfd)

    nsd["ip-profiles"]=[]
    nsd["ip-profiles"].append(ip_profiles)

    nsd["constituent-vnfd"]=constituent_vnfd
    # nsd["constituent_vnfd"].append()

    #DESABILITANDO A UTILIZAÇÃO DO SFC NESTE MOMENTO

    # vnffgd = create_vnffgd(payload["networkfunctions"])

    # nsd["vnffgd"]=[]
    # nsd["vnffgd"].append(vnffgd)

    d['nsd:nsd-catalog']["nsd"]=[]
    d['nsd:nsd-catalog']["nsd"].append(nsd)

    # response = requests.request("POST", url, headers=headers, data=payload,verify=False)
    # print(response.text.encode('utf8'))
    # return response.text.encode('utf8')
    return d