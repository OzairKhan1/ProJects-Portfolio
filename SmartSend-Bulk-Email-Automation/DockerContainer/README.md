There are Only 3 Steps 
**1: Pull the code from DockerHub using the command** 
```bash
docker pull ozairkhan1/smartsend:latest
```
**2: Mount the Volumes to Keep track of the Sent Emails Inorder to Avoid Multiple Sending**
'''bash
docker run -p 8501:8501 -v smartsend_logs:/SmartSend/logs ozairkhan1/smartsend:latest
'''
