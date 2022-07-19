OSM_IP = "10.50.1.126"
OPENSTACK_IP = "10.50.0.159"
IP = "172.16.112.56"
PORT = "9999"
LABVER_PREFIX = '_LABVER_'
DEFAULT_USER = 1 # ajustar de acordo com cadastro no banco

url_projects = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/projects"
url_users = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/users"
url_vim = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/vims"
url_vnf = "https://"+OSM_IP+":"+PORT+"/osm/vnfpkgm/v1/vnf_packages"
url_associate = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/users/admin"
url_token_osm = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/tokens"
# url_ns_descriptor = "https://"+IP+":"+PORT+"/osm/nsd/v1/ns_descriptors"
url_ns_descriptor = "https://"+OSM_IP+":"+PORT+"/osm/nsd/v1/ns_descriptors_content"
url_vim_accounts = "https://"+OSM_IP+":"+PORT+"/osm/admin/v1/vim_accounts"
url_ns_instance = "https://"+OSM_IP+":"+PORT+"/osm/nslcm/v1/ns_instances"
url_osm = "https://"+OSM_IP+":"+PORT+"/osm"



# REQUEST_POST = {
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

DESCRIPTION_TEST = '5VM/2VNF'

REQUEST_POST1 = {
    "name": "Teste9",
    "user_owner": "Teste9",
    "image": "desktop_padrao_vnfd",
    "classroom": "codigodauturma",
    "instances": 5,
    "description": "descricao informativa do laboratorio",
    "internetaccess": True,
    "creation_date": '1655773901',
    "removal_date": '1656034212',
    "networkfunctions": {
        "vnf1": {
            "image": "openwrt_vnfd",
            "order": 1,
            "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
        },
        "vnf2": {
            "image": "openwrt_vnfd",
            "order": 2,
            "configs": "TEXTO EM FORMATO JSON QUE SERÁ TRATADO PELO GERENCIADOR DA VNF",
        },
    },
}


# AUTH_URL='https://200.137.75.159:5000/v3'
# VIM_USER='labver'
# VIM_PASS='BZMM!@7fCmkVktpmG0'
# VIM_PROJETO='PRJ_LABVER'
# OS_CLIENT_CONFIG_FILE="./app/clouds.yaml"