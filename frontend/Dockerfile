# Multi-stage build
  FROM node:20-alpine as builder

  WORKDIR /app

  # Copy package files
  COPY package*.json ./

  # Install dependencies
  RUN npm ci

  # Copy source code
  COPY . .

  # Build aplikasi
  RUN npm run build

  # Production stage
  FROM nginx:alpine

  # Copy build results
  COPY --from=builder /app/build /usr/share/nginx/html

  # Copy nginx config
  COPY nginx.conf /etc/nginx/conf.d/default.conf

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]

  frontend/nginx.conf:
  server {
      listen 80;
      root /usr/share/nginx/html;
      index index.html;

      location / {
          try_files $uri $uri/ /index.html;
      }

      # Proxy API ke backend
      location /api {
          proxy_pass http://gelis-backend:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      }
  }
