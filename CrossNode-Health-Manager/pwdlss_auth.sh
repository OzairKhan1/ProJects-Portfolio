# The Only Limitation for This Program is that the Private should be present at default location which is ~/.ssh. Then it works fine. I have seen this limitation 
# When the instances were created using Terrafrom. 
# Althouh for private .pem file it works fine no matter where the key is present

# So The best Alternative use to this program is a modified version with name "Prod_Rdy_PwdLess_Aut.sh" if the key is at default location. the program detects the key 
# Automatically. If the key is not at the default location it is recommended to pass the key while running the program. 
# Example: bash Prod_Rdy_PwdLess_Aut.sh /home/ubuntu/projectAnsible/VmHealth_Project/testKey.pem


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

