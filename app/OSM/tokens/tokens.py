import requests
from urls import *

def create_token(project_id='admin'):

    headers = {
        'Content-Type': 'application/json'
    }

    payload = {
        "username": 'admin',
        "password": 'admin',
        "project_id": project_id
    }

    response = requests.request(method="POST", url=url_token_osm, headers=headers,
                                json=payload, verify=False)

    return response.text


def get_token_info(token):
    # /admin/v1/tokens/{tokenId} Query information about an individual Token
    token = token.replace('\r','')
    method_osm = "/admin/v1/tokens/"+token
    url = url_osm+method_osm
    payload = {}

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": 'Bearer '+token
    }
    print(token)
    response = requests.request("GET", url, headers=headers, data=payload,verify=False)
    return response.text