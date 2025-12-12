# 🚀 Tutorial Deploy GELIS dengan Nixpacks

Panduan lengkap deployment aplikasi GELIS menggunakan **Nixpacks** buildpack ke Railway, Coolify (modern), dan platform deployment lainnya.

---

## 📋 Apa itu Nixpacks?

**Nixpacks** adalah buildpack modern yang:
- ✅ Auto-detects framework & dependencies
- ✅ Zero configuration (atau minimal config)
- ✅ Fast builds dengan caching
- ✅ Reproducible builds (Nix-based)
- ✅ Multi-language support
- ✅ Used by Railway, Coolify, dan platform modern

**Keunggulan vs Dockerfile:**
- 🚀 Lebih cepat setup (no Dockerfile needed)
- 🔄 Auto-updates dependencies
- 📦 Smaller final images
- ⚙️ Smart caching

---

## 🎯 Platform yang Support Nixpacks

1. **Railway** ⭐ EASIEST
2. **Coolify** (modern version)
3. **Render**
4. **Fly.io** (dengan nixpacks CLI)
5. **Self-hosted** (dengan nixpacks CLI)

---

## 📦 Files Nixpacks untuk GELIS

### Backend Configuration

**File:** `/app/backend/nixpacks.toml`

```toml
[phases.setup]
nixPkgs = ["python310", "gcc", "curl"]

[phases.install]
cmds = [
    "pip install --upgrade pip",
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "mkdir -p uploads"
]

[start]
cmd = "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001}"

[variables]
PORT = "8001"
PYTHONUNBUFFERED = "1"
```

**File:** `/app/backend/Procfile` (Railway fallback)

```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

**File:** `/app/backend/runtime.txt` (Python version)

```
python-3.10
```

### Frontend Configuration

**File:** `/app/frontend/nixpacks.toml`

```toml
[phases.setup]
nixPkgs = ["nodejs_20"]

[phases.install]
cmds = [
    "yarn install --frozen-lockfile"
]

[phases.build]
cmds = [
    "yarn build"
]

[start]
cmd = "npx serve -s build -l ${PORT:-3000}"

[variables]
PORT = "3000"
NODE_ENV = "production"
```

**File:** `/app/frontend/Procfile` (Railway fallback)

```
web: npx serve -s build -p $PORT
```

---

## 🎯 METODE 1: Deploy ke Railway (EASIEST!)

### Persiapan

**Requirements:**
- GitHub account
- Railway account (https://railway.app)
- Code pushed ke GitHub

### Step 1: Buat Project di Railway

1. **Login ke Railway:** https://railway.app
2. **Klik "New Project"**
3. **Pilih "Deploy from GitHub repo"**
4. **Connect GitHub account** (jika belum)
5. **Pilih repository:** `your-username/gelis-app`

### Step 2: Deploy MongoDB

**Di Railway Project:**

1. **Klik "+ New"**
2. **Pilih "Database"**
3. **Pilih "MongoDB"**
4. **Wait** (~2 menit untuk provision)

**Get Connection String:**

1. **Klik MongoDB service**
2. **Tab "Connect"**
3. **Copy "MongoDB Connection URL"**
   ```
   mongodb://mongo:PASSWORD@mongodb.railway.internal:27017
   ```

### Step 3: Deploy Backend

**Add Service:**

1. **Klik "+ New"**
2. **Pilih "GitHub Repo"**
3. **Select repository:** `gelis-app`
4. **Configure Service:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Service Name: gelis-backend

Root Directory: /backend  ← IMPORTANT!

Builder: Nixpacks (auto-detected)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Environment Variables:**

Click **"Variables"** tab:

| Variable | Value |
|----------|-------|
| `MONGO_URL` | `mongodb://mongo:PASSWORD@mongodb.railway.internal:27017/gelis_db` |
| `DB_NAME` | `gelis_db` |
| `SECRET_KEY` | `[Generate 64 char]` |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `43200` |
| `APP_NAME` | `GELIS` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | `https://gelis-frontend.railway.app` |
| `MAX_UPLOAD_SIZE` | `10485760` |
| `UPLOAD_DIR` | `/app/uploads` |

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Deploy:**
1. **Klik "Deploy"**
2. **Wait** (~3-5 menit)
3. **Status:** 🟢 Active

**Get Backend URL:**
```
Settings → Networking → Generate Domain
https://gelis-backend.railway.app
```

### Step 4: Deploy Frontend

**Add Service:**

1. **Klik "+ New"**
2. **Pilih "GitHub Repo"**
3. **Select repository:** `gelis-app`
4. **Configure:**

```
Service Name: gelis-frontend
Root Directory: /frontend
Builder: Nixpacks
```

**Environment Variables:**

| Variable | Value |
|----------|-------|
| `REACT_APP_BACKEND_URL` | `https://gelis-backend.railway.app` |
| `REACT_APP_NAME` | `GELIS` |
| `REACT_APP_VERSION` | `1.0.0` |
| `REACT_APP_ENVIRONMENT` | `production` |

**Deploy:**
1. **Klik "Deploy"**
2. **Wait** (~10-12 menit karena yarn install + build)
3. **Status:** 🟢 Active

**Get Frontend URL:**
```
Settings → Networking → Generate Domain
https://gelis-frontend.railway.app
```

### Step 5: Configure Custom Domain (Optional)

**Backend:**
1. **gelis-backend → Settings → Networking**
2. **Custom Domain → Add Domain**
3. **Enter:** `api.yourdomain.com`
4. **Add DNS CNAME:**
   ```
   CNAME api → [railway-value]
   ```

**Frontend:**
1. **gelis-frontend → Settings → Networking**
2. **Custom Domain → Add Domain**
3. **Enter:** `yourdomain.com`
4. **Add DNS records**

### Step 6: Seed Mock Data

**Via Railway CLI:**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Connect to backend service
railway run python scripts/seed_complete_mockup.py
```

**Or via browser:**

1. **Backend service → Shell**
2. **Run command:**
   ```bash
   python scripts/seed_complete_mockup.py
   ```

### Step 7: Test Application

**Open:**
```
https://gelis-frontend.railway.app
```

**Login:**
```
Username: owner
Password: owner123
```

**Verify:** Dashboard loads dengan mock data!

---

## 🎯 METODE 2: Deploy ke Coolify dengan Nixpacks

### Persiapan

**Requirements:**
- Coolify installed di server
- GitHub repository
- Domain (optional)

### Step 1: Enable Nixpacks di Coolify

**Check Coolify Version:**
- Nixpacks support: Coolify v4+
- Check: Settings → About

**If not supported:**
- Update Coolify: `cd /data/coolify && ./upgrade.sh`

### Step 2: Create MongoDB

**Same as Docker method:**
1. Services → + New Service → MongoDB
2. Configure & Create
3. Get connection string

### Step 3: Deploy Backend with Nixpacks

**Create Application:**

1. **Applications → + New Application**
2. **Select Repository:** `gelis-app`
3. **Configure:**

```
Application Name: gelis-backend
Repository: github.com/user/gelis-app
Branch: main
Base Directory: /backend

Build Pack: Nixpacks  ← Select this!

Port: 8001
```

**Environment Variables:**
- Same as Railway method
- Set MONGO_URL dengan service name: `mongodb://user:pass@gelis-mongodb:27017/gelis_db`

**Deploy:**
- Click "Deploy"
- Nixpacks will auto-detect & build
- Wait ~3-5 menit

### Step 4: Deploy Frontend with Nixpacks

**Create Application:**

```
Application Name: gelis-frontend
Base Directory: /frontend
Build Pack: Nixpacks
Port: 3000
```

**Environment Variables:**
- `REACT_APP_BACKEND_URL`: Backend domain

**Deploy:**
- Click "Deploy"
- Wait ~10-12 menit

### Step 5: Setup Domain & SSL

Same as Docker method:
- Add domains
- Auto-generate SSL
- Done!

---

## 🎯 METODE 3: Deploy dengan Nixpacks CLI (Self-Hosted)

### Install Nixpacks CLI

```bash
# Via curl (Linux/Mac)
curl -sSL https://nixpacks.com/install.sh | bash

# Via cargo (Rust)
cargo install nixpacks

# Via npm
npm install -g nixpacks
```

### Build Backend Image

```bash
cd /app/backend

# Build with Nixpacks
nixpacks build . --name gelis-backend

# Or with Docker integration
nixpacks build . --name gelis-backend --docker

# Run container
docker run -d \
  -p 8001:8001 \
  -e MONGO_URL="mongodb://..." \
  -e SECRET_KEY="..." \
  --name gelis-backend \
  gelis-backend
```

### Build Frontend Image

```bash
cd /app/frontend

# Build
nixpacks build . --name gelis-frontend

# Run
docker run -d \
  -p 3000:3000 \
  -e REACT_APP_BACKEND_URL="http://localhost:8001" \
  --name gelis-frontend \
  gelis-frontend
```

### Using Docker Compose with Nixpacks

**Create:** `/app/docker-compose.nixpacks.yml`

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_DATABASE: gelis_db
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"

  backend:
    build:
      context: ./backend
      dockerfile_inline: |
        FROM nixpacks
    environment:
      MONGO_URL: mongodb://mongodb:27017/gelis_db
      SECRET_KEY: ${SECRET_KEY}
      CORS_ORIGINS: http://localhost:3000
    ports:
      - "8001:8001"
    depends_on:
      - mongodb

  frontend:
    build:
      context: ./frontend
      dockerfile_inline: |
        FROM nixpacks
    environment:
      REACT_APP_BACKEND_URL: http://localhost:8001
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  mongodb_data:
```

**Run:**
```bash
docker-compose -f docker-compose.nixpacks.yml up -d
```

---

## 🔧 Troubleshooting

### Problem 1: "Nixpacks not found"

**Solution:**
```bash
# Verify platform supports Nixpacks
# Railway: ✅ Built-in
# Coolify: ✅ v4+ only
# Others: Install CLI

# Check Coolify version
# Settings → About → Version

# Update Coolify if needed
cd /data/coolify && ./upgrade.sh
```

### Problem 2: "Build failed - requirements.txt not found"

**Cause:** Root directory tidak di-set dengan benar

**Solution:**
```
Pastikan:
- Backend: Root Directory = /backend
- Frontend: Root Directory = /frontend

Railway: Service Settings → Root Directory
Coolify: Application → Base Directory
```

### Problem 3: "Python version mismatch"

**Solution:**
```bash
# Verify runtime.txt exists
cat backend/runtime.txt
# Should show: python-3.10

# Or in nixpacks.toml
[phases.setup]
nixPkgs = ["python310"]  # Not python39 or python311
```

### Problem 4: "Frontend build succeeds but app won't start"

**Cause:** `serve` package tidak terinstall

**Solution:**
```bash
# Add to package.json dependencies
"serve": "^14.2.1"

# Or update start command in nixpacks.toml
[start]
cmd = "npx serve -s build -l $PORT"
```

### Problem 5: "CORS error in production"

**Solution:**
```bash
# Update backend CORS_ORIGINS
CORS_ORIGINS=https://gelis-frontend.railway.app,https://yourdomain.com

# Don't forget to redeploy backend after change
```

### Problem 6: "MongoDB connection refused"

**Railway:**
```
Use internal URL: mongodb.railway.internal
NOT: external URL or localhost
```

**Coolify:**
```
Use service name: gelis-mongodb
NOT: localhost or 127.0.0.1
```

---

## 📊 Nixpacks vs Dockerfile Comparison

| Feature | Nixpacks | Dockerfile |
|---------|----------|------------|
| Setup Time | ⭐⭐⭐⭐⭐ Instant | ⭐⭐⭐ Manual |
| Configuration | ⭐⭐⭐⭐⭐ Minimal | ⭐⭐ Verbose |
| Build Speed (cached) | ⭐⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐ Fast |
| Build Speed (cold) | ⭐⭐⭐⭐ Fast | ⭐⭐⭐ Medium |
| Auto-updates | ✅ Yes | ❌ No |
| Image Size | ⭐⭐⭐⭐ Small | ⭐⭐⭐ Medium |
| Flexibility | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Full |
| Learning Curve | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐ Medium |

**Recommendation:**
- **Nixpacks:** Quick deployment, standard apps
- **Dockerfile:** Complex requirements, full control

---

## 🎯 Environment Variables Reference

### Backend (Required)

```bash
MONGO_URL=mongodb://user:pass@host:27017/gelis_db
DB_NAME=gelis_db
SECRET_KEY=[64 char random]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
CORS_ORIGINS=https://frontend-url.com
```

### Frontend (Required)

```bash
REACT_APP_BACKEND_URL=https://backend-url.com
```

### Platform-Specific Variables

**Railway:**
```bash
PORT=$PORT  # Auto-assigned
DATABASE_URL=$MONGO_URL  # Auto if using Railway MongoDB
```

**Coolify:**
```bash
PORT=8001  # Custom
# Use service names for internal URLs
```

---

## 💡 Best Practices

### 1. Use Root Directory

```bash
# Railway
Service Settings → Root Directory → /backend

# Coolify
Application → Base Directory → /backend

# This allows Nixpacks to find:
- requirements.txt
- package.json
- nixpacks.toml
```

### 2. Separate Services

```bash
# DON'T: One service for backend + frontend
# DO: Two separate services

Service 1: gelis-backend (Root: /backend)
Service 2: gelis-frontend (Root: /frontend)
```

### 3. Use Environment Variables

```bash
# DON'T commit .env files
# DO set via platform UI

Railway: Service → Variables
Coolify: Application → Environment Variables
```

### 4. Enable Auto-Deploy

```bash
# Railway: Settings → Deployments
☑ Deploy on push to main branch

# Coolify: Settings → Webhooks
☑ Auto Deploy on Git Push
```

### 5. Monitor Builds

```bash
# Watch build logs
Railway: Service → Deployments → View Logs
Coolify: Application → Logs → Build Logs

# Common issues:
- Missing dependencies
- Wrong root directory
- Missing env vars
```

---

## 🚀 Deploy Timeline

### Railway (Nixpacks)

| Step | Time |
|------|------|
| MongoDB provision | 2 min |
| Backend build | 3-5 min |
| Frontend build | 10-12 min |
| Domain setup | 2 min |
| **Total** | **~20 min** |

### Coolify (Nixpacks)

| Step | Time |
|------|------|
| MongoDB setup | 2 min |
| Backend deploy | 3-5 min |
| Frontend deploy | 10-12 min |
| Domain & SSL | 5 min |
| **Total** | **~25 min** |

### Self-Hosted (Nixpacks CLI)

| Step | Time |
|------|------|
| Nixpacks install | 1 min |
| Build images | 15 min |
| Start containers | 2 min |
| **Total** | **~18 min** |

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] nixpacks.toml files present
- [ ] Procfile files present (Railway)
- [ ] runtime.txt present (backend)
- [ ] serve package in package.json
- [ ] .env.example files committed
- [ ] .env files NOT committed

### During Deployment
- [ ] Platform selected (Railway/Coolify)
- [ ] MongoDB created
- [ ] Backend root directory set: /backend
- [ ] Frontend root directory set: /frontend
- [ ] All env vars configured
- [ ] Builds succeeded
- [ ] Health checks passing

### Post-Deployment
- [ ] Backend URL accessible
- [ ] Frontend URL accessible
- [ ] Login working
- [ ] API calls working (no CORS errors)
- [ ] Mock data seeded
- [ ] Custom domain setup (if needed)
- [ ] Auto-deploy enabled

---

## 🎉 Kesimpulan

**Nixpacks Deployment** menawarkan:

✅ **Fastest setup** - No Dockerfile needed  
✅ **Smart detection** - Auto-detect framework  
✅ **Modern platform** - Railway, Coolify support  
✅ **Easy configuration** - Minimal toml files  
✅ **Quick deployment** - 20-25 minutes total  

**Best For:**
- Quick deployment
- Standard applications
- Modern platforms (Railway)
- Minimal configuration

**When to use Dockerfile instead:**
- Complex build requirements
- Custom base images
- Multi-stage optimization
- Full control needed

---

**Rekomendasi Deployment:**

🥇 **Railway + Nixpacks** - EASIEST (20 min)  
🥈 **Coolify + Nixpacks** - Fast (25 min)  
🥉 **Coolify + Docker** - Flexible (40 min)  
4️⃣ **Manual Server** - Full Control (2-3 hours)

**Choose Railway + Nixpacks untuk deployment tercepat dan termudah!**

---

**Happy Deploying dengan Nixpacks! 🚀**

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
