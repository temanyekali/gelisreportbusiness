# 📚 Tutorial Instalasi GELIS ke Server Pribadi

Panduan lengkap instalasi aplikasi GELIS (Gerbang Elektronik Layanan Informasi Sistem) ke server pribadi (VPS/Dedicated Server).

---

## 📋 Daftar Isi

1. [Persiapan Server](#1-persiapan-server)
2. [Instalasi Dependencies](#2-instalasi-dependencies)
3. [Setup MongoDB](#3-setup-mongodb)
4. [Setup Aplikasi](#4-setup-aplikasi)
5. [Konfigurasi Nginx](#5-konfigurasi-nginx)
6. [SSL Certificate](#6-ssl-certificate)
7. [Process Management dengan PM2](#7-process-management-dengan-pm2)
8. [Backup & Maintenance](#8-backup--maintenance)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Persiapan Server

### 1.1 Spesifikasi Minimum Server

```
- OS: Ubuntu 20.04 LTS atau lebih baru
- RAM: 2 GB (Recommended: 4 GB)
- Storage: 20 GB (Recommended: 40 GB)
- CPU: 2 Core (Recommended: 4 Core)
- Bandwidth: Unlimited atau minimum 1 TB/bulan
```

### 1.2 Domain & DNS

1. **Beli Domain** (contoh: gelis.com)
2. **Setup DNS Record** di control panel domain Anda:
   ```
   A Record: @ -> IP_SERVER_ANDA
   A Record: www -> IP_SERVER_ANDA
   ```
3. **Tunggu DNS Propagation** (15 menit - 48 jam)

### 1.3 Koneksi ke Server

```bash
# Koneksi via SSH
ssh root@IP_SERVER_ANDA

# Atau jika menggunakan user non-root
ssh username@IP_SERVER_ANDA
```

### 1.4 Update Sistem

```bash
# Update package list
sudo apt update

# Upgrade semua package
sudo apt upgrade -y

# Install tools essensial
sudo apt install -y curl wget git build-essential
```

---

## 2. Instalasi Dependencies

### 2.1 Install Node.js 20.x

```bash
# Install Node.js 20.x dari NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verifikasi instalasi
node --version  # Harus menampilkan v20.x.x
npm --version   # Harus menampilkan 10.x.x

# Install Yarn
sudo npm install -g yarn
yarn --version  # Harus menampilkan 1.22.x atau lebih
```

### 2.2 Install Python 3.10+

```bash
# Install Python 3.10 (jika belum ada)
sudo apt install -y python3.10 python3.10-venv python3-pip

# Verifikasi instalasi
python3 --version  # Harus menampilkan Python 3.10.x atau lebih

# Install pip untuk Python 3
sudo apt install -y python3-pip

# Upgrade pip
pip3 install --upgrade pip
```

### 2.3 Install MongoDB 7.0

```bash
# Import MongoDB public key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

# Tambahkan MongoDB repository
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt update

# Install MongoDB
sudo apt install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verifikasi status
sudo systemctl status mongod

# Verifikasi MongoDB berjalan
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

### 2.4 Install Nginx

```bash
# Install Nginx
sudo apt install -y nginx

# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verifikasi status
sudo systemctl status nginx

# Cek apakah Nginx sudah berjalan
curl http://localhost
# Harus menampilkan "Welcome to nginx!"
```

---

## 3. Setup MongoDB

### 3.1 Konfigurasi MongoDB untuk Keamanan

```bash
# Masuk ke MongoDB shell
mongosh

# Buat user admin
use admin
db.createUser({
  user: "admin",
  pwd: "PASSWORD_ADMIN_YANG_KUAT",
  roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
})

# Buat database dan user untuk GELIS
use gelis_db
db.createUser({
  user: "gelis_user",
  pwd: "PASSWORD_GELIS_YANG_KUAT",
  roles: [ { role: "readWrite", db: "gelis_db" } ]
})

# Keluar dari MongoDB shell
exit
```

### 3.2 Enable Authentication MongoDB

```bash
# Edit konfigurasi MongoDB
sudo nano /etc/mongod.conf

# Tambahkan atau ubah section security:
security:
  authorization: enabled

# Restart MongoDB
sudo systemctl restart mongod

# Test koneksi dengan authentication
mongosh -u admin -p PASSWORD_ADMIN_YANG_KUAT --authenticationDatabase admin
```

### 3.3 Setup Firewall (UFW)

```bash
# Install UFW jika belum ada
sudo apt install -y ufw

# Allow SSH (PENTING!)
sudo ufw allow 22/tcp

# Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# MongoDB hanya listen localhost (tidak perlu allow dari luar)
# Jangan expose port 27017 ke internet!

# Enable firewall
sudo ufw enable

# Cek status
sudo ufw status
```

---

## 4. Setup Aplikasi

### 4.1 Clone Repository

```bash
# Pindah ke direktori aplikasi
cd /opt

# Clone repository (ganti dengan URL repo Anda)
sudo git clone https://github.com/USERNAME/gelis-app.git gelis

# Set permissions
sudo chown -R $USER:$USER /opt/gelis
cd /opt/gelis
```

### 4.2 Setup Backend

```bash
cd /opt/gelis/backend

# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Buat file .env
nano .env
```

**Isi file `/opt/gelis/backend/.env`:**

```env
# MongoDB Configuration
MONGO_URL=mongodb://gelis_user:PASSWORD_GELIS_YANG_KUAT@localhost:27017/gelis_db?authSource=gelis_db

# JWT Configuration
SECRET_KEY=GENERATE_RANDOM_SECRET_KEY_DISINI_MINIMAL_64_KARAKTER
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Application Configuration
APP_NAME=GELIS
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False

# CORS Configuration (ganti dengan domain Anda)
ALLOWED_ORIGINS=https://gelis.com,https://www.gelis.com

# Upload Configuration
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/opt/gelis/backend/uploads
```

**Generate SECRET_KEY:**

```bash
# Jalankan di terminal
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Buat direktori uploads:**

```bash
mkdir -p /opt/gelis/backend/uploads
chmod 755 /opt/gelis/backend/uploads
```

### 4.3 Setup Frontend

```bash
cd /opt/gelis/frontend

# Install dependencies
yarn install

# Buat file .env
nano .env
```

**Isi file `/opt/gelis/frontend/.env`:**

```env
# Backend API URL (ganti dengan domain Anda)
REACT_APP_BACKEND_URL=https://gelis.com

# App Configuration
REACT_APP_NAME=GELIS
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production

# Optional: Google Analytics, Sentry, etc.
# REACT_APP_GA_ID=UA-XXXXXXXXX-X
```

**Build production:**

```bash
# Build aplikasi untuk production
yarn build

# Verifikasi build sukses
ls -lh build/
# Harus ada folder build/ dengan file index.html
```

### 4.4 Seed Data Awal (Optional)

```bash
cd /opt/gelis

# Aktifkan virtual environment backend
source backend/venv/bin/activate

# Jalankan script seed data
python scripts/seed_realistic_data.py

# Deaktivkan virtual environment
deactivate
```

---

## 5. Konfigurasi Nginx

### 5.1 Buat Konfigurasi Nginx untuk GELIS

```bash
# Buat file konfigurasi
sudo nano /etc/nginx/sites-available/gelis
```

**Isi file `/etc/nginx/sites-available/gelis`:**

```nginx
# Backend API Server
upstream backend_server {
    server 127.0.0.1:8001;
    keepalive 64;
}

# Main Server Block
server {
    listen 80;
    listen [::]:80;
    
    server_name gelis.com www.gelis.com;
    
    # Redirect to HTTPS (akan dikonfigurasi setelah SSL setup)
    # return 301 https://$server_name$request_uri;
    
    # Logging
    access_log /var/log/nginx/gelis_access.log;
    error_log /var/log/nginx/gelis_error.log;
    
    # Client body size limit (untuk upload file)
    client_max_body_size 10M;
    
    # Frontend Static Files
    root /opt/gelis/frontend/build;
    index index.html;
    
    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Backend API Proxy
    location /api {
        rewrite ^/api/(.*) /$1 break;
        
        proxy_pass http://backend_server;
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
    
    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Frontend React Router (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

### 5.2 Aktifkan Konfigurasi

```bash
# Buat symbolic link ke sites-enabled
sudo ln -s /etc/nginx/sites-available/gelis /etc/nginx/sites-enabled/

# Hapus default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test konfigurasi Nginx
sudo nginx -t

# Jika OK, reload Nginx
sudo systemctl reload nginx
```

---

## 6. SSL Certificate

### 6.1 Install Certbot

```bash
# Install Certbot untuk Nginx
sudo apt install -y certbot python3-certbot-nginx
```

### 6.2 Generate SSL Certificate

```bash
# Generate certificate (ganti email dan domain)
sudo certbot --nginx -d gelis.com -d www.gelis.com --email admin@gelis.com --agree-tos --no-eff-email

# Certbot akan otomatis:
# 1. Generate SSL certificate
# 2. Update konfigurasi Nginx
# 3. Setup auto-renewal
```

### 6.3 Verifikasi SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Cek certificate info
sudo certbot certificates
```

### 6.4 Update Nginx Config untuk HTTPS

Certbot sudah otomatis update konfigurasi. Verifikasi dengan:

```bash
sudo nano /etc/nginx/sites-available/gelis

# Pastikan ada:
# - listen 443 ssl;
# - ssl_certificate path
# - ssl_certificate_key path
# - redirect HTTP ke HTTPS
```

### 6.5 Reload Nginx

```bash
sudo systemctl reload nginx

# Test akses HTTPS
curl -I https://gelis.com
# Harus return 200 OK
```

---

## 7. Process Management dengan PM2

### 7.1 Install PM2

```bash
# Install PM2 globally
sudo npm install -g pm2

# Verifikasi instalasi
pm2 --version
```

### 7.2 Setup PM2 untuk Backend

```bash
cd /opt/gelis/backend

# Buat file ecosystem PM2
nano ecosystem.config.js
```

**Isi file `ecosystem.config.js`:**

```javascript
module.exports = {
  apps: [{
    name: 'gelis-backend',
    script: 'venv/bin/uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8001',
    cwd: '/opt/gelis/backend',
    interpreter: 'none',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PYTHONUNBUFFERED: '1'
    },
    error_file: '/var/log/pm2/gelis-backend-error.log',
    out_file: '/var/log/pm2/gelis-backend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
};
```

### 7.3 Start Backend dengan PM2

```bash
# Buat direktori log
sudo mkdir -p /var/log/pm2
sudo chown -R $USER:$USER /var/log/pm2

# Start backend
cd /opt/gelis/backend
pm2 start ecosystem.config.js

# Cek status
pm2 status

# Lihat logs
pm2 logs gelis-backend

# Monitoring
pm2 monit
```

### 7.4 Setup PM2 Startup

```bash
# Generate startup script
pm2 startup

# Copy & jalankan command yang muncul (contoh):
# sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u username --hp /home/username

# Save PM2 process list
pm2 save

# Verifikasi auto-start
sudo systemctl status pm2-$USER
```

### 7.5 PM2 Commands Berguna

```bash
# Restart backend
pm2 restart gelis-backend

# Stop backend
pm2 stop gelis-backend

# Delete from PM2
pm2 delete gelis-backend

# Reload (zero-downtime)
pm2 reload gelis-backend

# Show process details
pm2 show gelis-backend

# Show logs realtime
pm2 logs gelis-backend --lines 100

# Clear logs
pm2 flush

# Update PM2
pm2 update
```

---

## 8. Backup & Maintenance

### 8.1 Setup Backup MongoDB

```bash
# Buat direktori backup
sudo mkdir -p /opt/backups/mongodb
sudo chown -R $USER:$USER /opt/backups

# Buat script backup
nano /opt/backups/backup_mongodb.sh
```

**Isi file `backup_mongodb.sh`:**

```bash
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/backups/mongodb"
MONGO_USER="gelis_user"
MONGO_PASS="PASSWORD_GELIS_YANG_KUAT"
MONGO_DB="gelis_db"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="gelis_backup_$DATE"

# Create backup
mongodump \
    --username=$MONGO_USER \
    --password=$MONGO_PASS \
    --authenticationDatabase=$MONGO_DB \
    --db=$MONGO_DB \
    --out=$BACKUP_DIR/$BACKUP_NAME

# Compress backup
cd $BACKUP_DIR
tar -czf $BACKUP_NAME.tar.gz $BACKUP_NAME
rm -rf $BACKUP_NAME

# Delete backups older than 7 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_NAME.tar.gz"
```

**Set permissions & test:**

```bash
chmod +x /opt/backups/backup_mongodb.sh
/opt/backups/backup_mongodb.sh
```

### 8.2 Setup Cron untuk Auto Backup

```bash
# Edit crontab
crontab -e

# Tambahkan baris berikut (backup setiap hari jam 2 pagi)
0 2 * * * /opt/backups/backup_mongodb.sh >> /var/log/mongodb_backup.log 2>&1
```

### 8.3 Restore MongoDB dari Backup

```bash
# Extract backup
cd /opt/backups/mongodb
tar -xzf gelis_backup_YYYYMMDD_HHMMSS.tar.gz

# Restore database
mongorestore \
    --username=gelis_user \
    --password=PASSWORD_GELIS_YANG_KUAT \
    --authenticationDatabase=gelis_db \
    --db=gelis_db \
    --drop \
    gelis_backup_YYYYMMDD_HHMMSS/gelis_db
```

### 8.4 Update Aplikasi

```bash
# Backup database dulu!
/opt/backups/backup_mongodb.sh

# Pull latest code
cd /opt/gelis
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
pm2 restart gelis-backend

# Update frontend
cd ../frontend
yarn install
yarn build
sudo systemctl reload nginx

# Verifikasi
pm2 status
curl -I https://gelis.com
```

### 8.5 Monitoring & Logs

```bash
# Backend logs
pm2 logs gelis-backend

# Nginx access logs
sudo tail -f /var/log/nginx/gelis_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/gelis_error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# System resources
htop

# Disk usage
df -h

# Check listening ports
sudo netstat -tulpn | grep LISTEN
```

---

## 9. Troubleshooting

### 9.1 Backend Tidak Bisa Start

**Problem:** PM2 menunjukkan status error

```bash
# Cek logs detail
pm2 logs gelis-backend

# Cek apakah port 8001 sudah digunakan
sudo netstat -tulpn | grep 8001

# Cek virtual environment
cd /opt/gelis/backend
source venv/bin/activate
python -c "import fastapi; print(fastapi.__version__)"

# Test run manual
uvicorn server:app --host 0.0.0.0 --port 8001
# Lihat error yang muncul
```

### 9.2 MongoDB Connection Error

**Problem:** Backend tidak bisa connect ke MongoDB

```bash
# Cek MongoDB status
sudo systemctl status mongod

# Test koneksi manual
mongosh -u gelis_user -p PASSWORD_GELIS_YANG_KUAT --authenticationDatabase gelis_db gelis_db

# Cek MONGO_URL di .env
cat /opt/gelis/backend/.env | grep MONGO_URL

# Restart MongoDB
sudo systemctl restart mongod
```

### 9.3 Nginx 502 Bad Gateway

**Problem:** Nginx tidak bisa connect ke backend

```bash
# Cek backend running
pm2 status

# Cek port backend
curl http://localhost:8001
# Harus return response JSON

# Cek Nginx config
sudo nginx -t

# Cek Nginx logs
sudo tail -f /var/log/nginx/gelis_error.log

# Restart semua
pm2 restart gelis-backend
sudo systemctl reload nginx
```

### 9.4 Frontend 404 Error

**Problem:** React router tidak bekerja

```bash
# Cek Nginx config, pastikan ada:
# try_files $uri $uri/ /index.html;

# Cek build folder exists
ls -lh /opt/gelis/frontend/build/

# Rebuild frontend
cd /opt/gelis/frontend
yarn build

# Reload Nginx
sudo systemctl reload nginx
```

### 9.5 SSL Certificate Error

**Problem:** HTTPS tidak bekerja atau expired

```bash
# Cek certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Force renew
sudo certbot renew --force-renewal

# Restart Nginx
sudo systemctl restart nginx
```

### 9.6 High Memory Usage

**Problem:** Server kehabisan memory

```bash
# Cek memory usage
free -h

# Cek process memory
ps aux --sort=-%mem | head -10

# Restart PM2 apps
pm2 restart all

# Add swap jika perlu
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 9.7 Slow Performance

**Problem:** Aplikasi lambat

```bash
# Cek CPU & memory
htop

# Cek disk I/O
iostat -x 1 5

# Cek MongoDB slow queries
mongosh
use gelis_db
db.currentOp({ "active": true, "secs_running": { "$gt": 1 } })

# Cek Nginx connections
sudo nginx -V 2>&1 | grep -o with-http_stub_status_module

# Clear PM2 logs
pm2 flush

# Optimize MongoDB
mongosh
use gelis_db
db.adminCommand({ "reIndex": "nama_collection" })
```

---

## 📞 Dukungan & Kontak

Jika Anda mengalami masalah atau butuh bantuan:

1. **Cek Logs:** Selalu mulai dengan memeriksa logs
2. **Google Error:** Search error message di Google
3. **Documentation:** Baca dokumentasi FastAPI, React, MongoDB
4. **Community:** Forum, Stack Overflow, Reddit

---

## 🎉 Selesai!

Aplikasi GELIS Anda sekarang sudah berjalan di server pribadi dengan:

✅ Backend FastAPI di PM2  
✅ Frontend React (production build)  
✅ MongoDB dengan authentication  
✅ Nginx reverse proxy  
✅ SSL/HTTPS certificate  
✅ Auto backup database  
✅ Auto restart on failure  

Selamat! Aplikasi Anda sudah production-ready! 🚀

---

## 📝 Checklist Post-Installation

- [ ] Test login dengan semua role (Owner, Manager, Loket, Kasir, Teknisi)
- [ ] Test create/edit/delete di semua module
- [ ] Test upload file (jika ada)
- [ ] Test mobile responsive
- [ ] Setup monitoring (optional: New Relic, Datadog, etc.)
- [ ] Setup error tracking (optional: Sentry)
- [ ] Setup uptime monitoring (optional: UptimeRobot)
- [ ] Backup manual pertama
- [ ] Test restore dari backup
- [ ] Dokumentasikan credential untuk tim
- [ ] Setup email alerts untuk downtime
- [ ] Configure firewall rules
- [ ] Security audit
- [ ] Performance testing

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
