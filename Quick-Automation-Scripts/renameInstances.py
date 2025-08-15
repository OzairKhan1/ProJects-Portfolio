import boto3 


ec2 = boto3.client("ec2")

def get_instance_name(instance):
        """Return the Name tag of an instance, or 'Unnamed' if not set."""
        return next(
            (tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'),
            'Unnamed'
        )

def get_all_instances():
        response = ec2.describe_instances()
        instances = []
        for res in response['Reservations']:
            instances.extend(res['Instances'])
        return instances


def rename_instances():
    
        instances = get_all_instances()
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
                ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': new_name}])
                print(f"Renamed {instance_id} → {new_name}")
            return
    
        # If user didn't choose tag filter, fall back to manual renaming
        print("\nAvailable Instances:")
        for idx, instance in enumerate(instances):
            name = get_instance_name(instance)
            print(f"[{idx}] {instance['InstanceId']} | Name: {name}")
    
        try:
            choice = int(input("Enter the number of the instance to rename: ").strip())
            if 0 <= choice < len(instances):
                new_name = input("Enter the new name for the instance: ").strip()
                instance_id = instances[choice]['InstanceId']
                ec2.create_tags(Resources=[instance_id], Tags=[{'Key': 'Name', 'Value': new_name}])
                print(f"Renamed {instance_id} → {new_name}")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")


if __name__ == '__main__':
    rename_instances()
