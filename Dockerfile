 # Build stage
  FROM python:3.11-slim as builder

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      gcc \
      curl \
      && rm -rf /var/lib/apt/lists/*

  # Install Python dependencies
  RUN pip install --no-cache-dir \
      fastapi \
      uvicorn[standard] \
      motor \
      pymongo \
      pydantic \
      python-jose[cryptography] \
      passlib[bcrypt] \
      python-multipart \
      python-dotenv \
      uvicorn[standard] \
      python-jose[cryptography]

  # Install pip secara manual agar tidak ada masalah dengan venv path
  RUN python -m venv --system /opt/venv
  ENV PATH="/opt/venv/bin:$PATH"

  # Copy requirements dan backend application
  COPY backend/requirements.txt .
  COPY backend/ ./backend/

  # Install Python dependencies
  RUN pip install --no-cache-dir -r requirements.txt

  # Production stage
  FROM python:3.11-slim as production

  WORKDIR /app

  # Install runtime system dependencies
  RUN apt-get update && apt-get install -y \
      curl \
      && rm -rf /var/lib/apt/lists/*

  # Copy installed packages from builder
  COPY --from=builder /opt/venv /opt/venv

  # Copy application
  COPY --from=builder /app/backend /app/backend

  # Make venv active
  ENV PATH="/opt/venv/bin:$PATH"

  # Expose port
  EXPOSE 8001

  # Health check
  HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
      CMD curl -f http://localhost:8001/health || exit 1
