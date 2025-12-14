# 🚀 GELIS - Panduan Deployment ke Server Ubuntu

> **Panduan Lengkap Instalasi & Deployment GELIS (Gerbang Elektronik Layanan Informasi Sistem)**  
> Stack: FastAPI (Python) + React + MongoDB

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Pre-Installation Checklist](#pre-installation-checklist)
3. [Step 1: Server Preparation](#step-1-server-preparation)
4. [Step 2: Install Dependencies](#step-2-install-dependencies)
5. [Step 3: Setup MongoDB](#step-3-setup-mongodb)
6. [Step 4: Upload Application Code](#step-4-upload-application-code)
7. [Step 5: Backend Setup](#step-5-backend-setup)
8. [Step 6: Frontend Setup](#step-6-frontend-setup)
9. [Step 7: Setup Process Manager](#step-7-setup-process-manager)
10. [Step 8: Setup Nginx Reverse Proxy](#step-8-setup-nginx-reverse-proxy)
11. [Step 9: Setup SSL Certificate](#step-9-setup-ssl-certificate)
12. [Step 10: Firewall Configuration](#step-10-firewall-configuration)
13. [Step 11: Testing & Verification](#step-11-testing--verification)
14. [Maintenance & Troubleshooting](#maintenance--troubleshooting)

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
- [ ] Backup data (jika ada instalasi sebelumnya)

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

## Step 4: Upload Application Code

### 4.1. Option A: Clone from Git (Recommended)

```bash
# Navigate to application directory
cd /home/gelis

# Clone repository
git clone https://github.com/YOUR_USERNAME/gelis-app.git app

# Or if using private repository
git clone https://<token>@github.com/YOUR_USERNAME/gelis-app.git app

cd app
```

### 4.2. Option B: Upload via SCP

```bash
# From local machine, compress code
tar -czf gelis-app.tar.gz /path/to/app

# Upload to server
scp gelis-app.tar.gz username@your-server-ip:/home/gelis/

# On server, extract
cd /home/gelis
tar -xzf gelis-app.tar.gz
mv app-folder app
cd app
```

### 4.3. Set Proper Permissions

```bash
# Set ownership
sudo chown -R gelis:gelis /home/gelis/app

# Set directory permissions
sudo chmod -R 755 /home/gelis/app
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

### Update Application

```bash
# Pull latest code
cd /home/gelis/app
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend
cd ../frontend
yarn install
yarn build

# Restart services
sudo supervisorctl restart all
```

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
