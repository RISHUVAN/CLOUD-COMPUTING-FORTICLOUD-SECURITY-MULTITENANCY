from google.cloud import iam_v1

def create_role(project_id, role_id, title, description, permissions):
    client = iam_v1.IAMClient()
    role_name = f'projects/{project_id}/roles/{role_id}'
    role = {
        'name': role_name,
        'title': title,
        'description': description,
        'included_permissions': permissions
    }
    response = client.create_role(parent=f'projects/{project_id}', role_id=role_id, role=role)
    print(f'Created role: {response.name}')
    return response

# Example usage
project_id = 'your-project-id'
role_id = 'customRole'
title = 'Custom Role'
description = 'A custom role with specific permissions'
permissions = ['resourcemanager.projects.get', 'resourcemanager.projects.list']
create_role(project_id, role_id, title, description, permissions)

from google.cloud import compute_v1

def create_vpc(project_id, vpc_name):
    client = compute_v1.NetworksClient()
    network = compute_v1.Network(
        name=vpc_name,
        auto_create_subnetworks=False
    )
    operation = client.insert(project=project_id, network_resource=network)
    print(f'Creating VPC: {vpc_name}')
    return operation

def create_subnet(project_id, vpc_name, subnet_name, region, ip_range):
    client = compute_v1.SubnetworksClient()
    subnetwork = compute_v1.Subnetwork(
        name=subnet_name,
        network=f'projects/{project_id}/global/networks/{vpc_name}',
        ip_cidr_range=ip_range
    )
    operation = client.insert(project=project_id, region=region, subnetwork_resource=subnetwork)
    print(f'Creating Subnet: {subnet_name} in {vpc_name}')
    return operation

def create_firewall_rule(project_id, vpc_name, rule_name, allowed_protocol, allowed_ports, direction):
    client = compute_v1.FirewallsClient()
    firewall_rule = compute_v1.Firewall(
        name=rule_name,
        network=f'projects/{project_id}/global/networks/{vpc_name}',
        allowed=[{
            'IPProtocol': allowed_protocol,
            'ports': allowed_ports
        }],
        direction=direction
    )
    operation = client.insert(project=project_id, firewall_resource=firewall_rule)
    print(f'Creating Firewall Rule: {rule_name}')
    return operation

# Example usage
vpc_name = 'forticloud-vpc'
subnet_name = 'forticloud-subnet'
region = 'us-central1'
ip_range = '10.0.0.0/24'
rule_name = 'allow-http'
allowed_protocol = 'tcp'
allowed_ports = ['80']
direction = 'INGRESS'

create_vpc(project_id, vpc_name)
create_subnet(project_id, vpc_name, subnet_name, region, ip_range)
create_firewall_rule(project_id, vpc_name, rule_name, allowed_protocol, allowed_ports, direction)

from google.cloud import logging_v2

def setup_logging(project_id):
    client = logging_v2.LoggingServiceV2Client()
    log_name = f'projects/{project_id}/logs/example-log'
    logger = client.logger(log_name)

    def write_log(entry):
        logger.log_text(entry)

    write_log('This is a test log entry')
    print(f'Log entry created in {log_name}')

# Example usage
setup_logging(project_id)


