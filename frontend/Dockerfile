# Build stage
  FROM node:20-alpine AS builder

  # Set working directory
  WORKDIR /app

  # Copy package files
  COPY frontend/package*.json ./
  COPY frontend/yarn.lock ./

  # Install dependencies
  RUN yarn install --frozen-lockfile --network-timeout 1000000

  # Copy frontend source code
  COPY frontend/ ./

  # Create .env file for production
  ARG REACT_APP_API_URL
  ARG REACT_APP_APP_NAME
  ARG REACT_APP_VERSION

  ENV REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000/api}
  ENV REACT_APP_APP_NAME=${REACT_APP_APP_NAME:-GELIS}
  ENV REACT_APP_VERSION=${REACT_APP_VERSION:-1.0.0}
  ENV GENERATE_SOURCEMAP=false
  ENV DISABLE_ESLINT_PLUGIN=true
  ENV INLINE_RUNTIME_CHUNK=false
  ENV DISABLE_HOT_RELOAD=true
  ENV REACT_APP_ENABLE_VISUAL_EDITS=false
  ENV ENABLE_HEALTH_CHECK=true

  # Build the application
  RUN yarn build

  # Production stage
  FROM nginx:alpine AS production

  # Remove default nginx config
  RUN rm /etc/nginx/conf.d/default.conf

  # Copy custom nginx config
  COPY nginx.conf /etc/nginx/conf.d/default.conf

  # Copy built application
  COPY --from=builder /app/build /usr/share/nginx/html

  # Add healthcheck
  HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/ || exit 1

  # Expose port
  EXPOSE 80

  # Start nginx
  CMD ["nginx", "-g", "daemon off;"]
