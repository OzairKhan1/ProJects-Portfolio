#! /bin/bash

file=Path_to_your_hosts/Servers             # Replace this with you path to file
key=Path_to_Your_Public_key                 # Replace this with your path to Key

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

    echo "➤ Copying SSH key to $host (Group: $current_group)"
    ssh-copy-id -f -o "IdentityFile=$key" -o StrictHostKeyChecking=no "$host"
    
done < "$file"
  
