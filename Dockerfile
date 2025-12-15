FROM node:20-alpine as frontend-build

  WORKDIR /app/frontend
  COPY frontend/package*.json ./
  RUN npm install
  COPY frontend/ ./
  RUN npm run build

  FROM python:3.11-slim
  WORKDIR /app

  RUN apt-get update && apt-get install -y gcc curl netcat-openbsd && rm -rf /var/lib/apt/lists/*
  COPY backend/requirements.txt ./
  RUN pip install -r requirements.txt
  COPY backend/ ./

  # Copy frontend build
  COPY --from=frontend-build /app/frontend/build /app/static

  # Install simple HTTP server for static files
  RUN pip install fastapi uvicorn python-multipart

  EXPOSE 8000

  # Start backend
  CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
