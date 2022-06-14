# Rodar em modo de debug - autoreload
# PS C:\Users\1918648\Documents\GitHub\Campus-ON-Demand\app> $env:FLASK_ENV="development"
# PS C:\Users\1918648\Documents\GitHub\Campus-ON-Demand\app> python -m flask run
# $env:OS_CLIENT_CONFIG_FILE="clouds.yaml"
import json
from OSM.project.project_OSM import *
# import bios
# from requests.api import head
from database.models import Services
from database.models import Server
from database.models import *
import requests
from OSM.project import *
from OSM.VIM import vim as OSMvim
from OSM.NS import networkservice as OSMNS
from OSM.tokens import tokens
from flask import Flask, request, jsonify, json
from database.models import *
from openstack import *
from VIO.clouds.Openstack.Apis.neutron.security_group import *
from VIO.clouds.Openstack.Apis.neutron.rules import *
from VIO.clouds.Openstack.Apis.neutron.network import *
from VIO.clouds.Openstack.Apis.keystone.user import *
from VIO.clouds.Openstack.Apis.keystone.project import *
from VIO.clouds.Openstack.Apis.nova.flavor import *
from VIO.clouds.Openstack.Apis.nova.instance import *
from VIO.clouds.Openstack.Apis.nova.VM import *
from VIO.clouds.Openstack.connection.connection import *
from urls import *
from env import *
from authentication.authentication import *
from openstack.exceptions import *
from flask_cors import CORS
from flask import Response
import time
# from keystoneclient.v3 import client
# from playhouse.shortcuts import model_to_dict
from benedict import benedict
from operator import itemgetter
from os import getenv
from random import randint

requests.packages.urllib3.disable_warnings()

def main():
    print ("Iniciando Serviço")
    app = Flask(__name__)
    CORS(app)

# @cross_origin()

# @app.errorhandler(404)
# def page_not_found(e):
#     # note that we set the 404 status explicitly
#     return "", 404

    @app.route("/delete_laboratory/<laboratory_id>/", methods=['POST', 'GET', 'DELETE'])
    def delete_laboratory(laboratory_id):
        cloud = 'openstack-serra'

        connection_openstack = create_connection_openstack_clouds_file(cloud)
        
        laboratory_from_bd = Laboratory.get_or_none(Laboratory.id_laboratory==laboratory_id)

        project_from_bd = Project.get_or_none(Project.id_laboratory==laboratory_id)

        if laboratory_from_bd:
            delete_router(project_from_bd.openstack_id_router,
                          project_from_bd.openstack_id_router_gateway_port, 
                          connection_openstack)
            delete_network(project_from_bd.openstack_id_network, connection_openstack)
            delete_project(project_from_bd.id_project, connection_openstack)
            laboratory_from_bd.delete_instance(recursive=True)

        return "<a href='/create_laboratory'>Criar novo laboratorio</a>"

    @app.route('/create_laboratory')
    def create_laboratory():
        cloud = 'openstack-serra'
        payload = REQUEST_POST1

        if Laboratory.get_or_none(Laboratory.name==payload['name']):
            return "ja tem com esse nome"

        laboratory_to_bd = Laboratory.create(
            name = payload['name'],
            classroom = payload['classroom'],
            description = payload['description'],
            instances = payload['instances'],
            fk_user = User.select().where(User.id_user=='1234567890')
        )

        connection_openstack = create_connection_openstack_clouds_file(cloud)

        username = 'renancs'
        project_name = LABVER_PREFIX+'labteste01'
        description = payload['description']
        conn = connection_openstack

        project = create_project(username, project_name, description, conn)

        project_to_bd = Project.create(
            id_project =  project['id'],
            name = project_name,
            fk_user = User.select().where(User.id_user=='1234567890'),
            fk_laboratory = laboratory_to_bd.id_laboratory,
            description = description
        )

        network = create_network(LABVER_PREFIX+'rede-data', project['id'], connection_openstack)

        cidr = '10.'+ str(randint(0, 254))+'.'+str(randint(0, 254))+'.0/24'
        gateway = cidr.replace('.0/24','.1')

        subnetwork = create_subnet(network['id'], LABVER_PREFIX+'subrede-data', 4, cidr, 
        gateway, connection_openstack)

        router_gateway_port = connection_openstack.create_port(
                network_id = network['id'],
                name = LABVER_PREFIX+'porta_roteador',
                admin_state_up = True,
                fixed_ips = [
                            {"ip_address": gateway, "subnet_id": subnetwork['id']},
                            ])
        provider_networt = connection_openstack.get_network('provider')

        router = create_router(LABVER_PREFIX+'roteador', provider_networt['id'], project['id'], connection_openstack)

        connection_openstack.add_router_interface(router=router,
                                                  subnet_id=subnetwork['id'],
                                                  port_id=router_gateway_port['id'])

        project_to_bd.cidr=cidr
        project_to_bd.gateway=gateway
        project_to_bd.openstack_id_router=router['id']
        project_to_bd.openstack_id_router_gateway_port=router_gateway_port['id']
        project_to_bd.openstack_id_subnet=subnetwork['id']
        project_to_bd.openstack_id_network=network['id']

        project_to_bd.save()
        id_do_lab = laboratory_to_bd.id_laboratory
        link = "<a href='/delete_laboratory/"+str(id_do_lab)+"'>Apagar o LAB - "+str(id_do_lab)+"</a>"

        user_from_bd = User.get_by_id('1234567890')

        if user_from_bd.token_OSM == '':
            token = benedict.from_yaml(tokens.create_token())
            token = token['id']
            user_from_bd.token_OSM=token
            user_from_bd.save()
        else:
            token = tokens.get_token_info(user_from_bd.token_OSM)

        vimAccountId = OSMvim.create_vim(token)
        # vimAccountId = {}
        # vimAccountId["id"] = "8f3c0414-0ee7-4afe-a2bb-fe089433cdce"
        # print(vimAccountId["id"])

        nsd = OSMNS.create_nsd(REQUEST_POST1)
        nsdId = OSMNS.compose_ns(token, nsd)
        nsName = REQUEST_POST['nome']

        nsdId_instance = OSMNS.instantiate_ns(token, nsName, nsdId, vimAccountId)

        print(nsdId, nsdId_instance)
        return link


    @app.route('/testemodel')
    def testemodel():
        a = 10 + 10
 
        laboratory_to_bd = Laboratory(
            name = REQUEST_POST['nome'],
            classroom = REQUEST_POST['turma'],
            description = REQUEST_POST['descricao'],
            instances = REQUEST_POST['instancias'],
            fk_user = User.select().where(User.id_user=='')
        )

        laboratory_to_bd.save()
        laboratory_to_bd.networkservice()
        
    # id_laboratory = BigIntegerField(primary_key=True, unique=True,
    #         constraints=[SQL('AUTO_INCREMENT')])
    # name = CharField(max_length=100)
    # classroom = CharField(max_length=100)
    # description = CharField(max_length=100)
    # instances = IntegerField()
    # dt_start = DateTimeField(default=datetime.now)
    # creation_date = DateTimeField(default=datetime.now)
    # fk_project = CharField(max_length=100)
    # # fk_network_service = ForeignKeyField(networkservice, backref='laboratory')
    # fk_user = ForeignKeyField(User, backref='laboratories')
        # server_from_bd = Server.get_or_none(id_server_openstack=data['server_id'])
        # if server_from_bd is None:
        #     id = Server.insert(
        #         name=data['server_nome'],
        #         id_server_openstack=data['server_id'],
        #         creation_date=time.time(),
        #         fk_project=data['project_id'],
        #         state='emuso',
        #         cookie='COKKIECOOKIE'
        #     ).on_conflict('replace').execute()


        return 'Vamos testar o modelo!'

    @app.route('/teste/', methods=['POST', 'GET', 'DELETE'])
    def teste():

        #recebe as informações do laboratorio do FRONEND
        # info_lab = request.get_json()

        #criação e persistencia do laboratorio no banco de dados

        # Pilha de criação de infraestrutura dentro do Openstack

        # VERIFICAR SE JÁ TEM ALGUM TOKEN, SE TIVER USAR O EXISTENTE
        # CONSULTAR NO BANCO DE DADOS NA TABELA LABORATORIO - A CRIAR
        token = tokens.create_token()
        # token = token['id']
        # Pilha de criação de infraestrutura dentro do OSM

        # SERÁ CRIADA UM VIM PARA CADA LABORATORIO
        # Descobrir como passar de modo seguro  a senha e o usuário da conta LABVER
        # para criação desta VIM
        # Passar o nome do projeto do novo laboratorio 
        # openstackUser = Usuário com poder de criação dentro do projeto criado
        # openstackPass = Senha do usuário
        # labProject = Nome do Projeto criado para o laboratorio

        # vimId = OSMvim.create_vim(token["id"], openstackUser, openstackPass, labProject)
        print('88888888888888888888888888888888888888888888888888888888888')
        print(token)
        teste = token['id']
        vimAccountId = OSMvim.create_vim(teste)
        # vimAccountId = {}
        # vimAccountId["id"] = "8f3c0414-0ee7-4afe-a2bb-fe089433cdce"
        # print(vimAccountId["id"])

        nsd = OSMNS.create_nsd(REQUEST_POST)
        nsdId = OSMNS.compose_ns(token, nsd)
        nsName = REQUEST_POST['nome']

        OSMNS.instantiate_ns(token, nsName, nsdId, vimAccountId["id"])
        # return str(retorno)
        return 'Hello World isso é um teste!!!'

    @app.route('/createLaboratory/', methods=['POST', 'GET', 'DELETE'])
    def createLaboratory():

        cloud = 'openstack-serra'
        payload = REQUEST_POST

        connection_openstack = create_connection_openstack_clouds_file(cloud)
        if request.method == 'GET':
            data = request.get_json()
            
            # nsd = OSMNS.create_nsd(payload)

            print("GET")
        if request.method == 'POST':
            
            print("POST")

        print("blabla")
        return nsd

    @app.route('/createNSD/', methods=['POST', 'GET', 'DELETE'])
    def createNSD():
    # informações recebidas do FRONTEND    
        # payload = {
        #     "nome": "nomecanonicodolaboratorio",
        #     "imagem": "desktop_padrao_vnfd",
        #     "turma": "codigodauturma",
        #     "instancias": 1,
        #     "descricao": "descricao informativa do laboratorio",
        #     "acessoainternet": True,
        #     "funcoesderede": {
        #         "vnf1": {
        #             "imagem": "openwrt_vnfd",
        #             "ordem": 0,
        #             "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
        #         },
        #     },
        # }

        # info_service = request.get_json()
        # if request.method == 'POST':
        #     print("CHEGOU POR POST "&info_service)
        payload = REQUEST_POST
        d={}
        d['nsd:nsd-catalog']={}

        nsd={}    
        nsd["id"]="lab_nsdeumtesteamaisdiferente"
        nsd["name"]=payload["nome"] #nsd["name"]="lab_nsd"
        nsd["short-name"]=payload["nome"] #nsd["short-name"]="lab_nsd"
        nsd["vendor"]="OSM"
        nsd["description"]=payload["descricao"] #nsd["description"]="Laboratorio Padrao"
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

        for x in range(1, (payload["instancias"]+1)):
            vnfd_connection_point_ref={}
            vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
            vnfd_connection_point_ref["vnfd-id-ref"]=payload["imagem"]
            vnfd_connection_point_ref["member-vnf-index-ref"]=10+x
            vnfd_connection_point_ref["ip-address"]="10.10.10."+str(10+x) #
            vld["vnfd-connection-point-ref"].append(vnfd_connection_point_ref)

        for vnf in payload["funcoesderede"]:
            vnfd_connection_point_ref={}
            vnfd_connection_point_ref["vnfd-connection-point-ref"]="vnf-data"
            vnfd_connection_point_ref["vnfd-id-ref"]=payload["funcoesderede"][vnf]["imagem"]    
            vnfd_connection_point_ref["member-vnf-index-ref"]=100+payload["funcoesderede"][vnf]["ordem"]
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
        #loop e append, quantas instancias e funções de rede virtualizadas houverem

        for x in range(1, (payload["instancias"]+1)):
            cvnfd={}
            cvnfd["member-vnf-index"]=10+x
            cvnfd["vnfd-id-ref"]=payload["imagem"]
            constituent_vnfd.append(cvnfd)

        for vnf in payload["funcoesderede"]:
            cvnfd={}
            cvnfd["member-vnf-index"]=100+payload["funcoesderede"][vnf]["ordem"]
            cvnfd["vnfd-id-ref"]=payload["funcoesderede"][vnf]["imagem"]
            constituent_vnfd.append(cvnfd)

        # cvnfd["member-vnf-index"]=1
        # cvnfd["vnfd-id-ref"]=1
        # constituent_vnfd.append(cvnfd)

        vnffgd={}
        vnffgd["name"]= "vnffg1-name"
        vnffgd["short-name"]= "vnffg1-sname"
        vnffgd["vendor"]= "vnffg1-vendor"
        vnffgd["description"]= "vnffg1-description"
        vnffgd["id"]= "vnffg1"
        vnffgd["version"]= "1.0"
        vnffgd["rsp"]=[]
        vnffgd["classifier"]=[]

        rsp=[]
        #loop para quantidade de funções de rede virutalizadas que o SFC irá seguir
        for vnf in sorted(payload["funcoesderede"].values(),key=itemgetter('ordem')):
            rsp_element={}
            rsp_element["vnfd-id-ref"]=vnf["imagem"]    
            rsp_element["member-vnf-index-ref"]=100+vnf["ordem"]
            rsp_element["vnfd-ingress-connection-point-ref"]="vnf-data"
            rsp_element["vnfd-egress-connection-point-ref"]="vnf-data"
            rsp_element["order"]=vnf["ordem"]
            rsp.append(rsp_element)
            
        # rsp_element={}
        # rsp_element["vnfd-id-ref"]="openwrt_vnfd"
        # rsp_element["member-vnf-index-ref"]=101
        # rsp_element["vnfd-ingress-connection-point-ref"]="vnf-data"
        # rsp_element["vnfd-egress-connection-point-ref"]="vnf-data"
        # rsp_element["order"]=0
        # rsp.append(rsp_element)

        classifier={}

        classifier["name"]="class1name"
        classifier["vnfd-id-ref"]="desktop_padrao_vnfd"
        classifier["vnfd-connection-point-ref"]="vnf-data"
        classifier["member-vnf-index-ref"]=1
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

        nsd["ip-profiles"]=[]
        nsd["ip-profiles"].append(ip_profiles)

        nsd["constituent-vnfd"]=constituent_vnfd
        # nsd["constituent_vnfd"].append()

        nsd["vnffgd"]=[]
        nsd["vnffgd"].append(vnffgd)

        d['nsd:nsd-catalog']["nsd"]=[]
        d['nsd:nsd-catalog']["nsd"].append(nsd)

        # d['chave1']='1'
        # print(d)

        token = benedict.from_yaml(tokens.create_token())
        # print(token["id"])
        json_object = json.dumps(d, indent = 4)
        print(json_object)
        #token["id"]
        # retorno = OSMNS.create_nsd(json_object)
        # print(json_object)
        return str(json_object)

    @app.route('/listImages/', methods=['POST', 'GET', 'DELETE'])
    def listImages():
        cloud = 'openstack-serra'
        connection_openstack = create_connection_openstack_clouds_file(cloud)
        images=[]
        for image in connection_openstack.list_images():        
            if 'is_lab_allowed' in image['metadata']:            
                # ativo = server["metadata"]["ativo"]
                # este é um teste print(image)

                dic = {'id':image['id'], 'name':image['name']}
                print(dic)
                images.append(dic)
        return jsonify(images)

    @app.route('/osm/criarnetworkservice/', methods=['POST', 'GET', 'DELETE'])
    def osmNS():
        token = tokens.create_token()
        print(token)
        d = benedict.from_yaml(token)
        networkService={}

        # as opções dos DESKTOPs JA EXISTEm
        # As VNFs já EXISTEM
        # é necessário montar o NETWORKSERVICE
        # INFORMAÇÕES DO PORTAL DO PROFESSOR
        # NECESSÁRIO A INFORMAÇÃO DA SEQUENCIA DAS VNFS
        # 
    # informações recebidas do FRONTEND    
        payload = {
            'nome': "nomecanonicodolaboratorio",
            "imagem": "nomedoVNFdesktop",
            "turma": "codigodauturma",
            "instancias": 10,
            "descricao": "descrição informativa do laboratorio",
            "acessoainternet": True,
            "funcoesderede": {
                "vnf1": {
                    "imagem": "nomedoVNFdafuncaoderede",
                    "ordem": 1,
                    "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
                },
                "vnf2": {
                    "imagem": "nomedoVNFdafuncaoderede",
                    "ordem": 6,
                    "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
                },
                "vnf3": {
                    "imagem": "nomedoVNFdafuncaoderede",
                    "ordem": 0,
                    "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
                },
                "vnf4": {
                    "imagem": "nomedoVNFdafuncaoderede",
                    "ordem": 3,
                    "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
                },
            },
        }

        # for vnf in sorted(payload["funcoesderede"].values(),key=itemgetter('ordem')):
        #     print(vnf["ordem"])

        teste = OSMNS.create_nsd(payload)
        return teste    
    #     for key in a_dict:
    # ...     print(key, '->', a_dict[key])

        # OSMvim.create_vim(token["id"])
        # vimcreate_vim("tete")
        vim_ = OSMvim.get_vim_accounts(d["_id"])
        # tipo =  str(type(token))
        print(vim_)
        return (vim_)
        # return d["_id"]
        # return type(token)

    @app.route('/listarprojetos/', methods=['POST', 'GET', 'DELETE'])
    def listarprojetos():

        info_service = request.get_json()
        if request.method == 'GET':
            # print(info_service)

            auth_url = "http://172.16.112.60:5000/v3"
            region = 'RegionOne'
            project_name = 'lab-sfc'
            username = 'vdi'
            password = '123456'
            # username = 'admin'
            # password = 'keystoneadmin'
            user_domain = 'default'
            project_domain = 'default'
            connection_openstack = create_connection_openstack(auth_url, region, project_name, username, password,
                                                            user_domain, project_domain)
            lista_projetos = []
            filter = "[?contains(to_string(description),`teste`)]"
            for projeto in connection_openstack.list_projects(filters=filter):

                nome = projeto['name']
                id = projeto['id']
                descricao = projeto["description"]
                lista_projetos.append(
                    {"id": id, "nome": nome, "description": descricao})

            connection_openstack.close
            return jsonify(lista_projetos)

    @app.route("/vdi/<project_id>/<project_name>/", methods=['POST', 'GET', 'DELETE'])
    def virtual_desktop(project_id, project_name):
        if request.method == 'GET':
            # print(info_service)
            auth_url = "http://172.16.112.60:5000/v3"
            region = 'RegionOne'
            username = 'vdi'
            password = '123456'
            user_domain = 'default'
            project_domain = 'default'
            connection_openstack = create_connection_openstack(auth_url, region, project_name, username, password,
                                                            user_domain, project_domain)
            lista_console = []

            conn = connection_openstack
            filter = ""
            for server in conn.list_servers(filters=filter):
                ativo = None
                if "ativo" in server["metadata"]:
                    ativo = server["metadata"]["ativo"]
                elif ativo is None:
                    server_from_bd=Server.get_or_none(Server.id_server_openstack==server['id'], Server.state!="")
                    if server_from_bd is None:
                        nome = server['name']
                        id = server['id']
                        console_url = connection_openstack.compute.get_server_console_url(server['id'], "novnc")
                        tipo = console_url["type"]
                        url = console_url["url"]
                        url_console = {"id": id, "projeto_id": project_id,
                                    "nome": nome, "url": url, "tipo": tipo, "ativo": ativo}
                        lista_console.append(url_console)
            return jsonify(lista_console)

    @app.route('/authentication/', methods=['POST', 'GET', 'DELETE', 'UPDATE'])
    def authentication():
        info_service = request.get_json()
        nome = info_service['nome']

        if request.method == 'POST':
            try:
                token = create_authentication(nome)
                print("TOKEN: " + token)
            except HttpException as e:
                return "token ja existente", 400

            auth_url = "http://172.16.112.60:5000/v3"
            region = 'RegionOne'
            project_name = 'admin'
            username = 'admin'
            password = 'keystoneadmin'
            user_domain = 'default'
            project_domain = 'default'
            connection_openstack = create_connection_openstack(auth_url, region, project_name, username, password,
                                                            user_domain, project_domain)
            print(connection_openstack)

            try:
                connection_openstack.create_group(
                    nome, "description", domain='default')
                print("connection_openstack.create_group")
            except ConflictException as e:
                print("ConflictException")
                print(e)
                return "", 400

            connection_openstack.close()

            return token

        elif request.method == "UPDATE":
            new_name = info_service['new_name']
            return Services.update({Services.name: new_name}).where(Services.name == new_name).execute()

        elif request.method == 'GET':
            pass

    @app.route("/user/", methods=['POST', 'GET', 'DELETE'])
    def users():
        info_user = request.get_json()
        token = info_user['token']
        username = info_user['username']
        password = info_user['password']
        name = info_user['name']
        service = verify_service_authentication(token)
        if service == -1:
            return "authentication invalid"
        else:
            connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                            'RegionOne', 'admin', 'admin', 'stack',
                                                            'default', 'default')
            if request.method == "POST":
                start = time.time()

                try:
                    user = create_user_in_openstack(
                        username, password, connection_openstack)
                except ConflictException as e:
                    return str(e)

                id_openstack = user.id
                save_user_db(name, username, password,
                            id_openstack)

                end = time.time()
                elapsed = end - start
                print("tempo da requisição: ", elapsed)

                return user


    @app.route("/server/", methods=['POST', 'GET', 'DELETE', 'UPDATE'])
    def server():
        auth_url = "http://172.16.112.60:5000/v3"
        region = 'RegionOne'
        project_name = 'admin'
        username = 'admin'
        password = 'keystoneadmin'
        user_domain = 'default'
        project_domain = 'default'
        connection_openstack = create_connection_openstack(auth_url, region, project_name, username, password,
                                                        user_domain, project_domain)
        if request.method == "POST":
            data = request.get_json()

            try:
                server_from_bd = Server.get_or_none(id_server_openstack=data['server_id'])
                if server_from_bd is None:
                    id = Server.insert(
                        name=data['server_nome'],
                        id_server_openstack=data['server_id'],
                        creation_date=time.time(),
                        fk_project=data['project_id'],
                        state='emuso',
                        cookie='COKKIECOOKIE'
                    ).on_conflict('replace').execute()

                elif data['is_server_ativo'] == 'desconectar':
                    print("acessar a VM em uso previamente - COOKIE")
                    server_id = data['server_id']
                    Server.update({Server.state: ''}).where(Server.id_server_openstack == server_id).execute()
                else:
                    print("acessar uma nova VM")
                    server_id = data['server_id']
                    Server.update({Server.state: 'emuso'}).where(Server.id_server_openstack == server_id).execute()

                # if data['is_server_ativo'] == 'desconectar':
                #     print("liberar a VM")
                #     server_id = data['server_id']
                #     Server.update({Server.state: ''}).where(Server.id_server_openstack == server_id).execute()

            except HttpException as e:
                return "Erro não tratado.", 400

            return True

    @app.route('/laboratory/', methods=['POST', 'GET', 'DELETE'])
    def projects():

        if request.method == 'GET':
            info = request.headers
            token = info['token']
            username = info['username']

            projects_user = list_projects_per_user(username)
            # buscar depois os projetos no banco

            return jsonify(projects_user)

        elif request.method == 'POST':
            start = time.time()

            info_user = request.get_json()
            token = info_user['token']
            username = info_user['username']
            project_name = info_user['laboratory_name']
            service = verify_service_authentication(token)
            token_osm = "fdfsss"
            admin = True

            connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                            'RegionOne', 'admin', 'admin',
                                                            'stack', 'default', 'default')

            if service == -1:
                return "authentication invalid"
            else:
                exist = False
                for projects in connection_openstack.list_projects():
                    if projects == project_name:
                        exist = True
                if exist:
                    return "", 400
                else:
                    project_openstack = create_project(
                        username, project_name, "kkkkkkkkkkkkkkkkkkkk", connection_openstack)
                    connection_openstack.close()
                    resp = create_project_OSM(project_name, token_osm, admin)

                    id_OSM = resp.split()[2].strip('"')

                    data = tokens.create_token()
                    token = data.split()[2].strip()

                    payload = {
                        "add_project_role_mappings": [
                            {
                                "project": project_name,
                                "role": 'project_admin'
                            }]
                    }

                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": 'Bearer ' + token
                    }

                    resp = requests.request('PATCH', url_associate, headers=headers,
                                            json=payload, verify=False)

                    id_openstack = project_openstack.id
                    save_project_db(id_openstack, project_name, username,
                                    id_openstack, id_OSM)

                    end = time.time()
                    elapsed = end - start
                    print("tempo da requisição: ", elapsed)
                    print(id_OSM)

                    return project_openstack

        elif request.method == 'DELETE':
            start = time.time()
            info_user = request.get_json()
            project_name = info_user['project_name']

            connection_openstack = create_connection_openstack("http://10.50.1.61/identity", 'RegionOne', 'admin',
                                                            'admin', 'stack', 'default', 'default')

            connection_openstack.delete_project(project_name)

            data = tokens.create_token()
            token = data.split()[2].strip()
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            payload = {
                "remove_project_role_mappings": [
                    {
                        "project": project_name,
                        "role": 'project_admin'
                    }]
            }

            resp = requests.request('PATCH', 'https://10.50.1.142:9999/osm/admin/v1/users/admin', headers=headers,
                                    json=payload, verify=False)

            data = tokens.create_token()
            token = data.split()[2].strip()
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            id_OSM_Delete = delete_project_db(project_name)
            resp = requests.request(
                method="DELETE", url='https://10.50.1.142:9999/osm/admin/v1/projects/' + str(id_OSM_Delete), headers=headers, verify=False)

            return resp.text


    @ app.route('/VNF/', methods=['POST', 'GET', 'DELETE'])
    def VNF():

        if request.method == 'POST':

            info_user = request.get_json()
            # token = info_user['token']
            projeto_openstack = info_user['project_name']
            LABORATORIO_VNF = ["openwrt"]
            LABORATORIO_SITES_ALLOWED = ["github.com", "terra.com.br"]

            # TAMBÉM PODE SER DESKTOP PADRÃO
            # EXISTEM ALGUMAS CONFIGURAÇÕES QUE SERÃO FEITAS VIA FIREWALL
            # if LABORATORIO_VNF[0] == "openwrt":
            # Controle Parental
            # Liberar acesso a um Dominio
            # my_file = open(
            #     "/home/sanches/projects/Campus-ON-Demand/files/cloud-config-openwrt.txt")
            # string_list = my_file.readlines()
            # my_file.close()
            # indice = string_list.index('        # REGRAS INICIO #\n')+1
            # while string_list[indice] != '        # REGRAS FIM #\n':
            #     string_list.pop(indice)
            # for sites in LABORATORIO_SITES_ALLOWED:
            #     url = '        iptables -A OUTPUT -p tcp -d ' + sites + ' --dport 80 -j ACCEPT\n'
            #     string_list.insert(indice, url)
            # new_file_contents = "".join(string_list)
            # print(new_file_contents)
            # my_file = open(
            #     "/home/sanches/projects/Campus-ON-Demand/files/cloud-config-openwrt.txt", "w")
            # new_file_contents = "".join(string_list)
            # my_file.write(new_file_contents)
            # my_file.close()

            # d = bios.read(
            #     '/home/sanches/projects/Campus-ON-Demand/files/openwrt_vnfd.yaml')

            payload = "d"

            print(payload)
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                "Authorization": 'Bearer ' + "jdsiauhjdsiaojsda"
            }

            response = requests.request("POST", url_vnf, headers=headers,
                                        json=payload, verify=False)

            projeto_openstack = projeto_openstack
            if response.status_code == 401:
                data = tokens.create_token(project_id=projeto_openstack)
                token = data.split()[2].strip()

                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    "Authorization": 'Bearer ' + token
                }
                response = requests.request(method="POST", url=url_vnf, headers=headers,
                                            json=payload, verify=False)

                return response.text

            return(response.text)


    @ app.route('/vim/', methods=['POST', 'GET', 'DELETE'])
    def vim():
        info_user = request.get_json()

        token = info_user['token']
        vim_name = info_user['vim_name']
        description = info_user['description']
        vim_type = info_user['tipo_nuvem']
        vim_url = "http://10.50.1.61/identity"
        projeto_openstack = info_user['laboratory_name']

        # A VIM TEM QUE SER COM ADMIN. VERIFICAR ISSO MELHOR DEPOIS
        if request.method == 'POST':

            payload = {
                'name': vim_name,
                'description': description,
                'vim_type': vim_type,
                'vim_url': vim_url,
                'vim_tenant_name': 'admin',
                'vim_user': 'admin',
                'vim_password': 'stack',
                'schema_version': '1.0'
            }

            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                "Authorization": 'Bearer ' + token

            }

            response = requests.request(method="POST", url=url_vim,
                                        headers=headers, json=payload, verify=False)

            if response.status_code == 401:
                data = tokens.create_token(project_id=projeto_openstack)
                token = data.split()[2].strip()

                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    "Authorization": 'Bearer ' + token
                }
                response = requests.request(method="POST", url=url_vim, headers=headers,
                                            json=payload, verify=False)

                return response.text

            return(response.text)

    @ app.route("/security_group/", methods=['POST', 'GET', 'DELETE'])
    def security_groups():
        info_user = request.get_json()
        username = info_user['username']
        password = info_user['password']
        project_name = info_user['project_name']
        security_group_name = info_user['security_group_name']
        project_id = info_user['project_id']
        description = info_user['description']
        connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                        'RegionOne', project_name,
                                                        username, password, 'default',
                                                        'default')
        if request.method == 'POST':
            start = time.time()

            security_group = create_security_groups(security_group_name, project_id,
                                                    description, connection_openstack)
            connection_openstack.close()
            end = time.time()
            elapsed = end - start
            print("tempo da requisição: ", elapsed)

            return security_group

        elif request.method == 'GET':
            security_group = get_security_groups(
                security_group_name, connection_openstack)
            connection_openstack.close()

            return security_group

        elif request.method == 'DELETE':
            confirm = del_security_groups(
                security_group_name, connection_openstack)
            connection_openstack.close()

            return confirm


    @ app.route("/rules/", methods=['POST', 'GET', 'DELETE'])
    def rules():
        info_user = request.get_json()
        username = info_user['username']
        password = info_user['password']
        security_group_id = info_user['security_group_id']
        direction = info_user['direction']
        remote_ip_prefix = info_user['remote_ip_prefix']
        protocol = info_user['protocol']
        port_range_max = info_user['port_range_max']
        port_range_min = info_user['port_range_min']
        ethertype = info_user['ethertype']
        project_name = info_user['laboratory_name']

        connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                        'RegionOne', project_name,
                                                        username, password, 'default',
                                                        'default')

        if request.method == 'POST':
            start = time.time()

            rules = create_rules_to_secutity_groups(security_group_id, direction, remote_ip_prefix,
                                                    protocol, port_range_max, port_range_min,
                                                    ethertype, connection_openstack)
            end = time.time()
            elapsed = end - start
            print("tempo da requisição: ", elapsed)

            return rules

        pass


    @ app.route("/network/", methods=['POST', 'GET', 'DELETE'])
    def network():
        info_user = request.get_json()
        username = info_user['username']
        password = info_user['password']
        project_name = info_user['project_name']
        name_network = info_user["name_network"]
        connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                        'RegionOne', project_name,
                                                        username, password, 'default',
                                                        'default')

        if request.method == 'POST':
            network = create_network(name_network, connection_openstack)

            return network

        else:
            pass


    @ app.route("/subnet/", methods=['POST', 'GET', 'DELETE'])
    def subnet():
        info_user = request.get_json()
        username = info_user['username']
        password = info_user['password']
        project_name = info_user['project_name']
        connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                        'RegionOne', project_name,
                                                        username, password, 'default',
                                                        'default')

        subnet_name = info_user['name_subnet']
        network_id = info_user['network_id']
        ip_version = info_user['ip_version']
        cidr = info_user['cidr']
        gateway_ip = info_user['gateway_ip']

        if request.method == 'POST':
            subnet = create_subnet(network_id, subnet_name, ip_version, cidr,
                                gateway_ip, connection_openstack)
            return subnet

        else:
            pass

    @ app.route("/image/", methods=['POST', 'GET', 'DELETE'])
    def image():
        pass


    @ app.route("/flavors/", methods=['POST', 'GET', 'DELETE'])
    def flavors():
        info_user = request.get_json()
        name = info_user['name']
        vcpus = info_user['vcpus']
        disk = info_user['disk']
        ram = info_user['ram']
        ephemeral = info_user['ephemeral']
        is_public = False
        project_id = info_user['laboratory_id']

        connection_openstack = create_connection_openstack("http://10.50.1.61/identity",
                                                        'RegionOne', 'admin',
                                                        'admin', 'stack', 'default', 'default')

        if request.method == 'POST':

            flavor = create_flavor(name, ram, vcpus, disk, ephemeral, is_public,
                                project_id, connection_openstack)

            return flavor


    @ app.route("/NS/", methods=['POST', 'GET', 'DELETE'])
    def instantiate():

        # if request.method == 'POST':
            start = time.time()
            headers = {
                'Content-Type': 'application/json'
            }

            payload = {
                "username": 'admin',
                "password": 'admin',
                "project_id": 'admin'
            }

            # response = requests.request(method="POST", url='https://10.50.1.56:9999/osm/admin/v1/tokens', headers=headers,
                                        # json=payload, verify=False)

            # teste = response.text
            teste = tokens.create_token
            token = teste().split()[2].strip()

            payload = {
                "nsd:nsd-catalog": {
                    "nsd": [
                        {
                            "short-name": "lab_nsd_teste1",
                            "vendor": "OSM",
                            "description": "lab padrao",
                            "vld": [{'id': 'dataNet', 'ip-profile-ref': 'IP-t1', 'name': 'dataNet', 'short-name': 'dataNet', 'type': 'ELAN', 'vnfd-connection-point-ref': [{'member-vnf-index-ref': 1, 'ip-address': '10.10.10.11', 'vnfd-connection-point-ref': 'vnf-data',
                                                                                                                                                                            'vnfd-id-ref': 'desktop_padrao_vnfd'},
                                                                                                                                                                        {'member-vnf-index-ref': 101, 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd'}]}],

                            'ip-profiles': [{'description': 'Rede de acesso dos desktops', 'ip-profile-params': {'dhcp-params': {'count': 100, 'enabled': True, 'start-address': '10.10.10.10'}, 'dns-server': [{'address': '8.8.8.8'}], 'ip-version': 'ipv4', 'gateway-address': '10.10.10.1', 'subnet-address': '10.10.10.0/24'}, 'name': 'IP-t1'}],
                            'vnffgd': [{'id': 'vnffg1', 'name': 'vnffg1-name', 'short-name': 'vnffg1-sname', 'description': 'vnffg1-description', 'vendor': 'vnffg1-vendor', 'version': '1.0', 'classifier': [{'id': 'class1', 'member-vnf-index-ref': 1, 'name': 'class1name', 'rsp-id-ref': 'rsp101', 'vnfd-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'desktop_padrao_vnfd', 'match-attributes': [{'id': 'match1', 'ip-proto': 17, 'source-ip-address': '10.10.10.11', 'destination-port': '5001:5011'}]}],
                                        'rsp': [{'id': 'rsp101', 'name': 'rsp101name', 'vnfd-connection-point-ref': [{'member-vnf-index-ref': 101, 'order': 0, 'vnfd-egress-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd', 'vnfd-ingress-connection-point-ref': 'vnf-data'}]}]}],
                            "constituent-vnfd": [{'member-vnf-index': 1, 'vnfd-id-ref': 'desktop_padrao_vnfd'}, {'member-vnf-index': 101, 'vnfd-id-ref': 'openwrt_vnfd'}],
                            "version": "1.0",
                            "id": "lab_nsd_teste1",
                            "name": "lab_nsd_teste1"
                        }
                    ]
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            response = requests.request(
                method="POST", url='https://10.50.1.56:9999/osm/nsd/v1/ns_descriptors_content', headers=headers, json=payload, verify=False)

            id_json = response.json()
            if 'id' in id_json.keys():
                id = id_json['id']
            else:            
                return id_json['code']

            payload = {
                "nsdId": id,
                "nsName": "lab_nsd_teste",
                "nsDescription": "lab padrao",
                "vimAccountId": "a466b6d6-70b7-4ee8-86e8-3d42da1bb7fb"
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            response = requests.request(
                method="POST", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances', headers=headers, json=payload, verify=False)

            id_json = response.json()
            id = id_json['id']

            payload = {
                "nsName": "lab_nsd_teste",
                "nsdId": id,
                "vimAccountId": "a466b6d6-70b7-4ee8-86e8-3d42da1bb7fb"
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            response = requests.request(
                method="POST", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances/'+id+'/instantiate', headers=headers, json=payload, verify=False)

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            finished = False
            while finished == False:
                response = requests.request(
                    method="GET", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances/'+id, headers=headers, verify=False)
                status = response.json()
                # print("------------->", status['nsState'])
                if status['nsState'] == 'READY':
                    finished = True

            end = time.time()
            elapsed = end - start
            print("tempo da requisição: ", elapsed)

            return "ok"

    # if __name__ == '__main__':
    #     app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.debug = True
    # app.config["DEBUG"] = True

if __name__ == "__main__":
    main()
