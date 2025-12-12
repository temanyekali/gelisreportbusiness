# 🚀 Tutorial Step-by-Step Deploy GELIS dengan Coolify

Panduan praktis deployment aplikasi GELIS menggunakan Coolify - dari nol hingga production ready dalam 30 menit!

---

## 📋 Yang Anda Butuhkan

✅ **Server/VPS** dengan:
- Ubuntu 20.04/22.04 LTS
- RAM minimum 2 GB (Recommended: 4 GB)
- CPU 2 Core (Recommended: 4 Core)
- Storage 20 GB+
- IP Public & SSH Access

✅ **Domain** (optional tapi recommended):
- Contoh: `gelis.yourdomain.com`
- Sudah pointing ke IP server

✅ **Repository GitHub**:
- Code GELIS sudah push ke GitHub
- Public atau Private repository

---

## 🎯 Langkah 1: Persiapan Server (10 menit)

### 1.1 Login ke Server

```bash
# SSH ke server Anda
ssh root@IP_SERVER_ANDA

# Atau dengan user non-root
ssh username@IP_SERVER_ANDA
```

### 1.2 Update Sistem

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install basic tools
sudo apt install -y curl wget git ufw
```

### 1.3 Setup Firewall

```bash
# Allow SSH (PENTING! Jangan sampai kelupaan)
sudo ufw allow 22/tcp

# Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Coolify ports
sudo ufw allow 8000/tcp  # Coolify dashboard
sudo ufw allow 6001/tcp  # Coolify realtime
sudo ufw allow 6002/tcp  # Coolify proxy

# Enable firewall
sudo ufw --force enable

# Verify
sudo ufw status
```

**Expected Output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                    ALLOW       Anywhere
8000/tcp                   ALLOW       Anywhere
6001/tcp                   ALLOW       Anywhere
6002/tcp                   ALLOW       Anywhere
```

---

## 🎯 Langkah 2: Install Coolify (5 menit)

### 2.1 Install Docker (Prerequisite)

```bash
# Download dan install Docker
curl -fsSL https://get.docker.com | sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Logout dan login kembali untuk apply group changes
# Atau jalankan:
newgrp docker

# Verify Docker installed
docker --version
# Expected: Docker version 24.x.x atau lebih baru

# Test Docker
docker ps
# Should show empty list (no errors)
```

### 2.2 Install Coolify

```bash
# Download dan jalankan installer Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**Proses instalasi akan:**
1. Download Coolify components
2. Setup Docker Compose
3. Create database
4. Generate admin password
5. Start services

**⏱️ Waktu: ~3-5 menit**

**Output akhir akan menampilkan:**
```
🎉 Coolify installed successfully!

📍 Access your Coolify instance at: http://YOUR_IP:8000

🔑 Login credentials:
   Email: admin@example.com
   Password: [RANDOM_PASSWORD_HERE]

⚠️  IMPORTANT: Change your password immediately after first login!
```

**📝 CATAT PASSWORD INI!** Anda akan membutuhkannya untuk login pertama kali.

---

## 🎯 Langkah 3: Setup Coolify Dashboard (5 menit)

### 3.1 Akses Coolify Dashboard

1. Buka browser
2. Akses: `http://IP_SERVER_ANDA:8000`
3. Login dengan credentials yang ditampilkan saat instalasi

**Tampilan Login:**
- Field Email: `admin@example.com`
- Field Password: [password dari output installer]

### 3.2 Initial Setup

Setelah login pertama kali:

**Step 1: Change Password**
- Klik profile icon (pojok kanan atas)
- Pilih "Settings"
- Tab "Security"
- Change password
- Save

**Step 2: Update Email** (Optional)
- Tab "General"
- Update email dengan email Anda
- Save

**Step 3: Setup SSH Key** (Untuk Private Repo)
- Settings → "SSH Keys"
- Klik "Generate New SSH Key"
- Copy public key
- Add ke GitHub (Settings → Deploy Keys)

---

## 🎯 Langkah 4: Persiapan GitHub Repository (3 menit)

### 4.1 Pastikan Files Penting Ada

Cek repository Anda memiliki file-file ini:

```
/
├── backend/
│   ├── Dockerfile          ← MUST HAVE
│   ├── requirements.txt    ← MUST HAVE
│   ├── server.py
│   └── ...
├── frontend/
│   ├── Dockerfile          ← MUST HAVE
│   ├── nginx.conf          ← MUST HAVE
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

### 4.2 Jika Belum Ada, Buat Files Berikut:

#### **backend/Dockerfile**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### **frontend/Dockerfile**

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source
COPY . .

# Build
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy build
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### **frontend/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### 4.3 Push ke GitHub

```bash
git add .
git commit -m "Add Docker configuration for Coolify"
git push origin main
```

---

## 🎯 Langkah 5: Deploy MongoDB di Coolify (2 menit)

### 5.1 Add Database Service

**Langkah-langkah:**

1. **Klik "Services"** di sidebar Coolify
2. **Klik "+ Add Service"** atau **"New Service"**
3. **Pilih "MongoDB"** dari daftar databases
4. **Configure:**
   ```
   Service Name: gelis-mongodb
   Version: 7.0
   Database Name: gelis_db
   Username: gelis_user
   Password: [Generate strong password - klik icon generate]
   Root Password: [Generate strong password - klik icon generate]
   ```
5. **Klik "Create"**

**⏱️ Proses: ~2-3 menit untuk pull image dan start container**

### 5.2 Catat Connection String

Setelah status menjadi "Running":

1. **Klik service "gelis-mongodb"**
2. **Tab "Configuration"**
3. **Catat Connection String:**
   ```
   mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
   ```

**📝 IMPORTANT:** 
- Hostname adalah **service name**: `gelis-mongodb`
- Port **internal**: `27017`
- **Jangan expose** MongoDB ke internet!

---

## 🎯 Langkah 6: Deploy Backend (FastAPI) (5 menit)

### 6.1 Create Application

1. **Klik "Applications"** di sidebar
2. **Klik "+ New Application"**
3. **Pilih "Public Repository"** (atau Private jika sudah setup SSH key)

### 6.2 Configure Repository

**For Public Repository:**
```
Git Repository URL: https://github.com/USERNAME/gelis-app.git
Branch: main
```

**For Private Repository:**
```
Git Repository URL: git@github.com:USERNAME/gelis-app.git
Branch: main
```

### 6.3 Configure Application

```
Application Name: gelis-backend
Base Directory: /backend
Port: 8001
Build Pack: Dockerfile
Dockerfile Path: ./Dockerfile
```

**Advanced Settings:**
```
Health Check Enabled: ✓
Health Check Path: /
Health Check Interval: 30s
```

### 6.4 Environment Variables

**Klik tab "Environment Variables"** dan tambahkan:

```env
# MongoDB - IMPORTANT: Use internal Docker network hostname!
MONGO_URL=mongodb://gelis_user:YOUR_PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db

# Database
DB_NAME=gelis_db

# JWT Configuration
SECRET_KEY=GENERATE_64_CHAR_RANDOM_STRING_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Application
APP_NAME=GELIS
ENVIRONMENT=production
DEBUG=False

# CORS - Update dengan domain Anda
CORS_ORIGINS=https://gelis.yourdomain.com,https://www.gelis.yourdomain.com

# Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/uploads
```

**Generate SECRET_KEY:**
```bash
# Di terminal local
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 6.5 Deploy Backend

1. **Klik "Deploy"**
2. **Monitor logs** di tab "Logs"
3. **Wait** hingga status menjadi "Running" (~3-5 menit first deploy)

**Deployment Steps yang terjadi:**
1. Clone repository
2. Build Docker image
3. Start container
4. Health check
5. Mark as healthy

---

## 🎯 Langkah 7: Deploy Frontend (React) (10 menit)

### 7.1 Create Frontend Application

1. **Applications → "+ New Application"**
2. **Connect same repository**

### 7.2 Configure Frontend

```
Application Name: gelis-frontend
Base Directory: /frontend
Port: 80
Build Pack: Dockerfile
Dockerfile Path: ./Dockerfile
```

### 7.3 Environment Variables

```env
# Backend URL - Update dengan domain backend Anda
REACT_APP_BACKEND_URL=https://api.gelis.yourdomain.com

# App Info
REACT_APP_NAME=GELIS
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
```

**⚠️ IMPORTANT:** 
- Environment variables `REACT_APP_*` akan di-embed ke build
- Ganti URL backend dengan URL public backend Anda
- Jika belum ada domain, gunakan: `http://IP_SERVER:8001`

### 7.4 Deploy Frontend

1. **Klik "Deploy"**
2. **Monitor build logs** (~10-15 menit karena yarn install)
3. **Wait** hingga status "Running"

**Build Steps:**
1. Clone repository
2. Install Node.js dependencies (yarn install) - paling lama
3. Build production bundle (yarn build)
4. Create Nginx container
5. Start serving

---

## 🎯 Langkah 8: Setup Domain & SSL (5 menit)

### 8.1 Setup DNS Records

**Di control panel domain Anda** (Cloudflare, Namecheap, dll):

```
# Backend API
Type: A
Name: api.gelis (atau api)
Value: IP_SERVER_ANDA
TTL: Auto atau 3600

# Frontend
Type: A
Name: gelis (atau @)
Value: IP_SERVER_ANDA
TTL: Auto atau 3600

Type: A
Name: www.gelis (atau www)
Value: IP_SERVER_ANDA
TTL: Auto atau 3600
```

**⏱️ Wait:** DNS propagation bisa 5 menit - 48 jam (biasanya < 1 jam)

**Check DNS Propagation:**
```bash
# Di terminal local
nslookup api.gelis.yourdomain.com
nslookup gelis.yourdomain.com

# Atau check online:
# https://dnschecker.org
```

### 8.2 Configure Domain di Coolify

**Backend:**
1. **Masuk ke app "gelis-backend"**
2. **Klik tab "Domains"**
3. **Klik "+ Add Domain"**
4. **Input:** `api.gelis.yourdomain.com`
5. **Toggle "Generate SSL Certificate"** → ON (akan auto-generate Let's Encrypt)
6. **Save**

**Frontend:**
1. **Masuk ke app "gelis-frontend"**
2. **Klik tab "Domains"**
3. **Add Domain:** `gelis.yourdomain.com`
4. **Add Domain:** `www.gelis.yourdomain.com` (add second domain)
5. **Toggle SSL** untuk kedua domain → ON
6. **Save**

**⏱️ Wait:** SSL generation ~1-2 menit

**Verify SSL:**
```bash
# Check SSL certificate
curl -I https://gelis.yourdomain.com
curl -I https://api.gelis.yourdomain.com

# Should return 200 OK with secure connection
```

---

## 🎯 Langkah 9: Setup Auto-Deploy (2 menit)

### 9.1 Enable Webhook di Coolify

**Backend:**
1. **Masuk ke "gelis-backend"**
2. **Tab "Settings"**
3. **Toggle "Auto Deploy on Git Push"** → ON
4. **Copy Webhook URL** yang muncul

**Frontend:**
1. **Masuk ke "gelis-frontend"**
2. **Tab "Settings"**
3. **Toggle "Auto Deploy on Git Push"** → ON
4. **Copy Webhook URL**

### 9.2 Setup Webhook di GitHub

**Di GitHub Repository:**

1. **Settings → Webhooks → Add webhook**
2. **Payload URL:** [Paste Webhook URL dari Backend]
3. **Content type:** `application/json`
4. **Which events:** "Just the push event"
5. **Active:** ✓
6. **Add webhook**

**Repeat untuk Frontend** (jika ingin auto-deploy frontend juga)

**✅ Sekarang:** Setiap `git push` ke main branch akan auto-deploy!

---

## 🎯 Langkah 10: Verifikasi & Testing (3 menit)

### 10.1 Check Services Status

**Di Coolify Dashboard:**

1. **Services:**
   - ✅ gelis-mongodb: Running
   
2. **Applications:**
   - ✅ gelis-backend: Healthy
   - ✅ gelis-frontend: Healthy

### 10.2 Test Backend API

```bash
# Test health endpoint
curl https://api.gelis.yourdomain.com/

# Should return: {"detail":"Not Found"} atau similar
# (404 is OK, berarti service running)

# Test API endpoint
curl https://api.gelis.yourdomain.com/api/

# Should return API response
```

### 10.3 Test Frontend

**Buka browser:**
```
https://gelis.yourdomain.com
```

**Should show:**
- ✅ GELIS Login Page
- ✅ No HTTPS warnings
- ✅ No CORS errors in console
- ✅ Can login with demo credentials

**Demo Login:**
```
Username: owner
Password: owner123
```

### 10.4 Test Full Flow

1. **Login** dengan owner credentials
2. **Navigate** ke Dashboard → should load data
3. **Check** semua menu (Orders, Reports, Users, dll)
4. **Create** test order
5. **Verify** di database (via Coolify logs atau MongoDB client)

---

## 🎯 Langkah 11: Monitoring & Maintenance

### 11.1 Monitor Logs

**Backend Logs:**
```
Coolify → Applications → gelis-backend → Logs
```

**Frontend Logs:**
```
Coolify → Applications → gelis-frontend → Logs
```

**MongoDB Logs:**
```
Coolify → Services → gelis-mongodb → Logs
```

### 11.2 Setup Alerts (Optional)

**Di Coolify:**
1. **Settings → Notifications**
2. **Add Notification Channel:**
   - Email
   - Slack
   - Discord
   - Telegram
3. **Configure alerts:**
   - Service down
   - High CPU/Memory
   - Deployment failures

### 11.3 Backup Database

**Manual Backup:**
1. **Services → gelis-mongodb**
2. **Tab "Backups"**
3. **Klik "Create Backup Now"**

**Auto Backup:**
1. **Enable "Automatic Backups"**
2. **Set schedule:** Daily, Weekly, or Monthly
3. **Save**

---

## ✅ Deployment Checklist

Pastikan semua ini sudah ✓:

### Server Setup
- [x] Server updated (apt update & upgrade)
- [x] Firewall configured (UFW)
- [x] Docker installed
- [x] Coolify installed

### Coolify Setup
- [x] Coolify accessible di http://IP:8000
- [x] Password changed
- [x] Email updated (optional)
- [x] SSH key setup (for private repos)

### Database
- [x] MongoDB service created
- [x] MongoDB status: Running
- [x] Connection string noted

### Backend
- [x] Application created
- [x] Repository connected
- [x] Environment variables set
- [x] Deployment successful
- [x] Health check passing
- [x] Domain configured (if applicable)
- [x] SSL certificate generated

### Frontend
- [x] Application created
- [x] Repository connected
- [x] REACT_APP_BACKEND_URL correct
- [x] Build successful
- [x] Deployment successful
- [x] Domain configured
- [x] SSL certificate generated

### Testing
- [x] Backend API responding
- [x] Frontend accessible
- [x] Login working
- [x] Dashboard loading
- [x] CRUD operations working
- [x] No CORS errors
- [x] No console errors

### Auto-Deploy
- [x] Webhook enabled di Coolify
- [x] Webhook added di GitHub
- [x] Test push & auto-deploy verified

---

## 🔧 Troubleshooting

### Problem 1: MongoDB Won't Start

**Symptoms:**
- Service status: Error atau Restarting

**Solutions:**
```bash
# Check logs
Coolify → Services → gelis-mongodb → Logs

# Common issues:
1. Port already in use → Change port
2. Insufficient memory → Increase RAM allocation
3. Wrong username/password → Recreate service
```

### Problem 2: Backend Build Failed

**Symptoms:**
- Deployment fails during build

**Solutions:**
```bash
# Check build logs
Coolify → Applications → gelis-backend → Logs → Build Logs

# Common issues:
1. Dockerfile syntax error → Fix Dockerfile
2. Missing requirements.txt → Add to repo
3. Python version mismatch → Use python:3.10
```

### Problem 3: Frontend Build Failed

**Symptoms:**
- yarn install or yarn build fails

**Solutions:**
```bash
# Check build logs

# Common issues:
1. Node version mismatch → Use node:20
2. Out of memory → Increase container memory
3. Missing nginx.conf → Add to repo
4. Lockfile mismatch → Commit yarn.lock
```

### Problem 4: Can't Connect Backend to MongoDB

**Symptoms:**
- Backend logs show MongoDB connection error

**Solutions:**
```bash
# Verify MONGO_URL in environment variables
# Should use service name: gelis-mongodb
# NOT localhost or 127.0.0.1

# Correct format:
mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
```

### Problem 5: Frontend Can't Reach Backend

**Symptoms:**
- CORS errors in browser console
- API calls fail

**Solutions:**
```bash
# 1. Check REACT_APP_BACKEND_URL in frontend env vars
# 2. Check CORS_ORIGINS in backend env vars
# 3. Rebuild frontend (env vars are embedded in build)
# 4. Verify backend domain/SSL working
```

### Problem 6: SSL Certificate Failed

**Symptoms:**
- SSL not generating atau expired

**Solutions:**
```bash
# 1. Wait for DNS propagation (up to 48h)
# 2. Check DNS pointing to correct IP:
nslookup yourdomain.com

# 3. Disable Cloudflare proxy temporarily
# 4. Check port 80/443 open in firewall
# 5. Regenerate certificate in Coolify
```

---

## 📊 Expected Timeline

| Step | Task | Time |
|------|------|------|
| 1 | Server Preparation | 10 min |
| 2 | Install Coolify | 5 min |
| 3 | Coolify Setup | 5 min |
| 4 | Prepare GitHub Repo | 3 min |
| 5 | Deploy MongoDB | 2 min |
| 6 | Deploy Backend | 5 min |
| 7 | Deploy Frontend | 10 min |
| 8 | Setup Domain & SSL | 5 min |
| 9 | Setup Auto-Deploy | 2 min |
| 10 | Verify & Test | 3 min |
| **Total** | **Complete Deployment** | **~50 min** |

**Note:** First-time deployment sedikit lebih lama karena:
- Docker image pulls
- Yarn install (Node modules)
- DNS propagation (if new domain)

---

## 🎉 Selesai!

Selamat! Aplikasi GELIS Anda sekarang sudah:

✅ **Running di production** dengan Coolify  
✅ **Auto-deploy** dari GitHub  
✅ **HTTPS/SSL** enabled  
✅ **Zero-downtime** deployment  
✅ **Easy rollback** dengan 1 klik  
✅ **Built-in monitoring**  
✅ **Auto-scaling** ready  

**Akses Aplikasi:**
- Frontend: https://gelis.yourdomain.com
- Backend API: https://api.gelis.yourdomain.com
- Coolify Dashboard: http://IP_SERVER:8000

**Next Steps:**
1. Ganti demo credentials (owner/owner123)
2. Clear mock data (Settings → Data)
3. Tambahkan real users
4. Input real orders & transactions
5. Setup backup schedule
6. Configure monitoring alerts

---

**Happy Deploying! 🚀**

Butuh bantuan? Cek:
- [INSTALASI_COOLIFY.md](INSTALASI_COOLIFY.md) - Dokumentasi lengkap
- [Coolify Docs](https://coolify.io/docs)
- [GELIS README.md](README.md)

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
