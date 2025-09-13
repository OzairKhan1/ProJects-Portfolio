#!/bin/bash

# Usage: ./open_ports.sh <instance-id> <port1> <port2> ...

INSTANCE_ID=$1
shift
PORTS=("$@")

if [ -z "$INSTANCE_ID" ] || [ ${#PORTS[@]} -eq 0 ]; then
    echo "Usage: $0 <instance-id> <port1> <port2> ..."
    exit 1
fi

# Step 1: Get the security group ID(s) of the instance
SG_IDS=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query "Reservations[*].Instances[*].SecurityGroups[*].GroupId" \
    --output text)

if [ -z "$SG_IDS" ]; then
    echo "No security groups found for instance $INSTANCE_ID"
    exit 1
fi

echo "Security Group(s) found: $SG_IDS"

# Step 2: Add ingress rules for each port
for SG_ID in $SG_IDS; do
    for PORT in "${PORTS[@]}"; do
        echo "Opening port $PORT on security group $SG_ID..."
        aws ec2 authorize-security-group-ingress \
            --group-id "$SG_ID" \
            --protocol tcp \
            --port "$PORT" \
            --cidr 0.0.0.0/0
    done
done

echo "Done!"

