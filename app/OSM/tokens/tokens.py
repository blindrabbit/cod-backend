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
