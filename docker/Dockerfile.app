FROM python:3.11-slim

WORKDIR /app

# Install build deps and netcat (used for a lightweight healthcheck)
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip
RUN pip install uv
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY src/ ./src/

# Lightweight healthcheck that probes the application port
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD nc -z 127.0.0.1 8000 || exit 1

CMD ["sh","-lc","uv run uvicorn voice.interaction.main:app --host 0.0.0.0 --port 8000 || python -m uvicorn voice.interaction.main:app --host 0.0.0.0 --port 8000"]
