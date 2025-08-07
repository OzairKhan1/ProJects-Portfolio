import socket
import requests
from datetime import datetime
import os

# Identify system
system_id = socket.gethostname()

# Server settings
SERVER_URL = f"http://Public_ip:8000/get_data/{system_id}"
API_TOKEN = "Your_Tokens"
HEADERS = {"X-Auth-Token": API_TOKEN}

# Timestamp for filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Cross-platform output directory
home_dir = os.path.expanduser("~")
output_dir = os.path.join(home_dir, "fetched_data")
os.makedirs(output_dir, exist_ok=True)

# Final output path
output_file = os.path.join(output_dir, f"{system_id}_{timestamp}.txt")

try:
    response = requests.get(SERVER_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()

    try:
        json_data = response.json()
        if not isinstance(json_data, dict):
            raise ValueError("Unexpected JSON format (not a dictionary)")

        data = json_data.get("data", "No data returned in 'data' field")

        # ✅ Convert data to string if needed (list, dict, etc.)
        if not isinstance(data, str):
            data = str(data)

    except Exception as json_err:
        data = f"⚠️ Failed to parse JSON: {json_err}\nRaw response:\n{response.text}"

    # Save the data
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(data)

    print(f"✅ Data saved: {output_file}")

except Exception as e:
    print(f"❌ Fetch failed: {e}")
