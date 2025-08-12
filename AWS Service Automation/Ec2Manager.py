import boto3
import time
import datetime
import json
import os

class EC2Manager: 
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.regions = region
        
    def get_all_instances(self):
        response = self.ec2.describe_instances()
        instances = []
        for res in response['Reservations']:
            instances.extend(res['Instances'])
        return instances

    def check_instances_exist(self, instances):
        return len(instances) > 0
        
  
    def ensure_instances_available(self):
        instances = self.get_all_instances()
        if not self.check_instances_exist(instances):
            print("No EC2 instances found. Please create an instance first.")
            return None
        return instances

    #1
    def list_instance_ids(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}")
    #2
    def list_instance_tags(self, instances):
        for inst in instances:
            print(f"\nInstance ID: {inst['InstanceId']}")
            for tag in inst.get('Tags', []):
                print(f"  {tag['Key']}: {tag['Value']}")
    #3
    def list_private_ips(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, Private IP: {inst.get('PrivateIpAddress')}")
    #4
    def list_public_ips(self, instances):
        for inst in instances:
            if inst['State']['Name'] == 'running':
                print(f"Instance ID: {inst['InstanceId']}, Public IP: {inst.get('PublicIpAddress')}")
                
    #5
    def list_subnets(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, Subnet ID: {inst.get('SubnetId')}")
            
    #6
    def list_dns(self, instances):
        for inst in instances:
            if inst['State']['Name'] == 'running':
                print(f"Instance ID: {inst['InstanceId']}, Public DNS: {inst.get('PublicDnsName')}")

    #7
    def list_instance_types(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, Type: {inst.get('InstanceType')}")

    #8
    def list_instance_states(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, State: {inst['State']['Name']}")
            
    #9
    def list_availability_zones(self, instances):
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, AZ: {inst['Placement']['AvailabilityZone']}")

    #10, 11, 12, 13
    def prompt_instance_action(self, action_name):
        instances = self.ensure_instances_available()
        if not instances:
            return

        print("\nAvailable Instances:")
        for i, inst in enumerate(instances):
            name = next((tag['Value'] for tag in inst.get('Tags', []) if tag['Key'] == 'Name'), 'Unnamed')
            print(f"[{i}] ID: {inst['InstanceId']} | Name: {name} | State: {inst['State']['Name']}")

        choice = input(f"\nDo you want to {action_name} (1) a single instance, (2) multiple, or (3) all? ")

        if choice == '1':
            index = int(input("Enter instance number: "))
            self._run_action(action_name, [instances[index]['InstanceId']])
        elif choice == '2':
            indices = input("Enter comma-separated instance numbers: ").split(',')
            ids = [instances[int(i.strip())]['InstanceId'] for i in indices]
            self._run_action(action_name, ids)
        elif choice == '3':
            ids = [inst['InstanceId'] for inst in instances]
            self._run_action(action_name, ids)
        else:
            print("Invalid choice.")

    def _run_action(self, action_name, instance_ids):
        for instance_id in instance_ids:
            if action_name == 'start':
                self.start_instance(instance_id)
            elif action_name == 'stop':
                self.stop_instance(instance_id)
            elif action_name == 'reboot':
                self.reboot_instance(instance_id)
            elif action_name == 'terminate':
                self.terminate_instance(instance_id)
            
    
    def start_instance(self, instance_id):
        print(f"Starting instance: {instance_id}")
        self.ec2.start_instances(InstanceIds=[instance_id])
        
    
    def stop_instance(self, instance_id):
        print(f"Stopping instance: {instance_id}")
        self.ec2.stop_instances(InstanceIds=[instance_id])

    
    def reboot_instance(self, instance_id):
        print(f"Rebooting instance: {instance_id}")
        self.ec2.reboot_instances(InstanceIds=[instance_id])

    
    def terminate_instance(self, instance_id):
        print(f"Terminating instance: {instance_id}")
        self.ec2.terminate_instances(InstanceIds=[instance_id])

    #15: This is Helper function for RenameInstances
    def get_instance_name(self, instance):
        """Return the Name tag of an instance, or 'Unnamed' if not set."""
        return next(
            (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
            'Unnamed'
        )

    def rename_instances(self,instances):
        instances = self.get_all_instances()
        if not instances:
            print("No instances found to rename.")
            return
    
        print("\nDo you want to rename based on a specific tag filter?")
        tag_choice = input("Enter 'y' to filter by tag or press Enter to rename manually: ").strip().lower()
    
        if tag_choice == 'y':
            key = input("Enter the Tag Key to filter (e.g., Env): ").strip()
            value = input("Enter the Tag Value to filter (e.g., Web): ").strip()
            filtered = [i for i in instances if any(
                t['Key'] == key and t['Value'].lower() == value.lower()
                for t in i.get('Tags', [])
            )]
            if not filtered:
                print(f"No instances found with tag {key}={value}")
                return
            print(f"\nFound {len(filtered)} instance(s) with tag {key}={value}")
            base_name = input("Enter base name for renaming (e.g., web): ").strip()
            for idx, instance in enumerate(filtered, 1):
                instance_id = instance['InstanceId']
                new_name = f"{base_name}-{idx}"
                self.ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': new_name}])
                print(f"Renamed {instance_id} → {new_name}")
            return
    
        # If user didn't choose tag filter, fall back to manual renaming
        print("\nAvailable Instances:")
        for idx, instance in enumerate(instances):
            name = self.get_instance_name(instance)
            print(f"[{idx}] {instance['InstanceId']} | Name: {name}")
    
        try:
            choice = int(input("Enter the number of the instance to rename: ").strip())
            if 0 <= choice < len(instances):
                new_name = input("Enter the new name for the instance: ").strip()
                instance_id = instances[choice]['InstanceId']
                self.ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': new_name}])
                print(f"Renamed {instance_id} → {new_name}")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    # Helper fUnction for KeyPair Creation and Saving Option 16
    def create_and_save_key(self, key_name):
        try:
            key_pair = self.ec2.create_key_pair(KeyName=key_name)
            private_key = key_pair['KeyMaterial']
            key_path = f"{key_name}.pem"

            with open(key_path, 'w') as file:
                file.write(private_key)
            os.chmod(key_path, 0o400)

            print(f"✅ Key pair '{key_name}' created and saved to: {key_path}")
        except Exception as e:
            print(f"❌ Error creating key pair: {str(e)}")


    #16  Main Function for 
    def create_instance_interactive(self):
        region = self.regions
        ami_map = {
            "Ubuntu 22.04": "ami-080e1f13689e07408",
            "Ubuntu 20.04": "ami-0fc5d935ebf8bc3bc",
            "Amazon Linux 2023": "ami-0f403e3180720dd7e",
            "Amazon Linux 2": "ami-0c101f26f147fa7fd",
            "Red Hat 9": "ami-05a4db8bdfe937387",
            "Debian 12": "ami-0f5daaa3a7fb3378b",
            "macOs": "ami-043cfcc8b0832d11a",
            "Windows": "ami-0c9fb5d338f1eec43"
            
        }
    
        print("\nAvailable AMIs in us-east-1:")
       
        for i, (name, ami_id) in enumerate(ami_map.items(), 1):
            print(f"{i}. {name} - {ami_id}")
    
        use_default_ami = input(f"\nUse default AMIs from {region}? (yes/no): ").strip().lower()
    
        if use_default_ami != 'yes':
            region = input("Enter custom region (e.g., us-west-1): ").strip()
            custom_ami = input("Enter the AMI ID to use: ").strip()
            ami_map = {f"Custom AMI": custom_ami}
            self.regions = region  # Update class region
    
        # Select AMI
        print("\nChoose AMI by number:")
        ami_choices = list(ami_map.items())
        for idx, (name, ami_id) in enumerate(ami_choices, 1):
            print(f"{idx}. {name} - {ami_id}")
        selection = int(input("Enter your choice: "))
        image_id = ami_choices[selection - 1][1]
    
        # How many instances
        count = int(input("How many instances to launch?: ").strip())

        #Choose a type
        instance_type = input("Enter the instance type (e.g., t2.micro): ").strip()
        # Key Name
        key_name = input("Enter key pair name to use: ").strip()
        self.create_and_save_key(key_name)
    
        # Name tag
        name_tag = input("Enter 'Name' tag for your instances: ").strip()
    
        # Extra tags
        tags = [{"Key": "Name", "Value": name_tag}]
        more_tags = input("Do you want to add more tags? (yes/no): ").strip().lower()
        if more_tags == 'yes':
            while True:
                key = input("Enter tag key (leave empty to stop): ").strip()
                if not key:
                    break
                value = input("Enter tag value: ").strip()
                tags.append({"Key": key, "Value": value})
    
        # Launch EC2
        ec2 = boto3.resource("ec2", region_name=self.regions)
        try:
            instances = ec2.create_instances(
                ImageId=image_id,
                MinCount=count,
                MaxCount=count,
                InstanceType=instance_type,
                KeyName=key_name,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': tags
                }]
            )
            instance_ids = [instance.id for instance in instances]
            print(f"🚀 Successfully launched {count} instance(s)")
            print("Instance IDs:", ', '.join(instance_ids))
            
        except Exception as e:
            print(f"❌ Error launching instance(s): {e}")

    #19
    def list_ebs_volumes(self):
        volumes = self.ec2.describe_volumes()['Volumes']
        for vol in volumes:
            print(f"Volume ID: {vol['VolumeId']}, State: {vol['State']}, Size: {vol['Size']} GiB")
            
    #17
    def export_instance_metadata(self):
        instances = self.get_all_instances()
        with open("instances_metadata.json", "w") as f:
            json.dump(instances, f, default=str, indent=2)
        print("Exported instance metadata to instances_metadata.json")

    #18
    def auto_stop_idle_instances(self):
        instances = self.get_all_instances()
        for inst in instances:
            if inst['State']['Name'] == 'running' and not inst.get('PublicIpAddress'):
                print(f"Auto-stopping likely idle instance: {inst['InstanceId']}")
                self.stop_instance(inst['InstanceId'])

    #19
    def check_ssh_keys(self):
        instances = self.get_all_instances()
        for inst in instances:
            print(f"Instance ID: {inst['InstanceId']}, Key Name: {inst.get('KeyName', 'No key')}")

    #20
    def calculate_uptime(self):
        instances = self.get_all_instances()
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        for inst in instances:
            launch_time = inst['LaunchTime']
            uptime = now - launch_time
            print(f"Instance ID: {inst['InstanceId']}, Uptime: {uptime}")
   

    #21
    def generate_inventory(self, filename="dynamic_inventory.ini"):
        instances = self.get_all_instances()

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
        ami_response = self.ec2.describe_images(ImageIds=image_ids)

        # Map image ID to name
        image_id_to_name = {
            img['ImageId']: img.get('Name', '').lower()
            for img in ami_response['Images']
        }

        inventory_groups = {}

        for inst in filtered:
            image_name = image_id_to_name.get(inst['ImageId'], '')
            user = self.detect_default_user(image_name)
            ip = inst['PublicIpAddress']

            if group_name:
                group = group_name
            elif group_by == 'ami':
                group = self.detect_group_name(image_name)
            elif group_by == 'tag' and tag_key:
                tags = {t['Key']: t['Value'] for t in inst.get('Tags', [])}
                group = tags.get(tag_key, 'misc')
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

    def detect_group_name(self, image_name):
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

    def detect_default_user(self, image_name):
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

    def show_menu(self):
        while True:
            print("\n=== EC2 MANAGER ===")
            print("1. Show Instance IDs")
            print("2. Show Tags")
            print("3. Show Private IPs")
            print("4. Show Public IPs")
            print("5. Show Subnet IDs")
            print("6. Show DNS Names")
            print("7. Show Instance Types")
            print("8. Show Instance States")
            print("9. Show Availability Zones")
            print("10. Start Instances")
            print("11. Stop Instances")
            print("12. Reboot Instances")
            print("13. Terminate Instances")
            print("14. Rename Instance")
            print("15. List EBS Volumes")
            print("16. Create New Instance")
            print("17. Export Instance Metadata to JSON")
            print("18. Auto-Stop Idle Instances")
            print("19. Check SSH Keys")
            print("20. Calculate Instance Uptime")
            print("21. Generate Dynamic Inventory")
            print("0. Exit")

            choice = input("Enter your choice: ")
            instances = self.ensure_instances_available()
            if choice == '0':
                break
            elif not instances and choice not in ['13']:
                continue

            if choice == '1':
                self.list_instance_ids(instances)
            elif choice == '2':
                self.list_instance_tags(instances)
            elif choice == '3':
                self.list_private_ips(instances)
            elif choice == '4':
                self.list_public_ips(instances)
            elif choice == '5':
                self.list_subnets(instances)
            elif choice == '6':
                self.list_dns(instances)
            elif choice == '7':
                self.list_instance_types(instances)
            elif choice == '8':
                self.list_instance_states(instances)
            elif choice == '9':
                self.list_availability_zones(instances)
            elif choice == '10':
                self.prompt_instance_action('start')
            elif choice == '11':
                self.prompt_instance_action('stop')
            elif choice == '12':
                self.prompt_instance_action('reboot')
            elif choice == '13':
                self.prompt_instance_action('terminate')
            elif choice == '14':
                self.rename_instances(instances)
            elif choice == '15':
                self.list_ebs_volumes()
            elif choice == '16':
                self.create_instance_interactive()
            elif choice == '17':
                self.export_instance_metadata()
            elif choice == '18':
                self.auto_stop_idle_instances()
            elif choice == '19':
                self.check_ssh_keys()
            elif choice == '20':
                self.calculate_uptime()
            elif choice == '21':
                self.generate_inventory()
            else:
                print("Invalid option.")
            choice = input("Do you want to proceed or exit the program? (yes/no):").strip().lower()
            if choice != 'yes':
                break
            else:
                pass
                

if __name__ == '__main__':
    manager = EC2Manager(input("Default Area is [ us-east-1 ]: Do you want to proceed with this or change it: ") or "us-east-1")
    manager.show_menu()
    
     
