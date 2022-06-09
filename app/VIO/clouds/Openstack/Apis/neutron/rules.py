def create_rules_to_secutity_groups(security_group_id, direction, remote_ip_prefix,
                                    protocol,port_range_max,port_range_min,
                                    ethertype, conn):
     
    example_rule = conn.network.create_security_group_rule(
    security_group_id = security_group_id,
    direction = direction,
    remote_ip_prefix = remote_ip_prefix,
    protocol = protocol,
    port_range_max = port_range_max,
    port_range_min = port_range_min,
    ethertype = ethertype)
    
    return example_rule