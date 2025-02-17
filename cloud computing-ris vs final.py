import os
from google.cloud import compute_v1, pubsub_v1
import time

# Set up authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/service-account-key.json'

project_id = 'cloud-rishuvan'
region = 'asia-south1(mumbai)'
zone = 'asia-south1'
network_name = 'fortigate-network'
subnetwork_name = 'fortigate-subnetwork'
firewall_name = 'fortigate-firewall'
instance_name = 'fortigate-vm'
fortigate_image = 'projects/cloud-rishuvan/fortinet-utm/global/images/c0-deeplearning-common-cpu-v20230925-debian-10'
machine_type = 'n1-standard-4'
subnetwork_cidr = '10.0.1.0/24'
pubsub_topic = 'fortigate-deployment'

def publish_message(publisher, topic, message):
    topic_path = publisher.topic_path(project_id, topic)
    future = publisher.publish(topic_path, message.encode('utf-8'))
    future.result()
    print(f"Published message to {topic}: {message}")

def create_vpc_network(compute_client, publisher, project, network_name):
    network = compute_v1.Network(
        name=network_name,
        auto_create_subnetworks=False
    )
    operation = compute_client.insert(project=project, network_resource=network)
    wait_for_operation(compute_client, project, operation)
    message = f"Created VPC network: {network_name}"
    publish_message(publisher, pubsub_topic, message)

def create_subnetwork(compute_client, publisher, project, region, network_name, subnetwork_name, cidr):
    subnetwork = compute_v1.Subnetwork(
        name=subnetwork_name,
        ip_cidr_range=cidr,
        network=f'projects/{project}/global/networks/{network_name}',
        region=region
    )
    operation = compute_client.insert(project=project, region=region, subnetwork_resource=subnetwork)
    wait_for_operation(compute_client, project, operation, region=region)
    message = f"Created subnetwork: {subnetwork_name}"
    publish_message(publisher, pubsub_topic, message)

def create_firewall_rule(compute_client, publisher, project, network_name, firewall_name):
    firewall = compute_v1.Firewall(
        name=firewall_name,
        allowed=[
            compute_v1.Allowed(
                IPProtocol='tcp',
                ports=['22', '443']
            )
        ],
        network=f'projects/{project}/global/networks/{network_name}',
        source_ranges=['0.0.0.0/0']
    )
    operation = compute_client.insert(project=project, firewall_resource=firewall)
    wait_for_operation(compute_client, project, operation)
    message = f"Created firewall rule: {firewall_name}"
    publish_message(publisher, pubsub_topic, message)

def create_instance(compute_client, publisher, project, zone, instance_name, machine_type, subnetwork_name, fortigate_image):
    instance = compute_v1.Instance(
        name=instance_name,
        machine_type=f'zones/{zone}/machineTypes/{machine_type}',
        disks=[
            compute_v1.AttachedDisk(
                boot=True,
                auto_delete=True,
                initialize_params=compute_v1.AttachedDiskInitializeParams(
                    source_image=fortigate_image
                )
            )
        ],
        network_interfaces=[
            compute_v1.NetworkInterface(
                subnetwork=f'projects/{project}/regions/{region}/subnetworks/{subnetwork_name}',
                access_configs=[compute_v1.AccessConfig(name='External NAT', type_='ONE_TO_ONE_NAT')]
            )
        ],
        metadata=compute_v1.Metadata(items=[
            compute_v1.Items(
                key='startup-script',
                value="""
                    #!/bin/bash
                    # FortiGate bootstrapping and configuration commands
                """
            )
        ])
    )
    operation = compute_client.insert(project=project, zone=zone, instance_resource=instance)
    wait_for_operation(compute_client, project, operation, zone=zone)
    message = f"Created instance: {instance_name}"
    publish_message(publisher, pubsub_topic, message)

def wait_for_operation(compute_client, project, operation, region=None, zone=None):
    while True:
        if zone:
            result = compute_client.zone_operations().get(project=project, zone=zone, operation=operation.name).execute()
        elif region:
            result = compute_client.region_operations().get(project=project, region=region, operation=operation.name).execute()
        else:
            result = compute_client.global_operations().get(project=project, operation=operation.name).execute()
        if result['status'] == 'DONE':
            if 'error' in result:
                raise Exception(result['error'])
            return result
        time.sleep(1)

def main():
    compute_client = compute_v1.NetworksClient()
    publisher = pubsub_v1.PublisherClient()

    # Create VPC Network
    create_vpc_network(compute_client, publisher, project_id, network_name)

    # Create Subnetwork
    subnetwork_client = compute_v1.SubnetworksClient()
    create_subnetwork(subnetwork_client, publisher, project_id, region, network_name, subnetwork_name, subnetwork_cidr)

    # Create Firewall Rule
    firewall_client = compute_v1.FirewallsClient()
    create_firewall_rule(firewall_client, publisher, project_id, network_name, firewall_name)

    # Create FortiGate Instance
    instance_client = compute_v1.InstancesClient()
    create_instance(instance_client, publisher, project_id, zone, instance_name, machine_type, subnetwork_name, fortigate_image)

if __name__ == "__main__":
    main()
