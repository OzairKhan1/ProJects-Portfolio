# Stage 1: Builder
FROM python:3.10-slim AS builder

WORKDIR /build

# Install build dependencies (for compiling some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /SmartSend

# Copy the virtual environment from builder
COPY --from=builder /venv /venv

# Activate venv for all commands
ENV PATH="/venv/bin:$PATH"

# Copy only your app code (not build tools, caches, etc.)
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "smartsend.py", "--server.port=8501", "--server.address=0.0.0.0"]

