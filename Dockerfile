 # Build stage
  FROM node:20-alpine AS builder

  WORKDIR /app

  # Copy package files
  COPY frontend/package*.json ./
  COPY frontend/yarn.lock ./

  # Install dependencies
  RUN yarn install --frozen-lockfile --network-timeout 1000000

  # Copy source code
  COPY frontend/ ./

  # Environment variables for build
  ENV NODE_ENV=production
  ENV GENERATE_SOURCEMAP=false
  ENV INLINE_RUNTIME_CHUNK=false

  ARG REACT_APP_API_URL
  ENV REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000/api}

  # Build application
  RUN yarn build

  # Production stage with nginx
  FROM nginx:alpine AS production

  # Copy build result
  COPY --from=builder /app/build /usr/share/nginx/html

  # Expose port
  EXPOSE 80

  # Start nginx
  CMD ["nginx", "-g", "daemon off;"]
