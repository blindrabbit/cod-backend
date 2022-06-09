# import openstack
# from openstack .config import loader
# import sys

def create_flavor(name,ram,vcpus,disk,ephemeral,is_public, project_id, connection_openstack):

    flavor = connection_openstack.create_flavor(name=name,ram=ram,vcpus=vcpus,
                                   disk=disk,ephemeral=ephemeral,is_public=is_public)
    
    connection_openstack.add_flavor_access(flavor_id=flavor.id,
                                       project_id=project_id)

    return flavor
    
    
    flavor_teste = conn.compute.create_flavor(
        name = name,
        vcpus = vcpus,
        disk = disk,
        ram = ram,
        ephemeral = ephemeral,
        is_public = is_public)
    
    return flavor_teste