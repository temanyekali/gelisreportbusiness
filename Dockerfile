# Build stage untuk dependencies
  FROM python:3.11-slim as builder

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      gcc \
      curl \
      && rm -rf /var/lib/apt/lists/*

  # Copy requirements
  COPY backend/requirements.txt .

  # Install Python dependencies
  RUN pip install --no-cache-dir -r requirements.txt

  # Production stage
  FROM python:3.11-slim

  WORKDIR /app

  # Install runtime system dependencies
  RUN apt-get update && apt-get install -y \
      curl \
      && rm -rf /var/lib/apt/lists/*

  # Copy installed packages from builder
  COPY --from=builder /opt/venv /opt/venv

  # Copy backend application
  COPY backend/ ./backend/

  # Make venv active
  ENV PATH="/opt/venv/bin:$PATH"

  # Expose port
  EXPOSE 8001

  # Health check
  HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
      CMD curl -f http://localhost:8001/health || exit 1

  # Start application
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
