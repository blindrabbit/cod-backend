import requests
from OSM.tokens import tokens
from urls import *

def list_projects(project_id, token):
        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + token
        }

        response = requests.request("GET", url_projects, headers=headers, data=payload, verify=False)

        if response.status_code == 401:
            data = tokens.create_token(project_id)
            token = data.split()[2].strip()

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            response = requests.request("GET", url_projects, headers=headers, data = payload, verify=False)

            return '{}\n {}'.format(response.text, token)

        return response

def create_project_OSM(project_name, token_osm,admin):
        payload = {
            'name': project_name,
            # valor de admin é true or false
            'admin': admin,
            "quotas": {
                "vnfds": 10,
                "nsds": 10,
                "slice_templates": 10,
                "pduds": 10,
                "ns_instances":10,
                "slice_instances": 10,
                "vim_accounts": 10,
                "wim_accounts": 10,
                "sdn_controllers": 10,
                "k8sclusters": 10,
                "k8srepos": 10,
                "osmrepos": 10
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": 'Bearer ' + token_osm
        }
 
        response = requests.request("POST", url_projects, headers=headers,
                                    json=payload, verify=False)

        if response.status_code == 401:            
            data = tokens.create_token()
            token = data.split()[2].strip()
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                "Authorization": 'Bearer ' + token
            }

            response = requests.request(method="POST",url= url_projects, 
                                        headers=headers, json = payload, verify=False)

            return response.text

        return response.text

def list_projects_id():
    pass

def del_project():

    url = "http://fgcn-backflip3.cs.upb.de:9999/osm/admin/v1/projects/" + obj.id

    payload = {}
    headers = {
        'Content-Type': ' application/json',
        'Accept': ' application/json',
        "Authorization": 'Bearer AkfZELr3KSRqBotP08arfWlfe4pACV7a'

    }

    response = requests.request("DELETE", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))
