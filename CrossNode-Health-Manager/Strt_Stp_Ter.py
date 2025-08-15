import boto3

ec2 = boto3.client("ec2")

def list_all_instances():
    """
    Lists all EC2 instances with their ID, Name, and State.
    """
    response = ec2.describe_instances()
    instances = []
    count = 1
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                "N/A"
            )
            state = instance["State"]["Name"]
            instances.append({
                "number": count,
                "id": instance["InstanceId"],
                "name": name,
                "state": state
            })
            count += 1

    print("\nAll Instances:")
    for inst in instances:
        print(f"{inst['number']}. {inst['name']} ({inst['id']}) - {inst['state']}")

    return instances


def list_instances_by_state(state_name):
    """
    Returns instances in a given state (e.g., 'running', 'stopped')
    """
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": [state_name]}]
    )
    instances = []
    count = 1
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                "N/A"
            )
            instances.append({
                "number": count,
                "id": instance["InstanceId"],
                "name": name,
                "state": state_name
            })
            count += 1

    print(f"\nInstances in state '{state_name}':")
    for inst in instances:
        print(f"{inst['number']}. {inst['name']} ({inst['id']}) - {inst['state']}")

    return instances


def start_instances():
    instances = list_instances_by_state("stopped")
    if not instances:
        print("No stopped instances found.")
        return

    choice = input("\nEnter 'single', 'multiple', 'all', or 'skip' to start instances: ").strip().lower()

    if choice == "all":
        ids = [inst["id"] for inst in instances]
    elif choice == "single":
        num = int(input("Enter the instance number to start: "))
        ids = [instances[num - 1]["id"]]
    elif choice == "multiple":
        nums = input("Enter instance numbers separated by commas (e.g., 1,2,3): ")
        ids = [instances[int(n.strip()) - 1]["id"] for n in nums.split(",")]
    elif choice == "skip":  # ✅ New option
        skips = input("Enter instance numbers to KEEP (comma-separated): ")
        skip_nums = [int(n.strip()) for n in skips.split(",")]
        ids = [inst["id"] for inst in instances if inst["number"] not in skip_nums]
    else:
        print("Invalid choice.")
        return

    ec2.start_instances(InstanceIds=ids)
    print(f"Started instances: {ids}")


def stop_instances():
    instances = list_instances_by_state("running")
    if not instances:
        print("No running instances found.")
        return

    choice = input("\nEnter 'single', 'multiple', 'all', or 'skip' to stop instances: ").strip().lower()

    if choice == "all":
        ids = [inst["id"] for inst in instances]
    elif choice == "single":
        num = int(input("Enter the instance number to stop: "))
        ids = [instances[num - 1]["id"]]
    elif choice == "multiple":
        nums = input("Enter instance numbers separated by commas (e.g., 1,2,3): ")
        ids = [instances[int(n.strip()) - 1]["id"] for n in nums.split(",")]
    elif choice == "skip":  # ✅ New option
        skips = input("Enter instance numbers to KEEP (comma-separated): ")
        skip_nums = [int(n.strip()) for n in skips.split(",")]
        ids = [inst["id"] for inst in instances if inst["number"] not in skip_nums]
    else:
        print("Invalid choice.")
        return

    ec2.stop_instances(InstanceIds=ids)
    print(f"Stopped instances: {ids}")

def terminate_instances():
    # First get all instances that are NOT terminated
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["pending", "running", "stopping", "stopped"]}]
    )

    instances = []
    count = 1
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            name = next(
                (tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"),
                "N/A"
            )
            state = instance["State"]["Name"]
            instances.append({
                "number": count,
                "id": instance["InstanceId"],
                "name": name,
                "state": state
            })
            count += 1

    if not instances:
        print("No terminable instances found.")
        return

    print("\nTerminable Instances:")
    for inst in instances:
        print(f"{inst['number']}. {inst['name']} ({inst['id']}) - {inst['state']}")

    choice = input("\nEnter 'single', 'multiple', 'all', or 'skip' to terminate instances: ").strip().lower()

    if choice == "all":
        ids = [inst["id"] for inst in instances]
    elif choice == "single":
        num = int(input("Enter the instance number to terminate: "))
        ids = [instances[num - 1]["id"]]
    elif choice == "multiple":
        nums = input("Enter instance numbers separated by commas (e.g., 1,2,3): ")
        ids = [instances[int(n.strip()) - 1]["id"] for n in nums.split(",")]
    elif choice == "skip":
        skips = input("Enter instance numbers to KEEP (comma-separated): ")
        skip_nums = [int(n.strip()) for n in skips.split(",")]
        ids = [inst["id"] for inst in instances if inst["number"] not in skip_nums]
    else:
        print("Invalid choice.")
        return

    ec2.terminate_instances(InstanceIds=ids)
    print(f"Terminated instances: {ids}")

def userOption():
    option = input("\nDo you want to proceed or exit the program? (yes/no): ").strip().lower()
    return option


# ===== Main Menu Loop =====
while True:
    print("\n===== EC2 Instance Manager =====")
    print("1. List All Instances")
    print("2. Start Instances")
    print("3. Stop Instances")
    print("4. Terminate Instances")
    print("5. Exit")
    
    choice = input("Choose an option: ").strip()
    
    if choice == '1':
        list_all_instances()
    elif choice == '2':
        start_instances()
    elif choice == '3':
        stop_instances()
    elif choice == '4':
        terminate_instances()
    elif choice == '5':
        break
    else:
        print("Invalid choice. Try again.")
        continue  # Skip asking again if invalid

    option = userOption()
    if option == 'no':
        break
    elif option != 'yes':
        print("\nYou will be proceeded for a new cycle!")

