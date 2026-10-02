# 🛡️ AegisOps — AI SRE Incident Response Agent

A lightweight, containerized **AI-powered SRE assistant** for troubleshooting Linux infrastructure, analyzing incidents, and performing root-cause analysis, with a modern web UI.

AegisOps combines **Flask, Ollama, Docker, and OpenTelemetry** to provide a polished browser-based chat interface and a REST API for interacting with a local AI model. Everything runs on your own machine, with no external AI API and no API keys.

---

## ⚡ Quick Start

All you need is **Git** and **Docker Compose**.

```bash
# 1. Clone the repository
git clone https://github.com/OzairKhan1/ProJects-Portfolio.git

# 2. Enter the project directory
cd ProJects-Portfolio/3-AegisOps_AI_SRE_Agent

# 3. Start everything
docker-compose up -d
```

Then open **http://host/ip:5000** in your browser.

> **Don't have Docker Compose?** The repository includes an installation guide for Docker and Docker Compose. Install it first, then come back to the steps above.

--- 

### Stop / Restart / Clean Up

```bash
docker-compose stop        # stop the containers (keeps everything)
docker-compose start       # start them again
docker-compose down        # remove the containers (model volume is kept)
docker-compose logs -f     # follow the logs
```

> If your system uses Docker Compose v2, `docker compose` (with a space) works the same way as `docker-compose`.

---

## ✨ What It Does

AegisOps is an SRE-focused troubleshooting assistant that helps with:

* 🔥 High CPU and memory usage
* 💾 Disk and I/O problems
* 🌐 Network and connectivity issues
* 📋 Linux system logs
* 🚨 Service and server incidents
* 🔍 Root Cause Analysis (RCA)
* 🛠️ Troubleshooting and remediation guidance
* 📊 Infrastructure reliability and scalability

The goal is an AI assistant that reasons about common infrastructure incidents and guides an engineer through investigation and resolution.

---

## 🖥️ Web Interface

AegisOps ships with a modern, responsive chat interface, served from a dedicated `templates/index.html` file.

**Highlights**

* 🎬 **Cinematic intro**: the designer's name animates in the center of the screen and then settles at the top middle of the header (click or press Esc to skip)
* 🌌 Animated gradient background with a subtle grid and a glass-style interface
* 💬 Real-time chat with avatars, message bubbles and a typing indicator
* 🧑‍💻 **Code blocks** in AI replies rendered terminal-style with a one-click **Copy** button
* 🔥 SRE-focused quick-start cards: High CPU, High Memory, Disk I/O, Server Outage
* ⌨️ Enter to send, Shift+Enter for a new line, auto-growing input box
* 📱 Fully responsive layout (desktop and mobile)
* 🎨 One-place theming through CSS variables at the top of `index.html`
* ⚠️ Friendly error handling when the AI backend is unreachable

---

## 🏗️ Architecture

```text
                     Browser
                        │
                        │ HTTP
                        ▼
              ┌───────────────────┐
              │    Flask App      │
              │    AegisOps       │
              │                   │
              │  app.py           │  ← API + AI integration
              │  templates/       │
              │    index.html     │  ← Web UI
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

Both services run together using **Docker Compose** and communicate over the internal Docker network.

**Separation of concerns**

| Layer        | File                   | Responsibility                                          |
| ------------ | ---------------------- | ------------------------------------------------------- |
| **Backend**  | `app.py`               | Flask routes, REST API, Ollama calls, OpenTelemetry     |
| **Frontend** | `templates/index.html` | UI, styling, animations, chat logic (HTML + CSS + JS)   |

The backend serves the UI with Flask's `render_template("index.html")`, so the interface can be redesigned without touching the API code.

---

## 🛠️ Technology Stack

| Technology         | Purpose                                  |
| ------------------ | ---------------------------------------- |
| **Python**         | Application development                  |
| **Flask**          | Web server, REST API and templating      |
| **HTML / CSS / JS** | Web interface (single template file)    |
| **Ollama**         | Local AI model serving                   |
| **Llama 3.2 1B**   | AI inference model                       |
| **Docker**         | Application containerization             |
| **Docker Compose** | Multi-container orchestration            |
| **OpenTelemetry**  | Application tracing                      |
| **Requests**       | Flask → Ollama communication             |

---

## 📁 Project Structure

```text
3-AegisOps_AI_SRE_Agent/
│
├── app.py
│   └── Flask application, REST API, AI integration, OpenTelemetry
│
├── templates/
│   └── index.html
│       └── Web UI (HTML, CSS and JavaScript)
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

## 🔌 REST API

The UI is just one client. The same backend exposes a REST API.

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
curl -X POST http://localhost:5000/chat \
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

Install the client dependency:

```bash
python3 -m pip install requests
```

Run:

```bash
python3 test.py
```

The CLI client sends prompts to the running `/chat` API and prints the AI response.

---

## ⚙️ Configuration

The Flask application supports these environment variables:

```text
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.2:1b
```

The defaults already work with Docker Compose. To use a different model, pull it into Ollama and set `OLLAMA_MODEL` in `docker-compose.yml`.

### Customizing the UI

All colors are defined as CSS variables at the top of `templates/index.html`:

```css
:root {
    --a1: #fbbf24;   /* accent 1 */
    --a2: #f97316;   /* accent 2 */
    --a3: #e11d48;   /* accent 3 */
}
```

Change these (and their `-rgb` twins) to re-theme the whole interface. After editing the template, rebuild the container:

```bash
docker-compose up -d --build
```

---

## 📡 Observability

The application is instrumented with **OpenTelemetry**. Tracing covers the Flask application and the AI agent calls, so the project can be integrated with observability and distributed-tracing platforms.

---

## 🎯 Project Objective

AegisOps demonstrates how AI can be integrated into modern **Cloud, DevOps and SRE workflows** to assist with:

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

Focused on **Cloud Infrastructure, DevOps, Kubernetes, Automation, Observability and AI-assisted Operations**.

📂 More projects: [ProJects-Portfolio](https://github.com/OzairKhan1/ProJects-Portfolio)
