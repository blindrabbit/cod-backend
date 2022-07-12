# Rodar em modo de debug - autoreload
# PS C:\Users\1918648\Documents\GitHub\Campus-ON-Demand\app> $env:FLASK_ENV="development"
# PS C:\Users\1918648\Documents\GitHub\Campus-ON-Demand\app> python -m flask run
# $env:OS_CLIENT_CONFIG_FILE="clouds.yaml"
# PS C:\Users\1918648\Documents\GitHub\cod-backend> .\env\Scripts\Activate
# (env) PS C:\Users\1918648\Documents\GitHub\cod-backend> $env:OS_CLIENT_CONFIG_FILE="./app/clouds.yaml"
from ipaddress import ip_address
import json
import threading
from xmlrpc.client import boolean
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
from VIO.clouds.Gnocchi import *
from urls import *
from vars import *
from authentication.authentication import *
from openstack.exceptions import *
from flask_cors import CORS
from flask import Response
import time
import datetime

# from keystoneclient.v3 import client
# from playhouse.shortcuts import model_to_dict
# from benedict import benedict
from operator import itemgetter
from os import getenv
from random import randint

# import logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

requests.packages.urllib3.disable_warnings()


def main():
    print("Iniciando Serviço")

    app = Flask(__name__)
    CORS(app)

    # @cross_origin()

    # @app.errorhandler(404)
    # def page_not_found(e):
    #     # note that we set the 404 status explicitly
    #     return "", 404

    def date_time_now():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @app.before_first_request
    def activate_schedule():
        def run_scheduler():
            print("Starting Thread to monitor laboratory schedules.")
            while True:
                time.sleep(10)
                query = (Laboratory
                         .select()
                         .where((Laboratory.status == 'scheduled') |
                                (Laboratory.status == 'instantiated'))
                         )
                laboratories = {'removal': [], 'create': []}

                # print(query.get_or_none())
                if query.get_or_none() != None:
                    for lab in query:
                        laboratory_id = lab.id_laboratory
                        # print('ID LAB', laboratory_id)

                        laboratory_from_bd = (Laboratory
                                              .select(Laboratory, User, Project, Networkservice,
                                                      Networkservice.id_osm_vim.alias('id_vim'),
                                                      Project.name.alias('proj_name'))
                                              .join(User)
                                              .join(Project)
                                              .join(Networkservice)
                                              .where((Laboratory.id_laboratory == laboratory_id) &
                                                     (Project.id_laboratory == laboratory_id)))

                        laboratory = laboratory_from_bd.dicts().get()
                        token = laboratory['token_OSM']
                        nsName = laboratory['proj_name']
                        nsdId = laboratory['id_osm_ns_instance']
                        vimAccountId = laboratory['id_vim']

                        tokenInfo = tokens.get_token_info(token)
                        if 'code' in tokenInfo:
                            if tokenInfo['code'] == 'UNAUTHORIZED':  # token gravado não existe mais, renovar
                                token = tokens.create_token()

                        retorno = OSMNS.get_ns_resource(token, nsdId)
                        # print('>>>>>>>>>>>>>>>>>>>>', retorno)

                        if 'nsState' not in retorno:
                            if laboratory['creation_date'] <= datetime.datetime.now():
                                print(laboratory['creation_date'], 'está tentando criar um novo lab!')
                                # ns_instantiated = OSMNS.instantiate_ns(token, nsName, nsdId, vimAccountId)
                                dic = {nsdId: nsName}
                                laboratories['create'].append(dic)
                        if 'nsState' in retorno:
                            if retorno['nsState'] == 'READY':
                                if laboratory['removal_date'] < datetime.datetime.now():
                                    print(laboratory['creation_date'], 'está tentando remover um lab!')
                                    # ns_terminaded = OSMNS.delete_ns_instantiate(token, nsdId)
                                    ns_terminaded = delete_laboratory(laboratory['id_laboratory'])
                                    dic = {nsdId: nsName}
                                    laboratories['removal'].append(dic)

                print(laboratories)
                time.sleep(20)

        thread = threading.Thread(target=run_scheduler)
        thread.start()

    def create_laboratory_validade_json(json):
        if 'name' not in json:
            return 'name not defined'
        if 'user_owner' not in json:
            return 'user_owner not defined'
        if 'image' not in json:
            return 'image not defined'
        if 'classroom' not in json:
            return 'classroom not defined'
        if 'instances' not in json:
            return 'instances not defined'
        else:
            if not isinstance(json['instances'], int):
                return 'instances must be integer'
        if 'description' not in json:
            return 'description not defined'
        if 'internetaccess' not in json:
            return 'internetaccess not defined'
        else:
            if not isinstance(json['internetaccess'], bool):
                return 'internetaccess must be bool [true/false]'
        if 'creation_date' not in json:
            return 'creation_date not defined'
        else:
            if not isinstance(datetime.datetime.fromtimestamp(int(json['creation_date'])),
                              datetime.datetime):
                return 'creation_date must be datetime [timestamp]'
        if 'removal_date' not in json:
            return 'removal_date not defined'
        else:
            if not isinstance(datetime.datetime.fromtimestamp(int(json['removal_date'])),
                              datetime.datetime):
                return 'removal_date must be datetime [timestamp]'
        if 'networkfunctions' not in json:
            return 'networkfunctions not defined'
        else:
            for vnf in json['networkfunctions']:
                # print(json['networkfunctions'][vnf])
                if 'image' not in json['networkfunctions'][vnf]:
                    return 'image not defined at ' + vnf
                if 'order' not in json['networkfunctions'][vnf]:
                    return 'order not defined at ' + vnf
                else:
                    if not isinstance(json['networkfunctions'][vnf]['order'], int):
                        return 'order defined at ' + vnf + ' must be integer'
                if 'configs' not in json['networkfunctions'][vnf]:
                    return 'configs not defined at ' + vnf
        return False

    @app.route('/beta/listImages/', methods=['POST', 'GET', 'DELETE'])
    def beta_listImages():
        if request.method == 'POST':
            return 'Post Method not allowed', 400

        if request.method == 'GET':
            try:
                cloud = 'openstack-serra'
                connection_openstack = create_connection_openstack_clouds_file(cloud)
                images = []
                for image in connection_openstack.list_images(show_all=True):
                    if 'properties' in image:
                        if 'is_lab_allowed' in image['properties']:
                            dic = {'id': image['id'], 'name': image['name']}
                            print(dic)
                            images.append(dic)
                return jsonify(images)

            except Exception as error:
                print("error", error)
                return 'erro não tratado.', 400

    @app.route('/beta/create_laboratory', methods=['POST', 'GET'])
    def beta_create_laboratory():
        # print(request)
        if request.method == 'GET':
            return 'Get Method not allowed', 400

        if request.method == 'POST':
            data = request.get_json()
            lab_check_up = create_laboratory_validade_json(data)

            if lab_check_up:
                return lab_check_up, 400

            try:
                user_name = 'renancs'  # recuperar o nome do FRONTEND
                user_id = data['user_owner']  # recuperar o ID do FRONTEND

                laboratory_name = LABVER_PREFIX + data['name']
                laboratory_classroom = data['classroom']
                laboratory_description = data['description']
                laboratory_instances = data['instances']

                if Laboratory.get_or_none(Laboratory.name == laboratory_name):
                    return "ja tem com esse nome"

                laboratory_to_bd = Laboratory.create(
                    name=laboratory_name,
                    classroom=laboratory_classroom,
                    description=laboratory_description,
                    instances=laboratory_instances,
                    fk_user=User.select().where(User.id_user == user_id)
                )

                var = laboratory_to_bd.id_laboratory
                retorno = {'id': var}
                return retorno, 200

            except Exception as error:
                print("error", error)
                return 'erro não tratado.', 400

    @app.route("/beta/delete_laboratory/<laboratory_id>/", methods=['POST', 'GET', 'DELETE'])
    def beta_delete_laboratory(laboratory_id):
        if request.method == 'POST':
            return 'Post Method not allowed', 400

        if request.method == 'GET':
            try:
                laboratory_from_bd = (Laboratory
                                      .select(Laboratory)
                                      .where(Laboratory.id_laboratory == laboratory_id))
                laboratory = laboratory_from_bd.dicts().get()
                if laboratory:
                    laboratory_from_bd.get().delete_instance(recursive=True)

                return '', 200

            except Exception as error:
                print("error", error)
                return 'erro não tratado.', 400

    @app.route("/delete_laboratory/<laboratory_id>/", methods=['POST', 'GET', 'DELETE'])
    def delete_laboratory(laboratory_id):
        cloud = 'openstack-serra'

        connection_openstack = create_connection_openstack_clouds_file(cloud)

        laboratory_from_bd = (Laboratory
                              .select(Laboratory, User, Project, Networkservice,
                                      Networkservice.id_osm_vim.alias('id_vim'), Project.name.alias('proj_name'))
                              .join(User)
                              .join(Project)
                              .join(Networkservice)
                              .where((Laboratory.id_laboratory == laboratory_id) &
                                     (Project.id_laboratory == laboratory_id)))

        laboratory = laboratory_from_bd.dicts().get()
        print(laboratory)
        tests_select = (Tests
                        .select()
                        .where(Tests.fk_laboratory == laboratory_id))

        teste_liberar_recursos = Tests_Methods.create(
            id_tests=tests_select.get(),
            id_methods=5
        )

        # ---------- TESTE tempo para liberação dos recursos - tempo inicial
        teste_liberar_recursos.start_date_test_methods = date_time_now()

        token = laboratory['token_OSM']
        tokenInfo = tokens.get_token_info(token)
        if 'code' in tokenInfo:
            if tokenInfo['code'] == 'UNAUTHORIZED':  # token gravado não existe mais, renovar
                token = tokens.create_token()

        if laboratory:
            return_del_ns_instance = OSMNS.delete_ns_instantiate(token, laboratory['id_osm_ns_instance'])
            # print(return_del_ns_instance)

            return_del_nsd = OSMNS.delete_nsd(token, laboratory['id_osm_nsd'])
            # print(return_del_nsd)

            return_del_vim = OSMvim.delete_vim(token, laboratory['id_osm_vim'])
            # print(return_del_vim)

            delete_router(laboratory['openstack_id_router'],
                          laboratory['openstack_id_router_gateway_port'],
                          connection_openstack)
            delete_network(laboratory['openstack_id_network'], connection_openstack)
            return_del_project = delete_project(laboratory['id_project'], connection_openstack)

            laboratory_from_bd.get().delete_instance(recursive=True)

        # ---------- TESTE tempo para liberação dos recursos - tempo inicial
        teste_liberar_recursos.finish_date_test_methods = date_time_now()
        teste_liberar_recursos.save()

        return '', 204
        # return "<a href='/create_laboratory'>Criar novo laboratorio</a>"

    @app.route('/create_laboratory')
    def create_laboratory():
        cloud = 'openstack-serra'
        payload = REQUEST_POST1
        undo = {}
        ok = create_laboratory_validade_json(payload)
        if ok:
            True
        else:
            False
        try:

            # inicialização da coleta dos testes de tempo de criação
            timing_tests = Tests.create(  # datetime.nowdate_time_now()
                start_date_test=date_time_now(),
                # start_date_test = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                description=DESCRIPTION_TEST
            )

            teste_criar_usuario = Tests_Methods.create(
                fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
                fk_methods=1
            )
            teste_criar_projeto = Tests_Methods.create(
                fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
                fk_methods=2
            )
            teste_configurar_rede = Tests_Methods.create(
                fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
                fk_methods=3
            )
            teste_alocar_recursos = Tests_Methods.create(
                fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
                fk_methods=4
            )
            # teste_consumo_cpu = Tests_Methods.create(
            #     fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
            #     fk_methods=6
            # )
            # teste_consumo_memoria = Tests_Methods.create(
            #     fk_tests=Tests.select().where(Tests.id_tests == timing_tests.id_tests),
            #     fk_methods=7
            # )

            user_name = 'renancs'  # recuperar o nome do FRONTEND
            user_id = '2'  # recuperar o ID do FRONTEND

            user_from_bd = User.get_or_none(id_user=user_id)
            if user_from_bd is None:
                user_from_bd = User.get_by_id(DEFAULT_USER)

            user_id = user_from_bd.id_user

            laboratory_name = LABVER_PREFIX + payload['name']
            laboratory_classroom = payload['classroom']
            laboratory_description = payload['description']
            laboratory_instances = payload['instances']

            project_name = laboratory_name
            project_description = laboratory_description

            network_name = laboratory_name + 'rede-data'
            subnet_name = laboratory_name + 'subrede-data'
            router_gateway_port_name = laboratory_name + 'porta_roteador'
            router_name = laboratory_name + 'roteador'

            creation_date = datetime.datetime.fromtimestamp(int(payload['creation_date']))
            removal_date = datetime.datetime.fromtimestamp(int(payload['removal_date']))

            if Laboratory.get_or_none(Laboratory.name == laboratory_name):
                return "ja tem com esse nome"

            laboratory_to_bd = Laboratory.create(
                name=laboratory_name,
                classroom=laboratory_classroom,
                description=laboratory_description,
                instances=laboratory_instances,
                creation_date=creation_date,
                removal_date=removal_date,
                fk_user=User.select().where(User.id_user == user_id)
            )

            timing_tests.fk_laboratory = laboratory_to_bd.id_laboratory

            # print(laboratory_to_bd['id_laboratory'])
            undo['laboratory_to_bd'] = True  # laboratory_to_bd['id_laboratory']
            print('laboratory_to_bd')

            connection_openstack = create_connection_openstack_clouds_file(cloud)

            # ---------- TESTE tempo de criação de um projeto - tempo inicial
            teste_criar_projeto.start_date_test_methods = date_time_now()

            project = create_project(user_name, project_name, project_description, connection_openstack)

            undo['create_project_openstack'] = project['id']
            print('create_project_openstack')

            project_to_bd = Project.create(
                id_project=project['id'],
                name=project_name,
                fk_user=User.select().where(User.id_user == user_id),
                fk_laboratory=laboratory_to_bd.id_laboratory,
                description=project_description
            )

            undo['project_to_bd'] = project['id']
            print('project_to_bd')

            # ---------- TESTE tempo de criação de um projeto - tempo final
            teste_criar_projeto.finish_date_test_methods = date_time_now()

            # ---------- TESTE tempo de configuração de rede - tempo inicial
            teste_configurar_rede.start_date_test_methods = date_time_now()

            network = create_network(network_name, project['id'], connection_openstack)

            undo['create_network_openstack'] = network['id']
            print('create_network_openstack')

            cidr = '10.' + str(randint(0, 254)) + '.' + str(randint(0, 254)) + '.0/24'
            gateway = cidr.replace('.0/24', '.1')

            subnetwork = create_subnet(network['id'], subnet_name, 4, cidr,
                                       gateway, connection_openstack)

            router_gateway_port = create_port(network['id'], router_gateway_port_name,
                                              gateway, subnetwork['id'], connection_openstack)

            undo['create_port_openstack'] = router_gateway_port['id']
            print('create_port_openstack')

            provider_network = get_network_by_name('provider', connection_openstack)

            router = create_router(router_name, provider_network['id'], project['id'],
                                   connection_openstack)

            undo['create_router_openstack'] = router['id']
            print('create_router_openstack')

            add_port_to_router(router, subnetwork['id'], router_gateway_port['id'], connection_openstack)

            project_to_bd.cidr = cidr
            project_to_bd.gateway = gateway
            project_to_bd.openstack_id_router = router['id']
            project_to_bd.openstack_id_router_gateway_port = router_gateway_port['id']
            project_to_bd.openstack_id_subnet = subnetwork['id']
            project_to_bd.openstack_id_network = network['id']

            project_to_bd.save()

            # ---------- TESTE tempo de configuração de rede - tempo final
            teste_configurar_rede.finish_date_test_methods = date_time_now()

            # ---------- TESTE tempo para Alocar recursos - tempo inicial
            teste_alocar_recursos.start_date_test_methods = date_time_now()

            id_do_lab = laboratory_to_bd.id_laboratory

            if user_from_bd.token_OSM == '':
                token = tokens.create_token()
                user_from_bd.token_OSM = str(token['id'])
                user_from_bd.save()
                token = str(token['id'])
            else:
                tokenInfo = tokens.get_token_info(user_from_bd.token_OSM)
                if "_id" in tokenInfo:
                    token = tokenInfo['_id']
                if "code" in tokenInfo:
                    if tokenInfo['code'] == 'UNAUTHORIZED':
                        token = tokens.create_token()
                        user_from_bd.token_OSM = str(token['id'])
                        user_from_bd.save()
                        token = str(token['id'])

            vimAccount = OSMvim.get_vim_account_by_name(token, project_name)

            vimAccountId = {}

            if not vimAccount:
                vimAccountId = OSMvim.create_vim(token, project_name)
            else:
                vimAccountId['id'] = vimAccount['_id']

            undo['OSMvim_create_vim'] = vimAccountId['id']
            print('OSMvim_create_vim')

            nsd = OSMNS.create_nsd(laboratory_name, cidr, REQUEST_POST1)

            nsdId = OSMNS.compose_ns(token, nsd)
            nsName = project_name

            undo['OSMNS_compose_ns'] = nsdId
            print('OSMNS_compose_ns')

            # Recurso do agendamento, se a data de criação for menor que a data atual,
            # ele instancia no momento da criação. Se não, será inicializado por outro metodo de inicialização.
            if creation_date <= datetime.datetime.now():
                # print(token, nsName, nsdId, vimAccountId['id'])
                nsdId_instance = OSMNS.instantiate_ns(token, nsName, nsdId, vimAccountId['id'])
                laboratory_to_bd.status = 'instantiated'

                undo['OSMNS_instantiate_ns'] = nsdId_instance
                print('OSMNS_instantiate_ns')
            else:
                laboratory_to_bd.status = 'scheduled'

            networkservice_to_bd = Networkservice.create(
                id_networkservice=nsdId,
                id_osm_nsd=nsdId,
                id_osm_ns_instance=nsdId_instance['id'],
                id_osm_vim=vimAccountId['id'],
                fk_project=project['id']
            )
            networkservice_to_bd.save()

            retorno = {'id': id_do_lab}

            laboratory_to_bd.save()

            # ---------- TESTE tempo para Alocar recursos - tempo final
            teste_alocar_recursos.finish_date_test_methods = date_time_now()

            timing_tests.finish_date_test = date_time_now()

            timing_tests.save()

            teste_criar_usuario.save()
            teste_criar_projeto.save()
            teste_configurar_rede.save()
            teste_alocar_recursos.save()

            return retorno, 201

        except Exception as error:

            if 'OSMNS_instantiate_ns' in undo:

                print('apagar no OSM network service Instance')
                OSMNS.delete_ns_instantiate(token, undo['OSMNS_instantiate_ns'])

            # undo['create_vim']=vimAccountId['id']

            else:

                # undo['create_vim']=vimAccountId['id']
                # undo['OSMNS.instantiate_ns']=nsdId_instance

                if 'create_router_openstack' in undo:
                    print('apagar roteador')
                    delete_router(undo['create_router_openstack'], undo['create_port_openstack'], connection_openstack)

                if 'create_network_openstack' in undo:
                    print('apagar network')
                    delete_network(undo['create_network_openstack'], connection_openstack)

                if 'OSMNS_compose_ns' in undo:
                    print('apagar no OSM network service Descriptor')
                    OSMNS.delete_nsd(token, undo['OSMNS_compose_ns'])

                if 'OSMvim_create_vim' in undo:
                    print('apagar no OSM VIM')
                    OSMvim.delete_vim(token, undo['OSMvim_create_vim'])

            if 'create_project_openstack' in undo:
                print('apagar projeto')
                delete_project(undo['create_project_openstack'], connection_openstack)

            if 'laboratory_to_bd' in undo:
                print('apagar laboratorio no banco de dados')
                laboratory_to_bd.delete_instance(recursive=True)

            return jsonify(error)

    @app.route('/testemodel')
    def testemodel():
        return 'Vamos testar o modelo! -->'  # +str(vimAccountId)

    @app.route('/teste/', methods=['POST', 'GET', 'DELETE'])
    def teste():
        laboratory_id = 48
        cloud = 'openstack-serra'
        connection_openstack = create_connection_openstack_clouds_file(cloud)

        # Insert Session in Gnocchi object
        gnocchi = Gnocchi(session=connection_openstack.session)

        resource_ids_nova = gnocchi.get_resource_id('nova_compute')
        # return 'rota de teste'  # +str(vimAccountId)
        # print("RESOURCE ID--> ", resource_ids_nova)

        queryTests = (Tests_Methods
                      .select(Tests, Tests_Methods)
                      .join(Tests)
                      .where(Tests.fk_laboratory == laboratory_id)
                      )

        print('queryTests', queryTests)

        for test in queryTests:
            # print('id test', test.id_tests_methods)
            # print('start test', test.start_date_test_methods)
            # print('end test', test.finish_date_test_methods)
            if test.start_date_test_methods == 0:
                print('vazio')

            metrics_cpu = json.loads(gnocchi.get_measure_in_interval("compute.node.cpu.percent",
                                                                   resource_ids_nova,
                                                                   None,
                                                                   60,
                                                                   test.start_date_test_methods,
                                                                   test.finish_date_test_methods))

            # metrics_memory = json.loads(gnocchi.get_measure_in_interval("hardware.memory.used",
            #                                                        resource_ids_nova,
            #                                                        None,
            #                                                        60,
            #                                                        test.start_date_test_methods,
            #                                                        test.finish_date_test_methods))

            print(metrics_cpu)
            for metric_cpu in metrics_cpu:
                print('--->', test.id_tests_methods, metric_cpu[0], metric_cpu[1], metric_cpu[2])
                query = TestsMethodsData.create(id_tests_methods=test.id_tests_methods,
                                                timestamp=metric_cpu[0],
                                                granularity=metric_cpu[1],
                                                metric_utilization=metric_cpu[2],
                                                metric_type='cpu')
            # print(metrics_memory)
            # for metric_memory in metrics_memory:
            #     print('--->', test.id_tests_methods, metric_memory[0], metric_memory[1], metric_memory[2])
            #     query = TestsMethodsData.create(id_tests_methods=test.id_tests_methods,
            #                                     timestamp=metric_memory[0],
            #                                     granularity=metric_memory[1],
            #                                     metric_utilization=metric_memory[2],
            #                                     metric_type='memory')

        #     print('TESTESTESTES', resultado)
        #
        # print('queryTests', queryTests.dicts().get())
        #
        # testsResult = queryTests.dicts().get()
        #
        # now = datetime.datetime.now().utcnow()
        # intervalo = 600
        # delta = datetime.timedelta(seconds=intervalo)
        # time_past = now - delta
        # START = time_past
        # STOP = now
        # GRANULARITY = 60
        #
        # # resultado = gnocchi.get_last_measure("compute.node.cpu.idle.percent", resource_ids_nova, None, GRANULARITY,
        # #                                      START, STOP)
        # resultado = gnocchi.get_measure_in_interval("compute.node.cpu.percent", resource_ids_nova, None, GRANULARITY,
        #                                             START, STOP)
        # # resultado = gnocchi.get_metric_cpu_utilization(resource_ids_nova, GRANULARITY, 1, START, STOP)
        # print('TESTESTESTES', resultado)
        # res = json.loads(resultado)
        # print('JSONLOADS', len(res))
        #
        # for registro in res:
        #     query = TestsMethodsData.create(id_tests_methods=testsResult['id_tests_methods'],
        #                                     timestamp=registro[0],
        #                                     granularity=registro[1],
        #                                     metric_utilization=registro[0])

        # laboratory_to_bd = Laboratory.create(
        #     name=laboratory_name,
        #     classroom=laboratory_classroom,
        #     description=laboratory_description,
        #     instances=laboratory_instances,
        #     fk_user=User.select().where(User.id_user == user_id)
        # )

        # querymany = query.insert_many(res, fields=[TestsMethodsData.timestamp,
        #                                            TestsMethodsData.granularity,
        #                                            TestsMethodsData.metric_utilization])

        # print('query insert Many result', querymany)
        # result = querymany.execute()
        # print('insert Many result', result)
        # print(resultado)
        return 'resultado'

    @app.route('/createLaboratory/', methods=['POST', 'GET', 'DELETE'])
    def createLaboratory():

        cloud = 'openstack-serra'
        # payload = REQUEST_POST

        connection_openstack = create_connection_openstack_clouds_file(cloud)
        if request.method == 'GET':
            data = request.get_json()

            # nsd = OSMNS.create_nsd(payload)

            print("GET")
        if request.method == 'POST':
            print("POST")

        print("blabla")
        return False

    @app.route('/createNSD/', methods=['POST', 'GET', 'DELETE'])
    def createNSD():

        return False

    @app.route('/listImages/', methods=['POST', 'GET', 'DELETE'])
    def listImages():
        cloud = 'openstack-serra'
        connection_openstack = create_connection_openstack_clouds_file(cloud)
        images = []
        for image in connection_openstack.list_images(show_all=True):
            if 'properties' in image:
                if 'is_lab_allowed' in image['properties']:
                    dic = {'id': image['id'], 'name': image['name']}
                    print(dic)
                    images.append(dic)
        return jsonify(images)

    @app.route('/osm/criarnetworkservice/', methods=['POST', 'GET', 'DELETE'])
    def osmNS():
        return False

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
                    server_from_bd = Server.get_or_none(Server.id_server_openstack == server['id'], Server.state != "")
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
                method="DELETE", url='https://10.50.1.142:9999/osm/admin/v1/projects/' + str(id_OSM_Delete),
                headers=headers, verify=False)

            return resp.text

    @app.route('/VNF/', methods=['POST', 'GET', 'DELETE'])
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

            return (response.text)

    @app.route('/vim/', methods=['POST', 'GET', 'DELETE'])
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

            return (response.text)

    @app.route("/security_group/", methods=['POST', 'GET', 'DELETE'])
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

    @app.route("/rules/", methods=['POST', 'GET', 'DELETE'])
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

    @app.route("/network/", methods=['POST', 'GET', 'DELETE'])
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

    @app.route("/subnet/", methods=['POST', 'GET', 'DELETE'])
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

    @app.route("/image/", methods=['POST', 'GET', 'DELETE'])
    def image():
        pass

    @app.route("/flavors/", methods=['POST', 'GET', 'DELETE'])
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

    @app.route("/NS/", methods=['POST', 'GET', 'DELETE'])
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
                        "vld": [{'id': 'dataNet', 'ip-profile-ref': 'IP-t1', 'name': 'dataNet', 'short-name': 'dataNet',
                                 'type': 'ELAN', 'vnfd-connection-point-ref': [
                                {'member-vnf-index-ref': 1, 'ip-address': '10.10.10.11',
                                 'vnfd-connection-point-ref': 'vnf-data',
                                 'vnfd-id-ref': 'desktop_padrao_vnfd'},
                                {'member-vnf-index-ref': 101, 'vnfd-connection-point-ref': 'vnf-data',
                                 'vnfd-id-ref': 'openwrt_vnfd'}]}],

                        'ip-profiles': [{'description': 'Rede de acesso dos desktops', 'ip-profile-params': {
                            'dhcp-params': {'count': 100, 'enabled': True, 'start-address': '10.10.10.10'},
                            'dns-server': [{'address': '8.8.8.8'}], 'ip-version': 'ipv4',
                            'gateway-address': '10.10.10.1', 'subnet-address': '10.10.10.0/24'}, 'name': 'IP-t1'}],
                        'vnffgd': [{'id': 'vnffg1', 'name': 'vnffg1-name', 'short-name': 'vnffg1-sname',
                                    'description': 'vnffg1-description', 'vendor': 'vnffg1-vendor', 'version': '1.0',
                                    'classifier': [{'id': 'class1', 'member-vnf-index-ref': 1, 'name': 'class1name',
                                                    'rsp-id-ref': 'rsp101', 'vnfd-connection-point-ref': 'vnf-data',
                                                    'vnfd-id-ref': 'desktop_padrao_vnfd', 'match-attributes': [
                                            {'id': 'match1', 'ip-proto': 17, 'source-ip-address': '10.10.10.11',
                                             'destination-port': '5001:5011'}]}],
                                    'rsp': [{'id': 'rsp101', 'name': 'rsp101name', 'vnfd-connection-point-ref': [
                                        {'member-vnf-index-ref': 101, 'order': 0,
                                         'vnfd-egress-connection-point-ref': 'vnf-data', 'vnfd-id-ref': 'openwrt_vnfd',
                                         'vnfd-ingress-connection-point-ref': 'vnf-data'}]}]}],
                        "constituent-vnfd": [{'member-vnf-index': 1, 'vnfd-id-ref': 'desktop_padrao_vnfd'},
                                             {'member-vnf-index': 101, 'vnfd-id-ref': 'openwrt_vnfd'}],
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
            method="POST", url='https://10.50.1.56:9999/osm/nsd/v1/ns_descriptors_content', headers=headers,
            json=payload, verify=False)

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
            method="POST", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances', headers=headers, json=payload,
            verify=False)

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
            method="POST", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances/' + id + '/instantiate',
            headers=headers, json=payload, verify=False)

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + token
        }

        finished = False
        while finished == False:
            response = requests.request(
                method="GET", url='https://10.50.1.56:9999/osm/nslcm/v1/ns_instances/' + id, headers=headers,
                verify=False)
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
