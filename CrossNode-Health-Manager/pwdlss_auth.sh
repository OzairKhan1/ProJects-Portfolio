#!/bin/bash

file="/home/ubuntu/projectAnsible/VmHealth_Project/dynamic_inventory.ini"
key="/home/ubuntu/projectAnsible/VmHealth_Project/testKey.pem"

current_group=""

while IFS= read -r host; do
    # Trim leading/trailing spaces
    host="${host#"${host%%[![:space:]]*}"}"
    host="${host%"${host##*[![:space:]]}"}"

    # Skip empty lines and comment lines starting with # or ;
    [[ -z "$host" || "$host" =~ ^[\#\;] ]] && continue

    # Detect group headers like [taggy]
    if [[ "$host" =~ ^\[.*\]$ ]]; then
        current_group="${host#[}"
        current_group="${current_group%]}"
        echo "📌  Found group: $current_group"
        continue
    fi

    # Skip copying SSH key for Windows groups
    if [[ "$current_group" =~ [Ww]indows ]]; then
        echo "🚫 Skipping $host (Windows instance)"
        continue
    fi

    # Copy key for Linux instances
    echo "➤ Copying SSH key to $host (Group: $current_group)"
    ssh-copy-id -f -o "IdentityFile=$key" -o StrictHostKeyChecking=no "$host"

done < "$file"

