# Stage 1: Build
  FROM node:20-alpine AS builder

  WORKDIR /app

  # Copy package files
  COPY package*.json ./
  RUN npm ci --only=production

  # Copy source code
  COPY . .

  # Build the application
  RUN npm run build

  # Stage 2: Production
  FROM nginx:alpine AS production

  # Copy build results from builder stage
  COPY --from=builder /app/build /usr/share/nginx/html

  # Add nginx configuration
  RUN echo 'server { \
      listen 80; \
      root /usr/share/nginx/html; \
      index index.html index.htm; \
      location / { \
          try_files $uri $uri/ /index.html; \
      } \
      location /api { \
          proxy_pass http://gelis-backend:8000; \
          proxy_set_header Host $host; \
          proxy_set_header X-Real-IP $remote_addr; \
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
      } \
  }' > /etc/nginx/conf.d/default.conf

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]
