FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install runtime dependencies from requirements.txt (kept intentionally minimal)
COPY requirements.txt ./
RUN python -m venv /opt/venv \
	&& . /opt/venv/bin/activate \
	&& pip install --upgrade pip \
	&& pip install -r requirements.txt \
	&& pip install uv

# Copy project sources
COPY . .
ENV PATH="/opt/venv/bin:$PATH"

# Run Uvicorn (production use should replace with gunicorn + uvicorn workers)
CMD ["uvicorn", "voice.interaction.main:app", "--host", "0.0.0.0", "--port", "8000"]
