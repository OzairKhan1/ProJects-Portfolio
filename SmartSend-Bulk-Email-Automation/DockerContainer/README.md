**Follow these 3 simple steps**  

**1: Pull the code from DockerHub using the command**:
```bash
docker pull ozairkhan1/smartsend:latest  
```
**2: Run the container with volume and port binding to keep track of sent emails (to avoid duplicates):**:  
   ```bash
   docker run -d -p 8501:8501 -v smartsend_logs:/SmartSend/logs ozairkhan1/smartsend:latest
   ```
**3: Access the application in your browser**:  
```bash
   http://<your-server-ip>:8501
   ```
        
------------------ UseFul Docker Commands ---------------------------------------  

# 🐳 Docker Useful Commands

```bash
# --- Image Management ---
# List all images
docker images
# Build an image
docker build -t <image_name>:<tag> .
# Remove an image
docker rmi <image_name_or_id>
# Remove all dangling (untagged) images
docker image prune
# Force remove an image even if used by containers
docker rmi -f <image_name_or_id>

# --- Container Management ---
# List all running containers
docker ps
# List all containers (running + stopped)
docker ps -a
# Run a container in background with port mapping
docker run -d -p <host_port>:<container_port> <image_name>:<tag>
# Run a container interactively
docker run -it <image_name>:<tag> /bin/bash
# Stop a running container
docker stop <container_id_or_name>
# Remove a container
docker rm <container_id_or_name>
# Remove all stopped containers
docker container prune

# --- Volume Management ---
# List all volumes
docker volume ls
# Inspect a volume
docker volume inspect <volume_name>
# Remove a volume
docker volume rm <volume_name>
# Remove all unused volumes
docker volume prune

# --- Network & Misc ---
# List networks
docker network ls
# Inspect a network
docker network inspect <network_name>
# Show Docker system usage summary
docker system df
# Remove unused data (images, containers, volumes, networks)
docker system prune -a

