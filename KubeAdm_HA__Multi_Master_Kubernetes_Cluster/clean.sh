
#!/bin/bash

set -e

sudo kubeadm reset -f

sudo rm -rf $HOME/.kube

sudo systemctl restart containerd

echo "Node has been reset."
