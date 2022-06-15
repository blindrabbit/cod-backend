from urls import *
from database.models import User
from database.models import Project

def delete_project(project_id, conn):

    # DELETANDO O PROJETO
    project_openstack = conn.get_project(project_id)
    if project_openstack != None:
        if project_openstack['name'].startswith(LABVER_PREFIX):
            project_openstack = conn.delete_project(project_id)
        return True
    return False    

def create_project(username, project_name, description, conn):

    # CRIANDO O PROJETO

    project_openstack = conn.create_project(name=project_name, description=description,
                                            domain_id='default')

    # print("MEU PROJETO", project_openstack)

    role = 'member'
    role = conn.identity.find_role(role)
    user = conn.identity.find_user(username)
    project = conn.identity.find_project(project_name)

    # ASSOCIANDO UM PROJETO A UM USUÁRIO E SUA DETERMINADA FUNÇÃO
    conn.identity.assign_project_role_to_user(project, user, role)

    role = 'admin'
    role = conn.identity.find_role(role)
    user = conn.identity.find_user('labver')
    project = conn.identity.find_project(project_name)

    # ASSOCIANDO O USUÁRIO LABVER COMO ADM AO PROJETO
    conn.identity.assign_project_role_to_user(project, user, role)

    return project_openstack


def save_project_db(id_project, name, username, id_openstack, id_OSM):

    # fazer teste com esse get depois
    id_user = User.get(User.username == username)
    # print("ID DO MEU USUARIO: ", id_user)

    Project.insert(id_project=id_project, name=name,
                   creation_date='2021-04-03',
                   id_user=id_user,
                   id_openstack=id_openstack,
                   id_OSM=id_OSM
                   ).execute()


def delete_project_db(name_project):

    id_project_selected = Project.get(Project.name == name_project)
    # id_OSM_project = Project.select(Project.id_OSM).where(
    #     Project.name == name_project).execute()

    teste = Project.get(Project.id_project == id_project_selected).id_OSM
    Project.delete_instance(id_project_selected)

    return teste


def list_projects_per_user(username):

    id_user = User.get(User.username == username)
    teste = Project.select(Project.name).join(User).where(
        Project.fk_user == id_user)

    lista = []
    for item in teste:
        print("NOME DO PROJETO ", item.name)
        lista.append(item.name)
    return lista
