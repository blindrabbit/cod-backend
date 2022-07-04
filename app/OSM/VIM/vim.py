import requests
from vars import *
from urls import *
# from benedict import benedict
# from env import *

def delete_vim(token, vimId):
# /admin/v1/vims/{vimId} Delete a VIM

    if type(token) is dict:
        tokenId=token['id']
    else:
        tokenId = token.replace('\r','')

    method_osm = "/admin/v1/vims/"+vimId
    url = url_osm+method_osm
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+tokenId
    }

    response = requests.request("DELETE", url, headers=headers, data=payload,verify=False)

    return response.text


def get_vim_accounts(token):
    # GET /admin/v1/vims Query information about multiple VIMs
    method_osm = "/admin/v1/vims/"
    url = url_osm+method_osm
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }

    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return response.json()


def get_vim_account_by_id(token, id):
    # GET /admin/v1/vims/{vimId} Query information about an individual VIM
    method_osm = "/admin/v1/vims/"+id
    url = url_osm+method_osm
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }

    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return response.json()


def get_vim_account_by_name(token, vimName):
    # GET /admin/v1/vims Query information about multiple VIMs
    method_osm = "/admin/v1/vims/"
    url = url_osm+method_osm
    payload = {}
    # token = token.replace('\r','')

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }

    vims = requests.request("GET", url, headers=headers, data=payload,verify=False)
    for vim in vims.json():
        if vim['name']=="VIM_"+vimName:
            return vim

    return False


def create_vim(token, projname):
    # token = token.replace('\r','')

    method_osm = "/admin/v1/vim_accounts/"
    url = url_osm+method_osm

    payload = {
        # "schema_version": "1.11",
        "name": "VIM_"+projname,
        "description": "nuvem openstack",
        "vim_type": "openstack",
        "vim_url": AUTH_URL,
        "vim_tenant_name": projname,
        "vim_user": VIM_USER,
        "vim_password": VIM_PASS,
        "config": { 
            "insecure": True,
            # "use_existing_flavors": True,
            "use_existing_flavors": False,
            "additionalProp1": {}
        } #'{ vld: [ {name: dataNet, vim-network-name: rede-data} ] }'")
    }

    headers = {
        'Content-Type': 'application/json',
        "Accept":"application/json",
        "Authorization": "Bearer "+token
    }
    # print (headers)

    response = requests.request("POST", url, headers=headers, json = payload, verify=False)
    # return benedict.from_yaml(response.text)
    return response.json()
