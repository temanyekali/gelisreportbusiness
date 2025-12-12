# 🚀 Tutorial Instalasi GELIS dengan Coolify

Panduan lengkap deploy aplikasi GELIS ke server menggunakan Coolify (Self-hosted PaaS).

---

## 📋 Daftar Isi

1. [Tentang Coolify](#1-tentang-coolify)
2. [Persiapan Server](#2-persiapan-server)
3. [Instalasi Coolify](#3-instalasi-coolify)
4. [Persiapan Repository GitHub](#4-persiapan-repository-github)
5. [Setup MongoDB di Coolify](#5-setup-mongodb-di-coolify)
6. [Deploy Backend (FastAPI)](#6-deploy-backend-fastapi)
7. [Deploy Frontend (React)](#7-deploy-frontend-react)
8. [Konfigurasi Domain & SSL](#8-konfigurasi-domain--ssl)
9. [Environment Variables](#9-environment-variables)
10. [Monitoring & Logs](#10-monitoring--logs)
11. [Update & Rollback](#11-update--rollback)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Tentang Coolify

**Coolify** adalah self-hosted PaaS (Platform as a Service) open-source yang mirip dengan Heroku, Netlify, atau Vercel, namun berjalan di server Anda sendiri.

### Keuntungan Menggunakan Coolify:

✅ **Open Source & Free** - Tidak ada biaya lisensi  
✅ **Self-hosted** - Full kontrol atas data dan infrastructure  
✅ **Git Integration** - Auto-deploy dari GitHub/GitLab/Bitbucket  
✅ **Built-in SSL** - Otomatis generate Let's Encrypt certificate  
✅ **Multiple Services** - Deploy database, backend, frontend dalam satu dashboard  
✅ **Easy Rollback** - Rollback ke versi sebelumnya dengan 1 klik  
✅ **Built-in Monitoring** - Logs, metrics, dan health checks  
✅ **Zero Downtime Deploy** - Blue-green deployment  

### Spesifikasi Minimum Server:

```
- OS: Ubuntu 20.04/22.04 LTS (Recommended)
- RAM: 2 GB (Recommended: 4 GB+)
- CPU: 2 Core (Recommended: 4 Core+)
- Storage: 20 GB (Recommended: 50 GB+)
- IP Public dengan SSH access
```

---

## 2. Persiapan Server

### 2.1 Koneksi ke Server

```bash
# SSH ke server
ssh root@IP_SERVER_ANDA

# Atau dengan user non-root
ssh username@IP_SERVER_ANDA
```

### 2.2 Update Sistem

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y curl wget git
```

### 2.3 Setup Firewall

```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH (PENTING!)
sudo ufw allow 22/tcp

# Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Coolify ports
sudo ufw allow 8000/tcp  # Coolify dashboard
sudo ufw allow 6001/tcp  # Coolify realtime
sudo ufw allow 6002/tcp  # Coolify proxy

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 3. Instalasi Coolify

### 3.1 Install Docker (Prerequisite)

Coolify memerlukan Docker. Jika belum terinstall:

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add user ke docker group (agar tidak perlu sudo)
sudo usermod -aG docker $USER

# Logout dan login kembali atau jalankan:
newgrp docker

# Verify Docker
docker --version
docker ps
```

### 3.2 Install Coolify

```bash
# Download dan jalankan installer Coolify
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# Installer akan:
# - Install Docker (jika belum ada)
# - Install Docker Compose
# - Setup Coolify services
# - Generate initial admin password
```

**⏱️ Proses instalasi memakan waktu 5-10 menit.**

### 3.3 Akses Coolify Dashboard

Setelah instalasi selesai:

```bash
# Coolify akan berjalan di:
http://IP_SERVER_ANDA:8000

# Default credentials:
# Email: admin@example.com (ganti saat first setup)
# Password: [ditampilkan di output installer]
```

**🔐 PENTING:**
1. **Ganti password default** segera setelah login pertama
2. **Setup Email** untuk notifikasi
3. **Enable 2FA** (Two-Factor Authentication) untuk keamanan

### 3.4 Initial Setup Coolify

1. **Buka browser** → `http://IP_SERVER_ANDA:8000`
2. **Login** dengan credentials yang ditampilkan saat instalasi
3. **Change Password** → Settings → Security
4. **Setup Email** → Settings → Email Notifications (optional)
5. **Add SSH Key** → Settings → SSH Keys (untuk private repos)

---

## 4. Persiapan Repository GitHub

### 4.1 Push Kode ke GitHub

Jika belum push kode ke GitHub:

```bash
# Di local machine atau server development
cd /path/to/gelis

# Initialize git (jika belum)
git init

# Add remote repository
git remote add origin https://github.com/USERNAME/gelis-app.git

# Add all files
git add .

# Commit
git commit -m "Initial commit - GELIS v1.0"

# Push to GitHub
git push -u origin main
```

### 4.2 Buat File-file Penting

Pastikan repository memiliki file-file berikut:

#### **📄 `.gitignore` (Root)**

```gitignore
# Dependencies
node_modules/
backend/venv/
backend/__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Environment
.env
.env.local
.env.production
*.env

# Build
frontend/build/
backend/uploads/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Testing
coverage/
.coverage
htmlcov/
```

#### **📄 `Dockerfile` untuk Backend**

Buat file `/backend/Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
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

#### **📄 `Dockerfile` untuk Frontend**

Buat file `/frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build production bundle
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy build files to nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### **📄 `nginx.conf` untuk Frontend**

Buat file `/frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
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

#### **📄 `docker-compose.yml` (Optional - untuk local testing)**

Buat file `/docker-compose.yml`:

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: gelis-mongodb
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: gelis_db
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
    restart: unless-stopped

  backend:
    build: ./backend
    container_name: gelis-backend
    environment:
      MONGO_URL: ${MONGO_URL}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: gelis-frontend
    environment:
      REACT_APP_BACKEND_URL: ${REACT_APP_BACKEND_URL}
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  mongodb_data:
```

### 4.3 Push Perubahan ke GitHub

```bash
git add .
git commit -m "Add Docker configuration for Coolify deployment"
git push origin main
```

---

## 5. Setup MongoDB di Coolify

### 5.1 Add Database Service

1. **Login ke Coolify Dashboard**
2. **Klik "Services"** di sidebar
3. **Klik "Add Service"** atau **"+ New Service"**
4. **Pilih "MongoDB"**
5. **Konfigurasi:**

```
Name: gelis-mongodb
Version: 7.0
Database Name: gelis_db
Username: gelis_user
Password: [Generate Strong Password]
Root Password: [Generate Strong Password]
```

6. **Klik "Create"**
7. **Tunggu** hingga status menjadi **"Running"** (~ 2-3 menit)

### 5.2 Catat Connection String

Setelah MongoDB running, catat **Connection String**:

```
mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
```

**📝 IMPORTANT:**
- Hostname menggunakan service name: `gelis-mongodb`
- Ini adalah internal Docker network, tidak perlu expose ke public

---

## 6. Deploy Backend (FastAPI)

### 6.1 Create Application

1. **Klik "Applications"** di sidebar Coolify
2. **Klik "+ New Application"**
3. **Pilih "Public Repository"** atau **"Private Repository"**

### 6.2 Connect GitHub Repository

**Untuk Public Repository:**
```
Repository URL: https://github.com/USERNAME/gelis-app.git
Branch: main
```

**Untuk Private Repository:**
1. **Generate SSH Key** di Coolify (Settings → SSH Keys)
2. **Add SSH Key** ke GitHub (Settings → Deploy Keys)
3. Gunakan SSH URL: `git@github.com:USERNAME/gelis-app.git`

### 6.3 Configure Backend Application

```
Application Name: gelis-backend
Base Directory: /backend
Port: 8001
Build Pack: Dockerfile
Dockerfile Path: ./Dockerfile

Health Check:
- Enabled: Yes
- Path: /
- Interval: 30s
```

### 6.4 Environment Variables

Klik **"Environment Variables"** dan tambahkan:

```env
# MongoDB Connection
MONGO_URL=mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db

# JWT Configuration
SECRET_KEY=[Generate 64 char random string]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Application
APP_NAME=GELIS
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/uploads
```

**Generate SECRET_KEY:**

```bash
# Di local terminal
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 6.5 Deploy Backend

1. **Klik "Deploy"**
2. **Coolify akan:**
   - Clone repository
   - Build Docker image
   - Start container
   - Health check
3. **Tunggu hingga status "Running"** (~5-10 menit first deploy)

### 6.6 Verify Backend

```bash
# Test health endpoint
curl https://gelis-backend.yourdomain.com/

# Test API
curl https://gelis-backend.yourdomain.com/api/health
```

---

## 7. Deploy Frontend (React)

### 7.1 Create Frontend Application

1. **Klik "Applications" → "+ New Application"**
2. **Connect** repository yang sama (GitHub)

### 7.2 Configure Frontend

```
Application Name: gelis-frontend
Base Directory: /frontend
Port: 80
Build Pack: Dockerfile
Dockerfile Path: ./Dockerfile

Health Check:
- Enabled: Yes
- Path: /
- Interval: 30s
```

### 7.3 Environment Variables (Frontend)

```env
REACT_APP_BACKEND_URL=https://gelis-backend.yourdomain.com
REACT_APP_NAME=GELIS
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
```

**⚠️ IMPORTANT:**
- Frontend environment variables harus diawali dengan `REACT_APP_`
- Nilai akan di-embed ke build (tidak rahasia!)

### 7.4 Deploy Frontend

1. **Klik "Deploy"**
2. **Tunggu build process** (~10-15 menit first deploy karena yarn install)
3. **Verify status "Running"**

---

## 8. Konfigurasi Domain & SSL

### 8.1 Setup DNS Records

Di control panel domain Anda (Cloudflare, Namecheap, etc):

```
# Backend
A Record: api.yourdomain.com → IP_SERVER
atau
CNAME: api.yourdomain.com → gelis-backend.[coolify-domain]

# Frontend
A Record: yourdomain.com → IP_SERVER
A Record: www.yourdomain.com → IP_SERVER
```

### 8.2 Configure Domain di Coolify

**Backend:**
1. Masuk ke **gelis-backend** application
2. **Klik "Domains"**
3. **Add Domain:** `api.yourdomain.com`
4. **Enable SSL:** Toggle "SSL/TLS"
5. **Save**

**Frontend:**
1. Masuk ke **gelis-frontend** application
2. **Klik "Domains"**
3. **Add Domain:** `yourdomain.com` dan `www.yourdomain.com`
4. **Enable SSL:** Toggle "SSL/TLS"
5. **Save**

### 8.3 SSL Certificate

Coolify otomatis generate SSL certificate dengan Let's Encrypt:

✅ **Auto-renewal** setiap 90 hari  
✅ **Zero-downtime** certificate update  
✅ **A+ SSL Labs** rating  

**Verifikasi SSL:**

```bash
# Check certificate
curl -vI https://yourdomain.com

# Test SSL Labs
https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

---

## 9. Environment Variables

### 9.1 Update Environment Variables

Jika perlu update environment variables:

1. **Masuk ke Application** (backend/frontend)
2. **Klik "Environment Variables"**
3. **Edit atau Add** variables
4. **Save**
5. **Restart Application** (Coolify akan auto-restart)

### 9.2 Secrets Management

Untuk sensitive data (API keys, passwords):

1. **Gunakan Coolify Secrets**
2. **Jangan commit ke Git!**
3. **Reference di Environment Variables:** `${SECRET_NAME}`

---

## 10. Monitoring & Logs

### 10.1 Application Logs

**Real-time Logs:**
1. Masuk ke **Application**
2. Klik **"Logs"** tab
3. **Filter by:**
   - Build logs
   - Runtime logs
   - Error logs

**Download Logs:**
```bash
# Via Coolify UI
Application → Logs → Download
```

### 10.2 Resource Monitoring

**Dashboard menampilkan:**
- CPU usage
- Memory usage
- Disk usage
- Network traffic
- Request count

**Alerts:**
- Setup di **Settings → Notifications**
- Email/Slack/Discord alerts
- Threshold: CPU > 80%, Memory > 90%, etc.

### 10.3 Health Checks

Coolify automatically perform health checks:

```
Interval: 30s
Timeout: 10s
Retries: 3

If fails → Auto-restart container
```

---

## 11. Update & Rollback

### 11.1 Auto-Deploy dari GitHub

**Setup Webhook (Recommended):**

1. **Di Coolify Application:**
   - Klik "Settings"
   - Enable "Auto Deploy on Git Push"
   - Copy **Webhook URL**

2. **Di GitHub Repository:**
   - Settings → Webhooks → Add webhook
   - Payload URL: [Paste Webhook URL]
   - Content type: `application/json`
   - Events: `push` dan `pull_request`
   - Save

**Sekarang setiap `git push` akan auto-deploy!**

### 11.2 Manual Deploy

```
1. Masuk ke Application
2. Klik "Deploy" button
3. Coolify akan:
   - Pull latest code
   - Build new image
   - Blue-green deployment (zero downtime)
   - Health check
   - Switch traffic
```

### 11.3 Rollback

Jika deploy error atau bug:

```
1. Masuk ke Application
2. Klik "Deployments" tab
3. Pilih deployment sebelumnya
4. Klik "Rollback"
5. Confirm
```

**⚡ Rollback takes < 1 minute!**

---

## 12. Troubleshooting

### 12.1 Build Failed

**Problem:** Docker build error

```bash
# Check build logs
Coolify → Application → Logs → Build Logs

# Common issues:
1. Dockerfile syntax error
2. Missing dependencies in requirements.txt
3. File path incorrect

# Fix:
1. Update Dockerfile
2. Push to GitHub
3. Redeploy
```

### 12.2 Application Won't Start

**Problem:** Container crashes immediately

```bash
# Check runtime logs
Coolify → Application → Logs → Runtime Logs

# Common issues:
1. Environment variable missing
2. Database connection failed
3. Port already in use

# Fix:
1. Check Environment Variables
2. Verify MongoDB running
3. Check port configuration
```

### 12.3 SSL Certificate Failed

**Problem:** SSL not generating

```bash
# Check:
1. DNS pointing to correct IP
2. Port 80/443 open in firewall
3. Domain accessible

# Fix:
1. Wait for DNS propagation (up to 48h)
2. Disable Cloudflare proxy temporarily
3. Check firewall: sudo ufw status
```

### 12.4 Cannot Connect to MongoDB

**Problem:** Backend can't connect to database

```bash
# Check MongoDB status
Coolify → Services → gelis-mongodb → Status

# Verify:
1. MongoDB is running
2. Username/password correct in MONGO_URL
3. Database name correct
4. Service name correct (gelis-mongodb)

# Fix:
1. Restart MongoDB service
2. Check environment variables
3. Test connection from backend container:
   mongosh -u gelis_user -p PASSWORD gelis-mongodb:27017/gelis_db
```

### 12.5 Frontend Shows "API Not Found"

**Problem:** Frontend can't reach backend

```bash
# Check:
1. Backend is running
2. REACT_APP_BACKEND_URL correct
3. CORS configured in backend

# Fix:
1. Verify backend URL in frontend env vars
2. Update ALLOWED_ORIGINS in backend
3. Rebuild frontend (env vars embedded in build)
```

### 12.6 High Memory Usage

**Problem:** Container using too much RAM

```bash
# Check resource limits
Coolify → Application → Settings → Resources

# Set limits:
Memory Limit: 512MB (backend), 256MB (frontend)
CPU Limit: 1 core

# Restart application
```

---

## 🎯 Best Practices

### 1. Security

✅ **Change default passwords** immediately  
✅ **Use strong passwords** (generated)  
✅ **Enable 2FA** on Coolify  
✅ **Keep secrets out of Git**  
✅ **Regular backups**  
✅ **Update Coolify** regularly  

### 2. Performance

✅ **Use production builds** (not dev mode)  
✅ **Enable gzip compression**  
✅ **Setup CDN** for static assets  
✅ **Database indexes** for queries  
✅ **Monitor resource usage**  

### 3. Deployment

✅ **Use webhooks** for auto-deploy  
✅ **Test in staging** before production  
✅ **Health checks** configured  
✅ **Blue-green deployment** enabled  
✅ **Rollback plan** ready  

### 4. Monitoring

✅ **Setup alerts** for downtime  
✅ **Monitor logs** regularly  
✅ **Track error rates**  
✅ **Resource usage** dashboards  
✅ **Backup schedule** automated  

---

## 📚 Resources

### Official Documentation
- **Coolify Docs:** https://coolify.io/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev
- **MongoDB Docs:** https://docs.mongodb.com

### Community
- **Coolify Discord:** https://coollabs.io/discord
- **Coolify GitHub:** https://github.com/coollabsio/coolify

### Video Tutorials
- Coolify Quick Start: https://www.youtube.com/watch?v=...
- Deploy with GitHub: https://www.youtube.com/watch?v=...

---

## ✅ Post-Deployment Checklist

- [ ] MongoDB running dan accessible
- [ ] Backend deployed dan health check passed
- [ ] Frontend deployed dan accessible
- [ ] Domain DNS configured
- [ ] SSL certificates generated
- [ ] Environment variables configured
- [ ] Auto-deploy webhook setup
- [ ] Monitoring alerts configured
- [ ] Backup strategy implemented
- [ ] Test all user roles login
- [ ] Test CRUD operations
- [ ] Test mobile responsive
- [ ] Performance testing
- [ ] Security audit

---

## 🎉 Selesai!

Aplikasi GELIS Anda sekarang sudah deploy di Coolify dengan:

✅ Auto-deploy dari GitHub  
✅ Zero-downtime updates  
✅ SSL/HTTPS otomatis  
✅ Built-in monitoring  
✅ Easy rollback  
✅ Scalable infrastructure  

**Akses Aplikasi:**
- Frontend: https://yourdomain.com
- Backend API: https://api.yourdomain.com
- Coolify Dashboard: http://IP_SERVER:8000

**Selamat! Aplikasi Anda production-ready! 🚀**

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
