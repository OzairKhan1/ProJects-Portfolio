#!/usr/bin/env python3
# The path to "PRIVATE KEY" will be asked for creating a dynamic Inventory. Therefore it is recommended to Pass the path correctly. 

import boto3
import os

ec2 = boto3.client("ec2")

def get_all_instances():
    response = ec2.describe_instances()
    instances = []
    for res in response['Reservations']:
        instances.extend(res['Instances'])
    return instances

# Detect the default private key file if path is not provided
def get_private_key():
    default_keys = ["~/.ssh/id_ed25519", "~/.ssh/id_rsa"]
    print("🔑 Enter full path to private key (or press Enter to use default ~/.ssh keys): ", end="")
    key_path = input().strip()
    if key_path:
        if os.path.exists(os.path.expanduser(key_path)):
            return os.path.expanduser(key_path)
        else:
            print(f"⚠️ Provided key path {key_path} does not exist. Exiting.")
            exit(1)
    # Check default keys
    for k in default_keys:
        k = os.path.expanduser(k)
        if os.path.exists(k):
            return k
    print("⚠️ No default SSH keys found. Exiting.")
    exit(1)

def generate_inventory():

    filename="dynamic_inventory.ini"
    instances = get_all_instances()
    private_key = get_private_key()

    # Filter only running instances with Public IP
    filtered = [
        inst for inst in instances
        if inst['State']['Name'] == 'running' and inst.get('PublicIpAddress')
    ]

    if not filtered:
        print("⚠️ No running instances with public IP found.")
        return

    # Ask user for custom grouping basis
    group_by = input("🔧 Group by 'ami' or 'tag'? (ami/tag/none): ").strip().lower()
    group_name = input("📦 Enter custom group name (or press Enter to skip): ").strip()

    tag_key = None
    tag_value = None
    if group_by == 'tag':
        tag_key = input("🏷️ Enter tag key to group by (e.g., Env): ").strip()
        tag_value = input("🎯 Enter tag value to filter by (or press Enter to match any value): ").strip()
        # Filter instances by tag
        filtered = [
            inst for inst in filtered
            if any(
                t['Key'] == tag_key and
                (tag_value == '' or t['Value'] == tag_value)
                for t in inst.get('Tags', [])
            )
        ]
        if not filtered:
            print(f"⚠️ No running instances found with tag {tag_key}={tag_value or '*'}")
            return

    # Get unique AMI IDs
    image_ids = list(set(inst['ImageId'] for inst in filtered))
    ami_response = ec2.describe_images(ImageIds=image_ids)

    # Map image ID to name
    image_id_to_name = {
        img['ImageId']: img.get('Name', '').lower()
        for img in ami_response['Images']
    }

    inventory_groups = {}

    for inst in filtered:
        image_name = image_id_to_name.get(inst['ImageId'], '')
        user = detect_default_user(image_name)
        ip = inst['PublicIpAddress']

        # Build group
        if group_name:
            group = group_name
        elif group_by == 'ami':
            group = detect_group_name(image_name)
        elif group_by == 'tag' and tag_key:
            tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
            group = tags.get(tag_key,'misc')
        else:
            group = 'ec2_instances'

        # Inventory line with Ansible parameters
        inventory_entry = f"{ip} ansible_user={user} ansible_ssh_private_key_file={private_key} " \
                          f"ansible_ssh_common_args='-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'"

        if group not in inventory_groups:
            inventory_groups[group] = []
        inventory_groups[group].append(inventory_entry)

    # Write inventory
    with open(filename, 'w') as f:
        for group, hosts in inventory_groups.items():
            f.write(f"[{group}]\n")
            for entry in hosts:
                f.write(f"{entry}\n")
            f.write("\n")

    print(f"✅ Inventory written to {filename} with Ansible auto SSH params")

def detect_group_name(image_name):
    image_name = image_name.lower()
    if 'ubuntu' in image_name:
        return 'ubuntu'
    elif 'amzn' in image_name or 'amazon' in image_name:
        return 'amazon'
    elif 'centos' in image_name:
        return 'centos'
    elif 'debian' in image_name:
        return 'debian'
    elif 'rhel' in image_name or 'redhat' in image_name:
        return 'redhat'
    elif 'windows' in image_name:
        return 'windows'
    else:
        return 'misc'

def detect_default_user(image_name):
    image_name = image_name.lower()
    if 'ubuntu' in image_name:
        return 'ubuntu'
    elif 'amzn' in image_name or 'amazon' in image_name:
        return 'ec2-user'
    elif 'centos' in image_name:
        return 'centos'
    elif 'debian' in image_name:
        return 'admin'
    elif 'rhel' in image_name or 'redhat' in image_name:
        return 'ec2-user'
    elif 'windows' in image_name:
        return 'Administrator'
    else:
        return 'ec2-user'

generate_inventory()
