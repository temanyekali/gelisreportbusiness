 FROM node:20-alpine AS builder

  WORKDIR /app/frontend

  # Copy package files
  COPY frontend/package*.json ./
  COPY frontend/yarn.lock ./

  # Install dependencies
  RUN yarn install --frozen-lockfile

  # Copy source code
  COPY frontend/ ./

  # Build app
  RUN yarn build

  # Production stage
  FROM node:20-alpine AS production

  WORKDIR /app

  # Install serve globally
  RUN npm install -g serve

  # Copy build from builder stage
  COPY --from=builder /app/frontend/build ./build

  # Expose port
  EXPOSE 3000

  # Start command
  CMD ["serve", "-s", "build", "-l", "3000"]
