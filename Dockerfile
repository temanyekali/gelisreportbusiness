# Simple Dockerfile untuk GELIS
  FROM node:20-alpine as frontend-build

  # Build Frontend
  WORKDIR /app/frontend
  COPY frontend/package*.json ./
  RUN npm install
  COPY frontend/ ./
  RUN npm run build

  # Backend
  FROM python:3.11-slim
  WORKDIR /app

  # Install system deps
  RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

  # Install Python deps
  COPY backend/requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy backend code
  COPY backend/ ./

  # Copy frontend build
  COPY --from=frontend-build /app/frontend/build /app/static

  # Install simple HTTP server
  RUN pip install fastapi uvicorn

  # Expose port
  EXPOSE 8000

  # Run both frontend and backend
  CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000 & python -m http.server 3000 --directory 
  /app/static"]
