# 🚀 GELIS - Panduan Deployment ke Server Ubuntu

> **Panduan Lengkap Instalasi & Deployment GELIS (Gerbang Elektronik Layanan Informasi Sistem)**  
> Stack: FastAPI (Python) + React + MongoDB

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [GitHub Repository Setup](#github-repository-setup)
4. [Step 1: Server Preparation](#step-1-server-preparation)
5. [Step 2: Install Dependencies](#step-2-install-dependencies)
6. [Step 3: Setup MongoDB](#step-3-setup-mongodb)
7. [Step 4: Clone dari GitHub](#step-4-clone-dari-github)
8. [Step 5: Backend Setup](#step-5-backend-setup)
9. [Step 6: Frontend Setup](#step-6-frontend-setup)
10. [Step 7: Setup Process Manager](#step-7-setup-process-manager)
11. [Step 8: Setup Nginx Reverse Proxy](#step-8-setup-nginx-reverse-proxy)
12. [Step 9: Setup SSL Certificate](#step-9-setup-ssl-certificate)
13. [Step 10: Firewall Configuration](#step-10-firewall-configuration)
14. [Step 11: Testing & Verification](#step-11-testing--verification)
15. [Maintenance & Troubleshooting](#maintenance--troubleshooting)
16. [Update dari GitHub](#update-dari-github)

---

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS atau lebih baru (22.04 LTS recommended)
- **RAM**: 2GB (4GB recommended untuk production)
- **Storage**: 20GB free space
- **CPU**: 2 vCPU (4 vCPU recommended)
- **Network**: Public IP address & domain name (optional tapi recommended)

### Software Requirements
- Python 3.11+
- Node.js 18+ & Yarn
- MongoDB 6.0+
- Nginx
- Supervisor atau PM2
- Git

---

## Pre-Installation Checklist

- [ ] Server Ubuntu dengan akses root/sudo
- [ ] Domain name sudah diarahkan ke IP server (optional)
- [ ] SSH key atau password untuk akses server
- [ ] GitHub account dan repository (untuk version control)
- [ ] GitHub Personal Access Token (untuk private repository)
- [ ] Backup data (jika ada instalasi sebelumnya)

---

## GitHub Repository Setup

### Mengapa Perlu GitHub Repository?

Menggunakan GitHub untuk deployment memiliki banyak keuntungan:
- ✅ **Version Control**: Track semua perubahan code
- ✅ **Collaboration**: Tim dapat bekerja sama dengan mudah
- ✅ **Backup**: Code tersimpan aman di cloud
- ✅ **Easy Updates**: Deploy update dengan `git pull`
- ✅ **Rollback**: Kembali ke versi sebelumnya jika ada masalah

### 1. Persiapan GitHub Repository

#### Opsi A: Repository Baru

1. **Login ke GitHub**: https://github.com
2. **Buat Repository Baru**:
   - Klik tombol **"New"** atau **"+"** → **"New repository"**
   - Repository name: `gelis-app` (atau nama lain sesuai keinginan)
   - Description: `GELIS - Gerbang Elektronik Layanan Informasi Sistem`
   - Pilih **Private** (recommended untuk production app)
   - **JANGAN** centang "Initialize with README" (karena kita akan push existing code)
   - Klik **"Create repository"**

3. **Copy URL Repository**:
   ```
   https://github.com/USERNAME/gelis-app.git
   ```

#### Opsi B: Fork dari Existing Repository

Jika Anda menggunakan Emergent platform dan ingin push ke GitHub:

1. Gunakan fitur **"Save to GitHub"** yang ada di Emergent UI
2. Atau manual push (lihat section berikutnya)

### 2. Setup GitHub Personal Access Token (PAT)

Untuk private repository, Anda perlu PAT:

1. **Buka GitHub Settings**:
   - Klik profile picture → **Settings**
   - Scroll ke bawah → **Developer settings**
   - Klik **Personal access tokens** → **Tokens (classic)**

2. **Generate Token**:
   - Klik **"Generate new token"** → **"Generate new token (classic)"**
   - Note: `GELIS Deployment`
   - Expiration: `No expiration` (atau sesuai kebutuhan)
   - Select scopes:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
   - Klik **"Generate token"**

3. **Simpan Token**:
   ```
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   ⚠️ **PENTING**: Simpan token ini, tidak akan ditampilkan lagi!

### 3. Push Code ke GitHub (Jika Belum Push)

Jika Anda belum push code ke GitHub:

```bash
# Masuk ke directory aplikasi
cd /path/to/gelis-app

# Initialize git (jika belum)
git init

# Buat .gitignore untuk exclude sensitive files
cat > .gitignore <<EOF
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
venv/
*.so

# Node
node_modules/
build/
dist/
.DS_Store

# Logs
*.log
logs/

# IDE
.vscode/
.idea/

# System
.emergent/
EOF

# Add semua file
git add .

# Commit pertama
git commit -m "Initial commit: GELIS application"

# Link ke GitHub repository
git remote add origin https://github.com/USERNAME/gelis-app.git

# Push ke GitHub
git push -u origin main
```

Jika diminta username & password:
- **Username**: GitHub username Anda
- **Password**: Paste **Personal Access Token** (bukan password GitHub!)

### 4. Verify Repository

Buka browser dan check: `https://github.com/USERNAME/gelis-app`

Pastikan semua file sudah ter-upload (kecuali file di `.gitignore`)

---

## Step 1: Server Preparation

### 1.1. Login ke Server

```bash
# Login via SSH
ssh username@your-server-ip

# Atau jika menggunakan SSH key
ssh -i /path/to/key.pem username@your-server-ip
```

### 1.2. Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential build tools
sudo apt install -y build-essential software-properties-common curl wget git
```

### 1.3. Create Application User (Optional tapi Recommended)

```bash
# Create dedicated user untuk aplikasi
sudo adduser gelis --disabled-password --gecos ""

# Add user to sudo group (optional)
sudo usermod -aG sudo gelis

# Switch to application user
sudo su - gelis
```

---

## Step 2: Install Dependencies

### 2.1. Install Python 3.11

```bash
# Add deadsnakes PPA untuk Python terbaru
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
sudo apt install -y python3-pip

# Verify installation
python3.11 --version  # Should show: Python 3.11.x
```

### 2.2. Install Node.js & Yarn

```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Yarn package manager
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install -y yarn

# Verify installations
node --version   # Should show: v18.x.x
yarn --version   # Should show: 1.22.x
```

### 2.3. Install Additional Dependencies

```bash
# Install Nginx web server
sudo apt install -y nginx

# Install Supervisor (process manager)
sudo apt install -y supervisor

# Install certbot untuk SSL (Let's Encrypt)
sudo apt install -y certbot python3-certbot-nginx
```

---

## Step 3: Setup MongoDB

### 3.1. Install MongoDB 6.0

```bash
# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod
```

### 3.2. Configure MongoDB

```bash
# Edit MongoDB configuration
sudo nano /etc/mongod.conf
```

Update configuration:
```yaml
# network interfaces
net:
  port: 27017
  bindIp: 127.0.0.1  # Only accept local connections (secure)

# security
security:
  authorization: enabled  # Enable authentication
```

### 3.3. Create MongoDB Admin User

```bash
# Connect to MongoDB shell
mongosh

# Switch to admin database
use admin

# Create admin user
db.createUser({
  user: "admin",
  pwd: "YOUR_STRONG_PASSWORD_HERE",  # Change this!
  roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
})

# Exit mongosh
exit
```

### 3.4. Create Database & Application User

```bash
# Connect as admin
mongosh -u admin -p --authenticationDatabase admin

# Create GELIS database
use gelis_db

# Create application user
db.createUser({
  user: "gelis_user",
  pwd: "YOUR_APP_DB_PASSWORD",  # Change this!
  roles: [ { role: "readWrite", db: "gelis_db" } ]
})

# Exit
exit

# Restart MongoDB
sudo systemctl restart mongod
```

---

## Step 4: Clone dari GitHub

### 4.1. Clone Repository (Public Repository)

Jika repository Anda **public**:

```bash
# Switch ke user aplikasi
sudo su - gelis

# Clone repository
cd /home/gelis
git clone https://github.com/USERNAME/gelis-app.git app

# Masuk ke directory
cd app

# Verify
ls -la
```

### 4.2. Clone Repository (Private Repository)

Jika repository Anda **private**, gunakan Personal Access Token:

#### Method 1: Clone dengan Token di URL

```bash
# Switch ke user aplikasi
sudo su - gelis

# Clone dengan token
cd /home/gelis
git clone https://YOUR_GITHUB_TOKEN@github.com/USERNAME/gelis-app.git app

# Contoh:
# git clone https://ghp_xxxxxxxxxxxxxxxxxxxx@github.com/johndoe/gelis-app.git app

cd app
```

#### Method 2: Setup Git Credentials

```bash
# Switch ke user aplikasi
sudo su - gelis

# Configure git credentials
git config --global credential.helper store

# Clone repository (akan diminta username & password)
cd /home/gelis
git clone https://github.com/USERNAME/gelis-app.git app

# Saat diminta:
# Username: your-github-username
# Password: your-personal-access-token (bukan password GitHub!)

cd app

# Verify git remote
git remote -v
```

Credentials akan tersimpan di `~/.git-credentials` untuk penggunaan selanjutnya.

### 4.3. Clone Branch Tertentu

Jika Anda ingin clone branch tertentu (misalnya `production`):

```bash
# Clone branch production
git clone -b production https://github.com/USERNAME/gelis-app.git app

# Atau clone main lalu switch
git clone https://github.com/USERNAME/gelis-app.git app
cd app
git checkout production
```

### 4.4. Verify Clone

```bash
cd /home/gelis/app

# Check struktur folder
ls -la

# Output seharusnya menampilkan:
# drwxr-xr-x  backend/
# drwxr-xr-x  frontend/
# drwxr-xr-x  scripts/
# -rw-r--r--  README.md
# -rw-r--r--  CREDENTIALS.md
# dll.

# Check git status
git status

# Check current branch
git branch
```

### 4.5. Set Proper Permissions

```bash
# Keluar dari user gelis (kembali ke root)
exit

# Set ownership
sudo chown -R gelis:gelis /home/gelis/app

# Set directory permissions
sudo chmod -R 755 /home/gelis/app

# Verify
ls -la /home/gelis/app
```

### 4.6. Setup GitHub SSH Key (Optional - Recommended untuk Production)

Untuk keamanan lebih baik, gunakan SSH key daripada token:

```bash
# Login sebagai user gelis
sudo su - gelis

# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Press Enter untuk default location
# Set passphrase (optional tapi recommended)

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Output akan seperti:
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx your_email@example.com
```

**Tambahkan SSH Key ke GitHub**:

1. Buka GitHub: https://github.com/settings/keys
2. Klik **"New SSH key"**
3. Title: `GELIS Production Server`
4. Key type: `Authentication Key`
5. Paste public key dari output di atas
6. Klik **"Add SSH key"**

**Clone menggunakan SSH**:

```bash
# Clone repository dengan SSH
cd /home/gelis
git clone git@github.com:USERNAME/gelis-app.git app

# Atau update existing remote ke SSH
cd /home/gelis/app
git remote set-url origin git@github.com:USERNAME/gelis-app.git

# Verify
git remote -v
```

---

## Step 5: Backend Setup

### 5.1. Create Python Virtual Environment

```bash
cd /home/gelis/app/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 5.2. Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

### 5.3. Configure Environment Variables

```bash
# Create .env file
nano /home/gelis/app/backend/.env
```

Add the following configuration:
```bash
# MongoDB Configuration
MONGO_URL=mongodb://gelis_user:YOUR_APP_DB_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db
DB_NAME=gelis_db

# JWT Secret (generate a strong random string)
JWT_SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE_MIN_32_CHARS

# Application Settings
ENVIRONMENT=production
DEBUG=False

# CORS Settings (your domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Optional: External API Keys (if needed)
# OPENAI_API_KEY=your_key_here
# STRIPE_API_KEY=your_key_here
```

**Generate JWT Secret Key:**
```bash
# Generate random 64-character hex string
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5.4. Initialize Database with Seed Data

```bash
# Activate virtual environment
source /home/gelis/app/backend/venv/bin/activate

# Run seed scripts to populate initial data
cd /home/gelis/app/backend

# Seed roles
python3 scripts/seed_realistic_data.py

# Create admin users
python3 scripts/verify_roles_and_test.py

# Verify data
python3 -c "
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    users = await db.users.count_documents({})
    businesses = await db.businesses.count_documents({})
    
    print(f'Users: {users}')
    print(f'Businesses: {businesses}')
    
    client.close()

asyncio.run(check())
"
```

### 5.5. Test Backend Locally

```bash
# Test if backend can start
cd /home/gelis/app/backend
source venv/bin/activate

# Run temporarily to test
uvicorn server:app --host 0.0.0.0 --port 8001

# Test from another terminal
curl http://localhost:8001/api/health

# Press Ctrl+C to stop
```

---

## Step 6: Frontend Setup

### 6.1. Install Node Dependencies

```bash
cd /home/gelis/app/frontend

# Install dependencies using Yarn
yarn install

# This may take 5-10 minutes
```

### 6.2. Configure Frontend Environment

```bash
# Create production .env file
nano /home/gelis/app/frontend/.env.production
```

Add configuration:
```bash
# Backend API URL (your production domain)
REACT_APP_BACKEND_URL=https://api.yourdomain.com

# Or if using same domain with /api prefix
REACT_APP_BACKEND_URL=https://yourdomain.com
```

### 6.3. Build Frontend for Production

```bash
cd /home/gelis/app/frontend

# Build optimized production bundle
yarn build

# This creates /home/gelis/app/frontend/build directory
# Build process may take 3-5 minutes

# Verify build
ls -lh build/
```

---

## Step 7: Setup Process Manager

### Option A: Using Supervisor (Recommended)

### 7.1. Create Backend Supervisor Config

```bash
sudo nano /etc/supervisor/conf.d/gelis-backend.conf
```

Add configuration:
```ini
[program:gelis-backend]
command=/home/gelis/app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
directory=/home/gelis/app/backend
user=gelis
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/gelis-backend.err.log
stdout_logfile=/var/log/supervisor/gelis-backend.out.log
environment=PYTHONUNBUFFERED=1
```

### 7.2. Create Frontend Supervisor Config (if serving with serve)

```bash
sudo nano /etc/supervisor/conf.d/gelis-frontend.conf
```

Add configuration:
```ini
[program:gelis-frontend]
command=/usr/bin/yarn serve -s build -l 3000
directory=/home/gelis/app/frontend
user=gelis
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/gelis-frontend.err.log
stdout_logfile=/var/log/supervisor/gelis-frontend.out.log
```

### 7.3. Start Services

```bash
# Reload Supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start services
sudo supervisorctl start gelis-backend
sudo supervisorctl start gelis-frontend

# Check status
sudo supervisorctl status

# Output should show:
# gelis-backend    RUNNING   pid 12345, uptime 0:00:10
# gelis-frontend   RUNNING   pid 12346, uptime 0:00:10
```

---

## Step 8: Setup Nginx Reverse Proxy

### 8.1. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/gelis
```

Add configuration:
```nginx
# HTTP Configuration (will redirect to HTTPS)
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS Configuration
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate paths (will be configured by Certbot)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend (React App)
    location / {
        root /home/gelis/app/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # File upload size limit
    client_max_body_size 50M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/rss+xml font/truetype font/opentype application/vnd.ms-fontobject image/svg+xml;

    # Logs
    access_log /var/log/nginx/gelis_access.log;
    error_log /var/log/nginx/gelis_error.log;
}
```

### 8.2. Enable Site & Test Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gelis /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

---

## Step 9: Setup SSL Certificate

### 9.1. Install SSL Certificate using Let's Encrypt

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose to redirect HTTP to HTTPS

# Start Nginx
sudo systemctl start nginx

# Test SSL
sudo certbot renew --dry-run
```

### 9.2. Setup Auto-Renewal

```bash
# Certbot automatically creates a cron job/systemd timer
# Verify auto-renewal is configured
sudo systemctl status certbot.timer

# Manual renewal command (if needed)
sudo certbot renew
```

---

## Step 10: Firewall Configuration

### 10.1. Setup UFW (Uncomplicated Firewall)

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (IMPORTANT! Do this first to avoid locking yourself out)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check firewall status
sudo ufw status verbose

# Output should show:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

### 10.2. Additional Security (Optional)

```bash
# Limit SSH connection attempts
sudo ufw limit 22/tcp

# Deny all other incoming by default
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Reload firewall
sudo ufw reload
```

---

## Step 11: Testing & Verification

### 11.1. Check All Services

```bash
# Check MongoDB
sudo systemctl status mongod

# Check Supervisor services
sudo supervisorctl status

# Check Nginx
sudo systemctl status nginx

# Check logs
sudo tail -f /var/log/supervisor/gelis-backend.err.log
sudo tail -f /var/log/nginx/gelis_error.log
```

### 11.2. Test Backend API

```bash
# Health check
curl https://yourdomain.com/api/health

# Login test
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"owner","password":"owner123"}'
```

### 11.3. Test Frontend

```bash
# Open browser and navigate to:
https://yourdomain.com

# Test login with credentials:
# Username: owner
# Password: owner123
```

### 11.4. Performance Test

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 100 -c 10 https://yourdomain.com/api/health

# Test frontend
ab -n 100 -c 10 https://yourdomain.com/
```

---

## Maintenance & Troubleshooting

### Common Commands

```bash
# Restart all services
sudo supervisorctl restart all
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/supervisor/gelis-backend.err.log
sudo tail -f /var/log/nginx/gelis_error.log

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python
ps aux | grep node
```

---

## Update dari GitHub

### 1. Update Code dari GitHub (Manual)

Cara tercepat untuk deploy update:

```bash
# Login ke server
ssh username@your-server-ip

# Switch ke user aplikasi
sudo su - gelis

# Navigate ke app directory
cd /home/gelis/app

# Stash perubahan local (jika ada)
git stash

# Pull latest changes
git pull origin main

# Atau pull dari branch tertentu
# git pull origin production

# Check apa yang berubah
git log -5 --oneline
```

### 2. Update Backend Dependencies (Jika Ada Perubahan)

Jika ada perubahan di `requirements.txt`:

```bash
cd /home/gelis/app/backend

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Atau install package spesifik
# pip install package-name==version

# Verify
pip list
```

### 3. Update Frontend & Rebuild (Jika Ada Perubahan Code)

Jika ada perubahan di frontend:

```bash
cd /home/gelis/app/frontend

# Install new dependencies (jika ada)
yarn install

# Rebuild production bundle
yarn build

# Verify build
ls -lh build/
```

### 4. Restart Services

```bash
# Keluar dari user gelis
exit

# Restart backend
sudo supervisorctl restart gelis-backend

# Jika perlu restart frontend (jika menggunakan serve)
# sudo supervisorctl restart gelis-frontend

# Reload Nginx (untuk frontend static files)
sudo systemctl reload nginx

# Check status
sudo supervisorctl status
```

### 5. Verify Update

```bash
# Test backend API
curl https://yourdomain.com/api/health

# Check backend version/logs
sudo tail -f /var/log/supervisor/gelis-backend.out.log

# Test frontend
# Buka browser: https://yourdomain.com
```

### 6. Rollback Jika Ada Masalah

Jika update menyebabkan error:

```bash
# Switch ke user aplikasi
sudo su - gelis
cd /home/gelis/app

# Check commit history
git log --oneline -10

# Rollback ke commit sebelumnya
git reset --hard COMMIT_HASH

# Contoh:
# git reset --hard abc1234

# Atau rollback 1 commit
git reset --hard HEAD~1

# Rebuild (jika perlu)
cd frontend
yarn build

# Keluar dan restart
exit
sudo supervisorctl restart all
```

### 7. Automated Deployment Script (Recommended)

Buat script untuk automate deployment:

```bash
# Create deployment script
sudo nano /home/gelis/deploy.sh
```

Isi script:

```bash
#!/bin/bash

set -e  # Exit on error

echo "🚀 Starting GELIS Deployment..."

APP_DIR="/home/gelis/app"
cd $APP_DIR

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git stash
git pull origin main

# Backend update
echo "🔧 Updating backend..."
cd $APP_DIR/backend
source venv/bin/activate
pip install -r requirements.txt -q

# Frontend update
echo "🎨 Rebuilding frontend..."
cd $APP_DIR/frontend
yarn install --silent
yarn build --silent

# Restart services
echo "♻️  Restarting services..."
sudo supervisorctl restart gelis-backend
sudo systemctl reload nginx

# Verify
echo "✅ Deployment complete!"
echo ""
echo "📊 Service status:"
sudo supervisorctl status gelis-backend

echo ""
echo "🌐 Application URL: https://yourdomain.com"
```

Set permissions:

```bash
# Make executable
sudo chmod +x /home/gelis/deploy.sh

# Run deployment
sudo /home/gelis/deploy.sh
```

### 8. Setup Webhook untuk Auto-Deploy (Advanced)

Untuk auto-deploy saat push ke GitHub:

#### 8.1. Install webhook listener

```bash
# Install webhook package
sudo npm install -g webhook

# Create webhook config
sudo mkdir -p /etc/webhook
sudo nano /etc/webhook/hooks.json
```

Config:

```json
[
  {
    "id": "gelis-deploy",
    "execute-command": "/home/gelis/deploy.sh",
    "command-working-directory": "/home/gelis/app",
    "pass-arguments-to-command": [],
    "trigger-rule": {
      "match": {
        "type": "payload-hash-sha256",
        "secret": "YOUR_WEBHOOK_SECRET_HERE",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature-256"
        }
      }
    }
  }
]
```

#### 8.2. Create systemd service

```bash
sudo nano /etc/systemd/system/webhook.service
```

```ini
[Unit]
Description=Webhook Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/webhook -hooks /etc/webhook/hooks.json -port 9000 -verbose
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start webhook
sudo systemctl enable webhook

# Allow webhook port
sudo ufw allow 9000/tcp
```

#### 8.3. Setup GitHub Webhook

1. Buka GitHub repository: `https://github.com/USERNAME/gelis-app`
2. Settings → Webhooks → Add webhook
3. Payload URL: `http://your-server-ip:9000/hooks/gelis-deploy`
4. Content type: `application/json`
5. Secret: `YOUR_WEBHOOK_SECRET_HERE` (sama dengan config)
6. Events: `Just the push event`
7. Active: ✅
8. Add webhook

Sekarang setiap kali Anda push ke GitHub, server akan auto-deploy! 🎉

### Backup Database

```bash
# Create backup directory
mkdir -p /home/gelis/backups

# Backup MongoDB
mongodump --uri="mongodb://gelis_user:YOUR_APP_DB_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  --out=/home/gelis/backups/gelis_backup_$(date +%Y%m%d_%H%M%S)

# Compress backup
tar -czf /home/gelis/backups/gelis_backup_$(date +%Y%m%d).tar.gz \
  /home/gelis/backups/gelis_backup_*

# Upload to cloud storage (optional)
# aws s3 cp backup.tar.gz s3://your-bucket/
```

### Restore Database

```bash
# Extract backup
tar -xzf backup.tar.gz

# Restore MongoDB
mongorestore --uri="mongodb://gelis_user:YOUR_APP_DB_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  /path/to/backup/directory
```

### Common Issues

**Issue 1: Port already in use**
```bash
# Find process using port 8001
sudo lsof -i :8001

# Kill process
sudo kill -9 <PID>
```

**Issue 2: Permission denied**
```bash
# Fix permissions
sudo chown -R gelis:gelis /home/gelis/app
sudo chmod -R 755 /home/gelis/app
```

**Issue 3: MongoDB connection failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Restart MongoDB
sudo systemctl restart mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log
```

**Issue 4: Nginx 502 Bad Gateway**
```bash
# Check backend is running
sudo supervisorctl status gelis-backend

# Restart backend
sudo supervisorctl restart gelis-backend

# Check Nginx error log
sudo tail -f /var/log/nginx/gelis_error.log
```

---

## Security Best Practices

1. **Change default passwords** - Update all default credentials
2. **Regular updates** - Keep system and packages updated
3. **Firewall** - Only allow necessary ports
4. **SSL/TLS** - Always use HTTPS
5. **Backups** - Automated daily backups
6. **Monitoring** - Setup monitoring (Prometheus/Grafana)
7. **Rate limiting** - Implement API rate limiting
8. **Environment variables** - Never commit secrets to Git

---

## Performance Optimization

### 1. Enable HTTP/2
Already configured in Nginx config above.

### 2. Setup Redis Cache (Optional)

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf

# Set: supervised systemd
# Set: maxmemory 256mb
# Set: maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis

# Enable on boot
sudo systemctl enable redis
```

### 3. Setup CDN (Optional)
Use Cloudflare or similar CDN service for static assets.

---

## Monitoring & Logging

### Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/gelis
```

Add:
```
/var/log/supervisor/gelis-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 gelis gelis
}

/var/log/nginx/gelis_*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

---

## 📞 Support & Resources

- **Documentation**: `/app/CREDENTIALS.md`, `/app/ROLE_PERMISSION_REFERENCE.md`
- **Issue Tracking**: Check application logs
- **MongoDB Docs**: https://docs.mongodb.com/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Nginx Docs**: https://nginx.org/en/docs/

---

## ✅ Deployment Checklist

- [ ] Server setup completed
- [ ] All dependencies installed
- [ ] MongoDB configured & secured
- [ ] Application code deployed
- [ ] Backend running (port 8001)
- [ ] Frontend built & deployed
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Services auto-start on reboot
- [ ] Backups configured
- [ ] Monitoring setup (optional)
- [ ] All tests passed
- [ ] Documentation updated
- [ ] Team trained on maintenance

---

**Deployment Complete! 🎉**

Your GELIS application is now live at: **https://yourdomain.com**

Test with default credentials:
- **Owner**: owner / owner123
- **IT Developer**: it / it123

---

*Last Updated: 2025-12-14*  
*Version: 1.0*  
*Stack: FastAPI + React + MongoDB*
