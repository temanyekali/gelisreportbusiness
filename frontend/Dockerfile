# Dockerfile.frontend (untuk documentation)
  FROM node:20-alpine

  WORKDIR /app

  # Copy package files
  COPY frontend/package*.json ./

  # Install dependencies
  RUN npm ci --only=production

  # Copy source code
  COPY frontend/ ./

  # Build application
  RUN npm run build

  # Use nginx for serving static files
  FROM nginx:alpine

  # Copy built files
  COPY --from=0 /app/build /usr/share/nginx/html

  # Add nginx configuration
  RUN echo 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /index.html; } }' >
  /etc/nginx/conf.d/default.conf

  EXPOSE 80

  CMD ["nginx", "-g", "daemon off;"]
