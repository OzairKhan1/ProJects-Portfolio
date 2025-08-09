Ansible-Ready Fully Customizable Dynamic Inventory
Create inventories based on AMI, tag, or a combination of tag and value.

import boto3

ec2 = boto3.client("ec2")

def get_all_instances():
    response = ec2.describe_instances()
    instances = []
    for res in response['Reservations']:
        instances.extend(res['Instances'])
    return instances

def generate_inventory():
    
        filename="dynamic_inventory.ini"
        instances = get_all_instances()

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

            if group_name:
                group = group_name
            elif group_by == 'ami':
                group = detect_group_name(image_name)
            elif group_by == 'tag' and tag_key:
                tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
                print(f"all the tages are: {tags}")
                group = tags.get(tag_key,'misc')
            else:
                group = 'ec2_instances'

            inventory_entry = f"{user}@{ip}"

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

        print(f"✅ Inventory written to {filename}")

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
