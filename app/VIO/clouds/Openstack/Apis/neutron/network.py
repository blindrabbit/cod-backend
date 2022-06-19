import openstack
from openstack .config import loader
import sys

from sqlalchemy import true

# openstack.enable_logging(True, stream=sys.stdout)
# config = loader.OpenStackConfig()
# conn = openstack.connect(cloud="devstack-admin")


def add_port_to_router(router, subnet_id, port_id, conn):

    conn.add_router_interface(router=router,
                              subnet_id=subnet_id,
                              port_id=port_id)    
    return True

def get_network_by_name(network_name, conn):
    network = conn.get_network(network_name)

    return network

def create_network(name_network, project_id, conn):
    network = conn.create_network(name = name_network, project_id = project_id)
    
    return network


def create_subnet(network_id, subnet_name, ip_version, cidr, 
                  gateway_ip, conn):

    subnet = conn.create_subnet(
    network_id,
    subnet_name = subnet_name,
    ip_version = ip_version,
    cidr = cidr,
    gateway_ip = gateway_ip,
    enable_dhcp=True)
    
    return subnet


def create_router(name, ext_gateway_net_id, project_id, conn):

    router = conn.create_router(
    name = name,    
    ext_gateway_net_id = ext_gateway_net_id,
    project_id = project_id)
    
    return router

def delete_port(port_id, conn):

    port_openstack = conn.get_port(port_id)
    if port_openstack != None:
        if port_openstack['name'].startswith('_LABVER_'):
            conn.delete_port(port_id)
            return True

    return False

def delete_router(router_id, port_id, conn):

    router_openstack = conn.get_router(router_id)
    if router_openstack != None:
        if router_openstack['name'].startswith('_LABVER_'):
            conn.remove_router_interface(router = router_openstack, port_id = port_id)
            conn.delete_router(router_id)
            return True

    return False


def delete_network(network_id, conn):

    network_openstack = conn.get_network(network_id)
    # print(network_openstack)
    if network_openstack != None:
        if network_openstack['name'].startswith('_LABVER_'):
            conn.delete_network(network_id)
            return True

    return False


def create_port(network_id, port_name, port_ip, subnetwork_id, conn):

    port = conn.create_port(
        network_id = network_id,
        name = port_name,
        admin_state_up = True,
        fixed_ips = [
                    {"ip_address": port_ip, "subnet_id": subnetwork_id},
                    ])
    return port


# print(example_network)
# example_subnet = conn.network.create_subnet(
#     name='openstacksdk-example-project-subnet',
#     network_id=example_network.id,
#     ip_version='4',
#     cidr='10.0.2.0/24',
#     gateway_ip='10.0.2.1')
# print(example_subnet)



# print("Delete Network:")
# example_network = conn.network.find_network(
#     'openstacksdk-example-project-network')

# for example_subnet in example_network.subnet_ids:
#     conn.network.delete_subnet(example_subnet, ignore_missing=False)

# conn.network.delete_network(example_network, ignore_missing=False)