import requests
from urls import *
from benedict import benedict
from env import *

def get_vim_accounts(token):
    # GET /admin/v1/vims Query information about multiple VIMs
    method_osm = "/admin/v1/vims/"
    url = url_osm+method_osm
    payload = {}
    token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }

    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return benedict.from_yaml(response.text)

def get_vim_account_by_id(token, id):
    # GET /admin/v1/vims/{vimId} Query information about an individual VIM
    method_osm = "/admin/v1/vims/"+id
    url = url_osm+method_osm
    payload = {}
    token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }

    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return benedict.from_yaml(response.text)

def create_vim(obj):
    # https://172.16.112.56:9999/osm/admin/v1/vim_accounts
    # url = "https://fgcn-backflip3.cs.upb.de:9999/osm/admin/v1/wim_accounts"
    # executa("osm ns-create --ns_name "+ IDENTIFICADOR +" --nsd_name lab_nsd --vim_account VIM-"
    #  + IDENTIFICADOR + " --ssh_keys ~/.ssh/id_rsa.pub
    #  --config '{ vld: [ {name: dataNet, vim-network-name: rede-data} ] }'")
    # url = "https://172.16.112.56:9999/osm/admin/v1/vim_accounts"
    method_osm = "/admin/v1/vim_accounts/"
    url = url_osm+method_osm
    # url = url_vim_accounts
    # https://200.137.75.159:5000
# http://<openstack machine IP>/identity/v2.0

    payload = {
        # "schema_version": "1.11",
        "name": "Openstack Serra 3",
        "description": "nuvem openstack",
        "vim_type": "openstack",
        "vim_url": AUTH_URL,
        "vim_tenant_name": VIM_PROJETO,
        "vim_user": VIM_USER,
        "vim_password": VIM_PASS,
        "config": { 
            "insecure": True,
            "use_existing_flavors": True,
            "additionalProp1": {}
        }
    }
    print (payload)
    headers = {
        'Content-Type': 'application/json',
        "Accept":"application/json",
        "Authorization": "Bearer "+obj
    }

    response = requests.request("POST", url, headers=headers, json = payload, verify=False)
    response.json()
    # return benedict.from_yaml(response.text)
    return (response.json())
