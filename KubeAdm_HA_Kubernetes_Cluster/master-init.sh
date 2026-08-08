#!/bin/bash
set -e

# ============================================================
# Run this ONLY on the FIRST master node (master-1).
# Usage: ./master-init.sh <LOAD_BALANCER_IP_OR_DNS>
#
# Example: ./master-init.sh 10.0.0.50
#          ./master-init.sh k8s-api.mydomain.com
# ============================================================

LB_ENDPOINT="${1:?Usage: $0 <load-balancer-ip-or-dns>}"

echo "Initializing Kubernetes Control Plane (HA - node 1 of 3)..."
echo "Control plane endpoint: ${LB_ENDPOINT}:6443"

sudo kubeadm init \
  --control-plane-endpoint="${LB_ENDPOINT}:6443" \
  --upload-certs \
  --pod-network-cidr=192.168.0.0/16

echo "Configuring kubectl..."
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

echo "Downloading Calico manifest..."
curl -O https://raw.githubusercontent.com/projectcalico/calico/v3.30.3/manifests/calico.yaml

echo "Patching Calico to use VXLAN instead of IPIP (OCI Security Lists block IP-in-IP/protocol-4 by default; VXLAN uses standard UDP 4789, which is far easier to allow on OCI)..."
sed -i 's/# value: "Always"/value: "Never"/' calico.yaml
sed -i '/name: CALICO_IPV4POOL_IPIP/,/value:/ s/value: "Always"/value: "Never"/' calico.yaml
sed -i '/name: CALICO_IPV4POOL_VXLAN/,/value:/ s/value: "Never"/value: "Always"/' calico.yaml

echo "Installing Calico..."
kubectl apply -f calico.yaml

echo
echo "Waiting for control plane to stabilize..."
sleep 30

echo "Generating fresh certificate key for control-plane join (valid 2 hours)..."
CERT_KEY=$(sudo kubeadm init phase upload-certs --upload-certs 2>/dev/null | tail -1)
JOIN_CMD=$(kubeadm token create --print-join-command)

echo
echo "=================================================================="
echo " CONTROL-PLANE JOIN COMMAND"
echo " Run this on master-2 and master-3 (via master-join.sh):"
echo "=================================================================="
echo "${JOIN_CMD} --control-plane --certificate-key ${CERT_KEY}"
echo
echo " NOTE: certificate-key expires in 2 hours. If it expires before"
echo " you join the other masters, regenerate it with:"
echo "   sudo kubeadm init phase upload-certs --upload-certs"
echo "   kubeadm token create --print-join-command"
echo "=================================================================="
echo
echo " WORKER JOIN COMMAND"
echo " Run this on worker nodes (unchanged from single-master setup):"
echo "=================================================================="
echo "${JOIN_CMD}"
echo "=================================================================="
