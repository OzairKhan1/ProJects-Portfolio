#!/usr/bin/env python3
# The path to "PRIVATE KEY" will be asked for creating a dynamic Inventory. Therefore it is recommended to Pass the path correctly. 

import boto3
import json
import os
import glob


ec2 = boto3.client("ec2")


# -----------------------------
# Detect SSH key automatically
# -----------------------------
def detect_ssh_key():

    env_key = os.getenv("SSH_KEY")
    if env_key and os.path.exists(os.path.expanduser(env_key)):
        return os.path.expanduser(env_key)

    possible = glob.glob(os.path.expanduser("~/.ssh/id_*"))

    for key in possible:
        if not key.endswith(".pub"):
            return key

    return None


# -----------------------------
# Detect default SSH user
# -----------------------------
def detect_default_user(image_name):

    image_name = image_name.lower()

    if "ubuntu" in image_name:
        return "ubuntu"

    if "amzn" in image_name or "amazon" in image_name:
        return "ec2-user"

    if "centos" in image_name:
        return "centos"

    if "debian" in image_name:
        return "admin"

    if "rhel" in image_name or "redhat" in image_name:
        return "ec2-user"

    return "ec2-user"


# -----------------------------
# Detect OS group
# -----------------------------
def detect_group(image_name):

    image_name = image_name.lower()

    if "ubuntu" in image_name:
        return "ubuntu"

    if "amzn" in image_name or "amazon" in image_name:
        return "amazon"

    if "centos" in image_name:
        return "centos"

    if "debian" in image_name:
        return "debian"

    if "rhel" in image_name or "redhat" in image_name:
        return "redhat"

    return "misc"


# -----------------------------
# Get all EC2 instances
# -----------------------------
def get_instances():

    response = ec2.describe_instances()

    instances = []

    for r in response["Reservations"]:
        instances.extend(r["Instances"])

    return instances


# -----------------------------
# Build inventory JSON
# -----------------------------
def build_inventory():

    ssh_key = detect_ssh_key()

    instances = get_instances()

    running = [
        i for i in instances
        if i["State"]["Name"] == "running"
        and i.get("PublicIpAddress")
    ]

    image_ids = list(set(i["ImageId"] for i in running))

    images = ec2.describe_images(ImageIds=image_ids)

    image_map = {
        img["ImageId"]: img.get("Name", "").lower()
        for img in images["Images"]
    }

    inventory = {"_meta": {"hostvars": {}}}

    for inst in running:

        ip = inst["PublicIpAddress"]

        image_name = image_map.get(inst["ImageId"], "")

        user = detect_default_user(image_name)

        group = detect_group(image_name)

        if group not in inventory:
            inventory[group] = {"hosts": []}

        inventory[group]["hosts"].append(ip)

        inventory["_meta"]["hostvars"][ip] = {
            "ansible_user": user,
            "ansible_ssh_private_key_file": ssh_key,
            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
        }

    return inventory


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":

    inventory = build_inventory()

    print(json.dumps(inventory, indent=2))
