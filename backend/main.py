  echo 'from fastapi import FastAPI

  app = FastAPI()

  @app.get("/")
  def root():
      return {"message": "Backend is running"}

  if name == "main":
      import uvicorn
      uvicorn.run(app, host="0.0.0.0", port=8001)' > backend/main.py

  3. **Commit dan push:**
  ```bash
  git add backend/main.py
  git commit -m "Fix main.py indentation"
  git push
