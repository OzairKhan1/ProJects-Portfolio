#!/bin/bash
set -e

# ============================================================
# Run this on master-2 and master-3 (NOT master-1).
# Paste the full join command printed by master-init.sh,
# wrapped in quotes, as the single argument.
#
# Usage: ./master-join.sh "kubeadm join 10.0.0.50:6443 --token abc123.xyz \
#          --discovery-token-ca-cert-hash sha256:.... \
#          --control-plane --certificate-key ...."
# ============================================================

JOIN_COMMAND="${1:?Usage: $0 \"<full control-plane join command printed by master-init.sh>\"}"

echo "Joining this node as an additional control-plane node..."
sudo $JOIN_COMMAND

echo "Configuring kubectl on this master..."
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo
echo "Done. From any master, verify with:"
echo "  kubectl get nodes"
echo "  kubectl get pods -n kube-system | grep etcd"
