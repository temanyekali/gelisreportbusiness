# 📖 GELIS - Quick Reference Guide

> Cheat sheet untuk command-command penting dalam maintenance GELIS

---

## 🚀 Quick Start

### One-Line Installation
```bash
# Download dan jalankan installation script
curl -fsSL https://your-server.com/install.sh | sudo bash
```

### Manual Installation
```bash
# Clone repository
git clone https://github.com/your-repo/gelis.git
cd gelis

# Run installation script
sudo bash install.sh
```

---

## 🔧 Service Management

### Supervisor (Backend)
```bash
# Check status
sudo supervisorctl status

# Start service
sudo supervisorctl start gelis-backend

# Stop service
sudo supervisorctl stop gelis-backend

# Restart service
sudo supervisorctl restart gelis-backend

# Restart all services
sudo supervisorctl restart all

# View real-time logs
sudo tail -f /var/log/supervisor/gelis-backend.err.log
sudo tail -f /var/log/supervisor/gelis-backend.out.log
```

### Nginx (Web Server)
```bash
# Check status
sudo systemctl status nginx

# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Restart Nginx
sudo systemctl restart nginx

# Reload Nginx (graceful)
sudo systemctl reload nginx

# Test configuration
sudo nginx -t

# View logs
sudo tail -f /var/log/nginx/gelis_access.log
sudo tail -f /var/log/nginx/gelis_error.log
```

### MongoDB (Database)
```bash
# Check status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Stop MongoDB
sudo systemctl stop mongod

# Restart MongoDB
sudo systemctl restart mongod

# View logs
sudo tail -f /var/log/mongodb/mongod.log

# Connect to MongoDB shell
mongosh -u gelis_user -p --authenticationDatabase gelis_db
```

---

## 🗄️ Database Operations

### Connect to Database
```bash
# Connect as application user
mongosh mongodb://gelis_user:YOUR_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db

# Or interactive mode
mongosh
use gelis_db
db.auth("gelis_user", "YOUR_PASSWORD")
```

### Common Database Queries
```javascript
// Show all collections
show collections

// Count users
db.users.countDocuments()

// Find all active users
db.users.find({is_active: true}).pretty()

// Count businesses
db.businesses.countDocuments()

// Get total revenue from transactions
db.transactions.aggregate([
  {$match: {transaction_type: "income"}},
  {$group: {_id: null, total: {$sum: "$amount"}}}
])
```

### Backup Database
```bash
# Full backup
mongodump --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  --out=/home/gelis/backups/backup_$(date +%Y%m%d)

# Backup specific collection
mongodump --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  --collection=users \
  --out=/home/gelis/backups/users_backup

# Compress backup
tar -czf backup.tar.gz /home/gelis/backups/backup_YYYYMMDD/
```

### Restore Database
```bash
# Extract backup
tar -xzf backup.tar.gz

# Restore full database
mongorestore --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  /path/to/backup/gelis_db/

# Restore specific collection
mongorestore --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" \
  --collection=users \
  /path/to/backup/gelis_db/users.bson
```

---

## 🔄 Application Updates

### Update Code from Git
```bash
# Navigate to app directory
cd /home/gelis/app

# Pull latest changes
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies and rebuild
cd ../frontend
yarn install
yarn build

# Restart services
sudo supervisorctl restart gelis-backend
sudo systemctl reload nginx
```

### Manual File Upload
```bash
# From local machine, upload files via SCP
scp -r ./local-folder/* username@server:/home/gelis/app/

# On server, set permissions
sudo chown -R gelis:gelis /home/gelis/app
sudo chmod -R 755 /home/gelis/app
```

---

## 📊 Monitoring & Logs

### View Logs in Real-Time
```bash
# Backend logs (errors)
sudo tail -f /var/log/supervisor/gelis-backend.err.log

# Backend logs (output)
sudo tail -f /var/log/supervisor/gelis-backend.out.log

# Nginx access logs
sudo tail -f /var/log/nginx/gelis_access.log

# Nginx error logs
sudo tail -f /var/log/nginx/gelis_error.log

# MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# System logs
sudo journalctl -u mongod -f
```

### Check Resource Usage
```bash
# CPU & Memory
htop

# Or
top

# Disk usage
df -h

# Specific directory size
du -sh /home/gelis/app

# Memory usage
free -h

# Check running processes
ps aux | grep python
ps aux | grep nginx
```

### API Health Check
```bash
# Check backend health
curl http://localhost:8001/api/health

# Check with domain
curl https://yourdomain.com/api/health

# Test login endpoint
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"owner","password":"owner123"}'
```

---

## 🔒 Security Operations

### SSL Certificate Management
```bash
# Check certificate expiry
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Renew specific domain
sudo certbot renew --cert-name yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Firewall Management
```bash
# Check firewall status
sudo ufw status verbose

# Allow port
sudo ufw allow 8080/tcp

# Deny port
sudo ufw deny 8080/tcp

# Delete rule
sudo ufw delete allow 8080/tcp

# Reload firewall
sudo ufw reload
```

### User Management
```bash
# Create new system user
sudo adduser newuser

# Add user to sudo group
sudo usermod -aG sudo newuser

# Change password
sudo passwd username

# Delete user
sudo deluser username
```

---

## 🛠️ Troubleshooting Commands

### Backend Not Starting
```bash
# Check if port is in use
sudo lsof -i :8001

# Kill process on port
sudo kill -9 $(sudo lsof -t -i:8001)

# Check Python virtual environment
ls -la /home/gelis/app/backend/venv/

# Manually test backend
cd /home/gelis/app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend Not Loading
```bash
# Check if build directory exists
ls -la /home/gelis/app/frontend/build/

# Rebuild frontend
cd /home/gelis/app/frontend
yarn build

# Check Nginx serving files
curl -I http://localhost/
```

### Database Connection Issues
```bash
# Check MongoDB is running
sudo systemctl status mongod

# Test connection
mongosh mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db --eval "db.runCommand({ping: 1})"

# Check MongoDB ports
sudo netstat -tulpn | grep 27017

# Restart MongoDB
sudo systemctl restart mongod
```

### Permission Issues
```bash
# Fix app directory permissions
sudo chown -R gelis:gelis /home/gelis/app
sudo chmod -R 755 /home/gelis/app

# Fix log permissions
sudo chmod 644 /var/log/supervisor/gelis-*.log
sudo chmod 644 /var/log/nginx/gelis_*.log
```

### High CPU/Memory Usage
```bash
# Find process using most CPU
ps aux --sort=-%cpu | head

# Find process using most memory
ps aux --sort=-%mem | head

# Kill specific process
sudo kill -9 <PID>

# Restart all services
sudo supervisorctl restart all
sudo systemctl restart nginx
```

---

## 📦 Environment Variables

### Backend .env Location
```bash
/home/gelis/app/backend/.env
```

### Essential Variables
```bash
MONGO_URL=mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db
DB_NAME=gelis_db
JWT_SECRET_KEY=your_secret_key_here
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com
```

### Frontend .env Location
```bash
/home/gelis/app/frontend/.env.production
```

### Essential Variables
```bash
REACT_APP_BACKEND_URL=https://yourdomain.com
```

---

## 🧪 Testing Commands

### Backend API Tests
```bash
# Health check
curl http://localhost:8001/api/health

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"owner","password":"owner123"}'

# Get users (with token)
TOKEN="your_jwt_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/users

# Test specific endpoint
curl -X GET http://localhost:8001/api/businesses \
  -H "Authorization: Bearer $TOKEN"
```

### Performance Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8001/api/health

# Test frontend
ab -n 1000 -c 10 http://localhost/
```

---

## 🔄 Automated Tasks

### Setup Cron Jobs

```bash
# Edit crontab
crontab -e

# Example: Backup database daily at 2 AM
0 2 * * * mongodump --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" --out=/home/gelis/backups/daily_$(date +\%Y\%m\%d)

# Example: Clean old logs weekly
0 0 * * 0 find /var/log/supervisor -name "*.log" -mtime +30 -delete

# Example: Restart services weekly (Sunday 3 AM)
0 3 * * 0 supervisorctl restart all
```

---

## 📞 Emergency Commands

### Quick Restart Everything
```bash
sudo supervisorctl restart all && \
sudo systemctl restart nginx && \
sudo systemctl restart mongod
```

### Quick Health Check
```bash
# Check all services
echo "=== Supervisor ===" && sudo supervisorctl status && \
echo "=== Nginx ===" && sudo systemctl status nginx --no-pager && \
echo "=== MongoDB ===" && sudo systemctl status mongod --no-pager
```

### Quick Log Check
```bash
# Check last 50 lines of all logs
echo "=== Backend Error Log ===" && sudo tail -50 /var/log/supervisor/gelis-backend.err.log && \
echo "=== Nginx Error Log ===" && sudo tail -50 /var/log/nginx/gelis_error.log
```

### Emergency Stop All
```bash
sudo supervisorctl stop all && \
sudo systemctl stop nginx
```

---

## 📚 Useful Aliases

Add to `~/.bashrc`:

```bash
# GELIS aliases
alias gelis-logs='sudo tail -f /var/log/supervisor/gelis-backend.err.log'
alias gelis-status='sudo supervisorctl status'
alias gelis-restart='sudo supervisorctl restart all && sudo systemctl reload nginx'
alias gelis-backup='mongodump --uri="mongodb://gelis_user:PASSWORD@localhost:27017/gelis_db?authSource=gelis_db" --out=/home/gelis/backups/backup_$(date +%Y%m%d)'
alias gelis-logs-nginx='sudo tail -f /var/log/nginx/gelis_error.log'
alias gelis-update='cd /home/gelis/app && git pull && cd backend && source venv/bin/activate && pip install -r requirements.txt && cd ../frontend && yarn install && yarn build && cd ~ && sudo supervisorctl restart all'

# Reload aliases
source ~/.bashrc
```

---

## 🎯 Common Scenarios

### Scenario 1: Server Reboot
```bash
# All services should auto-start
# Verify services are running
sudo systemctl status nginx
sudo systemctl status mongod
sudo supervisorctl status

# If not, start manually
sudo systemctl start nginx
sudo systemctl start mongod
sudo supervisorctl start all
```

### Scenario 2: Deploy New Version
```bash
cd /home/gelis/app
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && yarn install && yarn build
sudo supervisorctl restart all
```

### Scenario 3: Emergency Rollback
```bash
cd /home/gelis/app
git log --oneline  # Find commit to rollback to
git reset --hard <commit-hash>
# Then follow Scenario 2 steps
```

---

## 📖 Documentation Files

- **Full Deployment Guide**: `/home/gelis/app/DEPLOYMENT_GUIDE.md`
- **Credentials List**: `/home/gelis/app/CREDENTIALS.md`
- **Permission Reference**: `/home/gelis/app/ROLE_PERMISSION_REFERENCE.md`
- **This Quick Reference**: `/home/gelis/app/QUICK_REFERENCE.md`

---

*Last Updated: 2025-12-14*  
*Quick Reference Version: 1.0*
