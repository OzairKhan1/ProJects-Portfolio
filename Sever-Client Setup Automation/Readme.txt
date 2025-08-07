⚠️ Note: This Setup runs using Gunicorn for improved stability and performance. While this is not a full production-grade server-client architecture, it serves as a highly practical and efficient solution for daily automation and routine data tasks.
There’s always room for improvement — your suggestions are welcome!
Current Design Overview

1: Server Reads from Two Core Files:
token.txt: Stores authentication tokens for validating client requests.
today_data.json: A structured JSON file containing user-specific data mapped to their system-id.

2: Client Requirements:
Each client only needs the server IP address and a valid authentication token to fetch data.

3: Data Storage on Client:
Retrieved data is automatically saved to a predefined directory on the client system for later use or processing.

4:Daily Update Cycle:
The design supports a full-cycle approach. If the today_data.json is updated daily, the system seamlessly adapts to deliver fresh content. 

5: Cron Integration for Automation:
The system can be easily scheduled with cron on the client side to automate periodic data fetching — reducing manual intervention.

6: Security Disclaimer:
While the current setup is functional, security best practices (such as HTTPS, token rotation,
encrypted storage) will be incorporated in future updates
