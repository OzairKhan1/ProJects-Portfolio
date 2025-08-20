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
http://<your-server-ip>:8501
