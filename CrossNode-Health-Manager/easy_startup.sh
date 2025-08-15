#!/bin/bash
# easy_startup.sh
# Runs your EC2 startup tasks in sequence.

# Exit if any 
set -e

echo "===== Step 1: Creating dynamic inventory for Linux ====="
python3 dynamic_inventory.py

localHostIp=$(curl -s ifconfig.me)

read -p "Does the local host have the same key as the Linux nodes? (yes/no): " option

if [[ "$option" != "yes" ]]; then
    echo "Removing local host ($localHostIp) from dynamic_inventory.ini..."
    sed -i "/$localHostIp/d" /home/ubuntu/projectAnsible/VmHealth_Project/dynamic_inventory.ini
    echo "Local host removed from inventory."
else
    echo "Keeping local host in inventory."
fi

echo "===== Step 2: Setting up passwordless authentication ====="
bash pwdlss_auth.sh

echo "===== Step 3: Testing connection with Ansible ping ====="
ansible-playbook -i dynamic_inventory.ini linux_check.yaml

echo "===== Step 4: Creating dynamic inventory for Windows====="
bash win_dynamic_Inv.sh

echo "===== Step 5: Testing connection to Windoes Servers  with Ansible win_ping ====="
ansible-playbook -i windows_inventory.ini win_check.yaml

echo "===== All steps completed successfully! ====="

