 from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware

  app = FastAPI(title="GELIS Backend API")

  # CORS Middleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "http://qks4s08kg4wwcgc8ww0k4sgc.109.123.245.9.sslip.io",
          "http://qks4s08kg4wwcgc8ww0k4sgc.109.123.245.9.sslip.io:3000",
          "http://localhost:3000",
          "*"  # Development only
      ],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  @app.get("/")
  def root():
      return {"message": "GELIS Backend is running"}

  @app.get("/health")
  def health():
      return {"status": "healthy"}

  @app.get("/api/test")
  def test():
      return {"message": "API is working"}

  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8001)
