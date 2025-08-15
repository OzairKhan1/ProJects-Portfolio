#!/bin/bash

KEY_PATH="/home/ubuntu/projectAnsible/VmHealth_Project/winKey.pem"   # Your PEM file path
CSV_FILE="./windows_ec2_passwords.csv"
INI_FILE="./windows_inventory.ini"
MAX_RETRIES=10
RETRY_INTERVAL=30   # seconds

# Ask user for optional tag filtering
read -p "Enter tag key (or press Enter for all Windows instances): " TAG_KEY
if [[ -n "$TAG_KEY" ]]; then
    read -p "Enter tag value: " TAG_VALUE
    TAG_FILTER="Name=tag:$TAG_KEY,Values=$TAG_VALUE"
else
    TAG_FILTER=""
fi

# Check if key file exists
if [[ ! -f "$KEY_PATH" ]]; then
  echo "❌ ERROR: Private key file not found at $KEY_PATH"
  exit 1
fi

# Write CSV header
echo "InstanceID,PublicIP,AdministratorPassword" > "$CSV_FILE"

# Write Ansible inventory header
echo "[windows]" > "$INI_FILE"

# Build AWS CLI filters
FILTERS=(--filters "Name=platform,Values=windows" "Name=instance-state-name,Values=running")
if [[ -n "$TAG_FILTER" ]]; then
    FILTERS+=("$TAG_FILTER")
fi

# Get matching instance IDs
aws ec2 describe-instances \
  "${FILTERS[@]}" \
  --query "Reservations[*].Instances[*].InstanceId" \
  --output text | tr '\t' '\n' | while read -r ID; do

    [[ -z "$ID" ]] && continue

    echo "Processing instance: $ID"

    IP=$(aws ec2 describe-instances \
        --instance-ids "$ID" \
        --query "Reservations[0].Instances[0].PublicIpAddress" \
        --output text)

    PASSWORD=""
    ATTEMPT=0

    # Retry fetching password
    until [[ -n "$PASSWORD" || $ATTEMPT -ge $MAX_RETRIES ]]; do
      PASSWORD=$(aws ec2 get-password-data \
          --instance-id "$ID" \
          --priv-launch-key "$KEY_PATH" \
          --query PasswordData \
          --output text)
      if [[ -z "$PASSWORD" ]]; then
        echo "Password not ready yet, retrying in $RETRY_INTERVAL seconds... (Attempt $((ATTEMPT+1))/$MAX_RETRIES)"
        sleep $RETRY_INTERVAL
      fi
      ((ATTEMPT++))
    done

    if [[ -z "$PASSWORD" ]]; then
      echo "⚠️ Warning: Password still empty after retries for instance $ID"
    fi

    # Write to CSV
    echo "$ID,$IP,$PASSWORD" >> "$CSV_FILE"

    # Write to Ansible inventory
    echo "$IP ansible_user=Administrator ansible_password=\"$PASSWORD\" ansible_connection=winrm" >> "$INI_FILE"

    echo "Instance: $ID"
    echo "Public IP: $IP"
    echo "Administrator Password: $PASSWORD"
    echo "----------------------------------------------"

done

# Add inventory group vars
cat <<EOL >> "$INI_FILE"

[windows:vars]
ansible_port=5985
ansible_winrm_transport=ntlm
ansible_winrm_scheme=http
ansible_winrm_server_cert_validation=ignore
EOL

echo "✅ CSV saved to: $CSV_FILE"
echo "✅ Ansible inventory saved to: $INI_FILE"

