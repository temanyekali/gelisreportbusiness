FROM python:3.11-slim

  WORKDIR /app

  # Install system dependencies including basic tools
  RUN apt-get update && apt-get install -y \
      gcc \
      curl \
      netcat \
      net-tools \
      procps \
      && rm -rf /var/lib/apt/lists/*

  # Install Python dependencies
  COPY backend/requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy application
  COPY backend/ ./

  # Expose port
  EXPOSE 8000

  # Run application
  CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
