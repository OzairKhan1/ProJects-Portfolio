#!/bin/bash
set -e

# ============================================================
# Run this on master-2 and master-3 (NOT master-1).
# Paste the full join command printed by master-init.sh.
# Quoting it is recommended but no longer required - this
# script reassembles all arguments you pass, so
#   ./master-join.sh kubeadm join 10.0.0.50:6443 --token ...
# and
#   ./master-join.sh "kubeadm join 10.0.0.50:6443 --token ..."
# both work identically.
#
# Usage: ./master-join.sh kubeadm join 10.0.0.50:6443 --token abc123.xyz \
#          --discovery-token-ca-cert-hash sha256:.... \
#          --control-plane --certificate-key ....
# ============================================================

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <full control-plane join command printed by master-init.sh>"
  exit 1
fi

# Reassemble ALL arguments, whether quoted or not, instead of only
# reading $1 - this is what prevents the "silently only ran kubeadm
# with no subcommand" failure mode.
JOIN_COMMAND="$*"

echo "About to run:"
echo "  sudo ${JOIN_COMMAND}"
echo

echo "Joining this node as an additional control-plane node..."
sudo $JOIN_COMMAND

if [ ! -f /etc/kubernetes/admin.conf ]; then
  echo "ERROR: /etc/kubernetes/admin.conf was not created - the join did not actually succeed."
  echo "Check the kubeadm output above for the real error and re-run before proceeding."
  exit 1
fi

echo "Configuring kubectl on this master..."
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo
echo "Done. From any master, verify with:"
echo "  kubectl get nodes"
echo "  kubectl get pods -n kube-system | grep etcd"
