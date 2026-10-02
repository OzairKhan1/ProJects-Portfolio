# 🐧 Linux AI — SRE Incident Response Agent

A lightweight, containerized **AI-powered Linux SRE assistant** for troubleshooting infrastructure issues, analyzing incidents, and performing root-cause analysis.

Linux AI combines **Flask, Ollama, Docker, and OpenTelemetry** to provide a simple web-based interface and REST API for interacting with a local AI model.

---

## ✨ What It Does

Linux AI is designed as an SRE-focused troubleshooting assistant that can help with:

* 🔥 High CPU and memory usage
* 💾 Disk and I/O problems
* 🌐 Network and connectivity issues
* 📋 Linux system logs
* 🚨 Service and server incidents
* 🔍 Root Cause Analysis (RCA)
* 🛠️ Linux troubleshooting and remediation guidance
* 📊 Infrastructure reliability and scalability

The goal is to provide an AI assistant that can reason about common Linux infrastructure incidents and guide an engineer through investigation and resolution.

---

## 🖥️ Web Interface

The application provides a browser-based chat interface.

The interface includes:

* Real-time chat experience
* SRE-focused example prompts
* Loading/typing indicator
* Responsive design
* Error handling
* Direct communication with the `/chat` API

---

## 🏗️ Architecture

```text
                     Browser
                        │
                        │ HTTP
                        ▼
              ┌───────────────────┐
              │    Flask App      │
              │    Linux AI       │
              │    Port: 5000     │
              └─────────┬─────────┘
                        │
                        │ HTTP
                        │ /api/chat
                        ▼
              ┌───────────────────┐
              │      Ollama       │
              │    Port: 11434    │
              └─────────┬─────────┘
                        │
                        ▼
                 llama3.2:1b
```

Both services run together using **Docker Compose** and communicate through the internal Docker network.

---

## 🛠️ Technology Stack

| Technology         | Purpose                       |
| ------------------ | ----------------------------- |
| **Python**         | Application development       |
| **Flask**          | Web server and REST API       |
| **Ollama**         | Local AI model serving        |
| **Llama 3.2 1B**   | AI inference model            |
| **Docker**         | Application containerization  |
| **Docker Compose** | Multi-container orchestration |
| **OpenTelemetry**  | Application tracing           |
| **Requests**       | Flask → Ollama communication  |

---

## 📁 Project Structure

```text
linux-ai-incident-agent/
│
├── app.py
│   └── Flask application, web UI, REST API and AI integration
│
├── dockerfile
│   └── Flask application container definition
│
├── docker-compose.yml
│   └── Flask + Ollama service orchestration
│
├── requirements.txt
│   └── Python dependencies
│
├── test.py
│   └── Command-line client for testing /chat
│
└── README.md
    └── Project documentation
```

---

## 🚀 Run with Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/hamza-cloud2004/linux-ai-incident-agent.git
cd linux-ai-incident-agent
```

### 2. Build and Start the Services

```bash
docker compose up -d --build
```

This starts:

* Flask AI Agent
* Ollama
* Docker network
* Persistent Ollama model storage

### 3. Download the AI Model

Ollama runs as a model server, while the model is downloaded separately:

```bash
docker exec ollama ollama pull llama3.2:1b
```

Verify the model:

```bash
docker exec ollama ollama list
```

You should see:

```text
llama3.2:1b
```

---

## 🌐 Access the Web Interface

Once the containers are running, open:

```text
http://localhost:5001
```

The browser interface communicates with the Flask `/chat` endpoint automatically.

---

## 🔌 REST API

The application also exposes a REST API.

### Endpoint

```text
POST /chat
```

### Request

```json
{
  "prompt": "Why is my Linux server using high CPU?"
}
```

### cURL Example

```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Why is my Linux server using high CPU?"}'
```

### Example Response

```json
{
  "status": "success",
  "agent_response": "High CPU usage can be investigated by..."
}
```

---

## 🧪 Test from Python

Install the required client dependency:

```bash
python3 -m pip install requests
```

Run:

```bash
python3 test.py
```

The CLI client sends prompts to the deployed `/chat` API and displays the AI response.

---

## ⚙️ Configuration

The Flask application supports the following environment variables:

```text
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
```

The default configuration is already suitable for Docker Compose.

---

## 📡 Observability

The application is instrumented with **OpenTelemetry**.

Tracing covers the Flask application and AI agent calls, allowing the project to be integrated with observability and distributed-tracing platforms.

---

## 🔐 Deployment Architecture

The project separates the web/API layer from the AI inference layer:

```text
┌─────────────────────────────┐
│        Flask App            │
│                             │
│  • Web Interface            │
│  • REST API                 │
│  • AI Request Handling      │
└──────────────┬──────────────┘
               │
               │ HTTP
               ▼
┌─────────────────────────────┐
│          Ollama             │
│                             │
│      llama3.2:1b            │
└─────────────────────────────┘
```

Docker Compose provides the networking and service orchestration between the two containers.

---

## 🎯 Project Objective

Linux AI demonstrates how AI can be integrated into modern **Cloud, DevOps, and SRE workflows** to assist with:

* Incident investigation
* Linux troubleshooting
* Root Cause Analysis
* Infrastructure reliability
* Observability
* Containerized deployments
* AI-assisted operations

---

## 👨‍💻 Author

**Ozair Khan**
**Cloud & DevOps Engineer**

Focused on **Cloud Infrastructure, DevOps, Kubernetes, Automation, Observability, and AI-assisted Operations**.
