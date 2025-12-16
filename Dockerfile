# Build stage (untuk frontend)
  FROM node:20-alpine AS builder

  WORKDIR /app

  # Copy package files hanya jika ada
  COPY frontend/package*.json ./
  COPY frontend/yarn.lock ./

  # Install dependencies & build frontend
  RUN yarn install --frozen-lockfile && yarn build

  # Production stage untuk backend
  FROM python:3.11-slim AS production

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      gcc \
      && rm -rf /var/lib/apt/lists/*

  # Copy Python dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy backend code
  COPY backend/ ./

  # Copy frontend build result
  COPY --from=builder /app/frontend/build ./static

  # Expose port
  EXPOSE 8000

  # Start command
  CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
