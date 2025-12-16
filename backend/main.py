from fastapi.middleware.cors import CORSMiddleware
  import os

  app = FastAPI(title="GELIS Backend API")

  # CORS Middleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=[
          "http://qks4s08kg4wwcgc8ww0k4sgc.109.123.245.9.sslip.io",
          "http://qks4s08kg4wwcgc8ww0k4sgc.109.123.245.9.sslip.io:3000",
          "http://localhost:3000",
          "*"  # Remove di production
      ],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
