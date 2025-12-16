from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  import uvicorn

  app = FastAPI(title="GELIS Backend API", version="1.0.0")

  # CORS Configuration - DIPERBAIKI
  allowed_origins = [
      "http://qks4s4s4w4w4cwwc8ww0k4sgc.109.123.245.9.sslip.io",
      "http://qks4s4s4w4w4cwwc8ww0k4sgc.109.123.245.9.sslip.io:3000",
      "http://localhost:3000",
      "http://127.0.0.1:3000",
      "*"  # Untuk development
  ]

  app.add_middleware(
      CORSMiddleware,
      allow_origins=allowed_origins,
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
      allow_headers=["*"],
  )

  @app.get("/")
  def root():
      return {
          "message": "Backend is running",
          "app": "GELIS Backend API",
          "version": "1.0.0",
          "status": "healthy"
      }

  @app.get("/health")
  def health():
      return {
          "status": "healthy",
          "app": "GELIS Backend",
          "version": "1.0.0"
      }

  @app.get("/api/test")
  def test():
      return {
          "message": "API is working",
          "timestamp": "2025-12-16",
          "endpoints": {
              "root": "/",
              "health": "/health",
              "test": "/api/test"
          }
      }

  @app.get("/api/info")
  def info():
      return {
          "app": "GELIS Business Reporting",
          "description": "Multi-business management system",
          "features": [
              "Business Management",
              "Financial Tracking",
              "Order Management",
              "User Management",
              "Reports & Analytics"
          ]
      }

  if __name__ == "__main__":
      print("Starting GELIS Backend on port 8001...")
      uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
