# To RUN the Program it is recommened to pass the "PATH TO PRIVATE KEY", If the Key is not available at the default location.
# Example: bash Prod_Rdy_PwdLess_Aut.sh /home/ubuntu/projectAnsible/VmHealth_Project/testKey.pem
# For default location the Program detects it automatically 

#!/bin/bash

file="/home/ubuntu/Terraform/forEach_MetaArgument/ProJects-Portfolio/CrossNode-Health-Manager/dynamic_inventory.ini"

# Optional key path argument
USER_KEY="$1"
current_group=""

# Function to attempt ssh-copy-id with a specific key
try_key() {
    local host="$1"
    local key="$2"
    echo "   🔑 Trying key: $key"
    ssh-copy-id \
        -i "$key" \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        "$host" &>/dev/null
    return $?
}

# Build key list
declare -a KEYS

# If user passed key explicitly
if [[ -n "$USER_KEY" && -f "$USER_KEY" ]]; then
    KEYS+=("$USER_KEY")
else
    # Try ssh-agent keys first
    AGENT_KEYS=$(ssh-add -L 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        echo "🔐 Using ssh-agent loaded keys"
        USE_AGENT=true
    fi

    # Scan common key locations
    for k in ~/.ssh/id_* ~/.ssh/*.pem; do
        [[ -f "$k" && ! "$k" =~ \.pub$ ]] && KEYS+=("$k")
    done
fi

while IFS= read -r line; do
    line="$(echo "$line" | xargs)"

    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^[\#\;] ]] && continue

    # Detect group headers like [webservers]
    if [[ "$line" =~ ^\[.*\]$ ]]; then
        current_group="${line#[}"
        current_group="${current_group%]}"
        echo "📌 Found group: $current_group"
        continue
    fi

    # Extract only the IP/hostname (first field)
    host="$(echo "$line" | awk '{print $1}')"

    # Extract ansible_user from the line (fallback to ec2-user)
    ansible_user="$(echo "$line" | grep -oP 'ansible_user=\K\S+')"
    [[ -z "$ansible_user" ]] && ansible_user="ec2-user"

    # Build the full ssh target
    ssh_target="${ansible_user}@${host}"

    # Skip Windows groups
    if [[ "$current_group" =~ [Ww]indows ]]; then
        echo "🚫 Skipping $ssh_target (Windows)"
        continue
    fi

    echo "➤ Processing $ssh_target"
    success=false

    # Try agent first
    if [[ "$USE_AGENT" == true ]]; then
        ssh-copy-id \
            -o StrictHostKeyChecking=no \
            -o UserKnownHostsFile=/dev/null \
            "$ssh_target" &>/dev/null && success=true
    fi

    # Try discovered/provided keys
    if [[ "$success" == false ]]; then
        for key in "${KEYS[@]}"; do
            if try_key "$ssh_target" "$key"; then
                success=true
                break
            fi
        done
    fi

    if [[ "$success" == true ]]; then
        echo "   ✅ Key copied to $ssh_target successfully"
    else
        echo "   ❌ No valid key found for $ssh_target"
    fi

done < "$file"
