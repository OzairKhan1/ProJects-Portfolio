# Python ka official slim image use kar rahe hain taaki container light weight rahe
FROM python:3.10-slim

# Working directory set kar rahe hain
WORKDIR /app

# System dependencies agar zaroori hon
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Pehle requirements file copy karo taaki caching achhi ho
COPY requirements.txt .

# Python dependencies install karo
RUN pip install --no-cache-dir -r requirements.txt

# Baaki sara project code copy karo (app.py, etc.)
COPY . .

# Flask port expose karo
EXPOSE 5000

# Flask app run karne ki command
CMD ["python", "app.py"]
