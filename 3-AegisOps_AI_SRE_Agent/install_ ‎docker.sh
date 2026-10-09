sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER && newgrp docker
sudo usermod -aG docker gitlab-runner && newgrp docker
echo "Docker installed $(docker --version)"
