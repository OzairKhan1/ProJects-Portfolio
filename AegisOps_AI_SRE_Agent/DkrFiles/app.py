import os
import requests
from flask import Flask, request, jsonify, render_template

# --- OpenTelemetry Tracing Setup ---
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor


# ============================================================
# OpenTelemetry
# ============================================================

provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

tracer = trace.get_tracer(__name__)


# ============================================================
# Ollama Configuration
# ============================================================

OLLAMA_HOST = os.environ.get(
    "OLLAMA_HOST",
    "http://ollama:11434"
)

MODEL_NAME = os.environ.get(
    "OLLAMA_MODEL",
    "llama3.2:1b"
)

SYSTEM_INSTRUCTION = (
    "You are Linux AI, an intelligent Cloud and DevOps incident assistant for Ozair Khan, a Cloud and DevOps Engineer. "
    "Diagnose infrastructure and application problems using logs, metrics, and system information; "
    "perform root-cause analysis and provide clear, actionable solutions across Linux, AWS, networking, containers, Kubernetes, and CI/CD. "
    "Think like an SRE: prioritize reliability, security, automation, and minimal downtime."
)


# ============================================================
# AI Agent
# ============================================================

def call_ai_agent(user_prompt: str) -> str:

    with tracer.start_as_current_span("ai_agent_call"):

        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "system",
                        "content": SYSTEM_INSTRUCTION
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]


# ============================================================
# Web UI (template: templates/index.html)
# ============================================================

# The UI lives in templates/index.html (Flask loads it with render_template).


# ============================================================
# Browser Home Page
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return render_template(
        "index.html",
        model=MODEL_NAME
    )


# ============================================================
# Chat API
# ============================================================

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data or "prompt" not in data:

            return jsonify({
                "error":
                    "Missing 'prompt' in request body"
            }), 400


        user_prompt = data["prompt"]

        agent_reply = call_ai_agent(user_prompt)


        return jsonify({

            "status": "success",

            "agent_response":
                agent_reply

        }), 200


    except Exception as e:

        return jsonify({

            "status": "error",

            "agent_error":
                str(e)

        }), 500


# ============================================================
# Application Start
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )


