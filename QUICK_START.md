# ⚡ Quick Start Guide - GELIS

Panduan cepat untuk memulai aplikasi GELIS di server Anda.

---

## 🚀 Instalasi Cepat (TL;DR)

```bash
# 1. Update sistem
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs python3.10 python3-pip nginx
sudo npm install -g yarn pm2

# 3. Install MongoDB 7.0
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update && sudo apt install -y mongodb-org
sudo systemctl start mongod && sudo systemctl enable mongod

# 4. Clone & setup aplikasi
cd /opt
sudo git clone YOUR_REPO_URL gelis
sudo chown -R $USER:$USER /opt/gelis

# 5. Setup backend
cd /opt/gelis/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 6. Setup frontend
cd /opt/gelis/frontend
yarn install
yarn build

# 7. Configure MongoDB
mongosh
use gelis_db
db.createUser({
  user: "gelis_user",
  pwd: "STRONG_PASSWORD",
  roles: [ { role: "readWrite", db: "gelis_db" } ]
})
exit

# 8. Create .env files (edit dengan editor)
nano /opt/gelis/backend/.env
nano /opt/gelis/frontend/.env

# 9. Start backend dengan PM2
cd /opt/gelis/backend
pm2 start venv/bin/uvicorn --name gelis-backend -- server:app --host 0.0.0.0 --port 8001
pm2 save
pm2 startup

# 10. Configure Nginx
sudo nano /etc/nginx/sites-available/gelis
# (copy config dari INSTALASI_SERVER.md)
sudo ln -s /etc/nginx/sites-available/gelis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 11. Setup SSL
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# ✅ Done! Akses https://yourdomain.com
```

---

## 📝 Template File .env

### Backend `.env`

```env
MONGO_URL=mongodb://gelis_user:STRONG_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db
SECRET_KEY=GENERATE_WITH_python3_-c_import_secrets_print_secrets_token_urlsafe_64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
APP_NAME=GELIS
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/opt/gelis/backend/uploads
```

### Frontend `.env`

```env
REACT_APP_BACKEND_URL=https://yourdomain.com
REACT_APP_NAME=GELIS
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
```

---

## 🔑 Default Login Credentials

Setelah seed data:

| Role | Username | Password |
|------|----------|----------|
| Owner | owner | owner123 |
| Manager | manager | manager123 |
| Finance | finance | finance123 |
| Loket | loket1 | loket123 |
| Kasir | kasir1 | kasir123 |
| Admin | admin1 | admin123 |
| Teknisi | teknisi1 | teknisi123 |

**⚠️ PENTING: Ganti password setelah login pertama!**

---

## 🛠️ Command Cheat Sheet

### PM2 Commands

```bash
pm2 status                    # Cek status
pm2 restart gelis-backend     # Restart backend
pm2 logs gelis-backend        # Lihat logs
pm2 monit                     # Monitoring realtime
pm2 save                      # Save process list
```

### Nginx Commands

```bash
sudo nginx -t                 # Test config
sudo systemctl reload nginx   # Reload config
sudo systemctl restart nginx  # Restart nginx
sudo tail -f /var/log/nginx/gelis_error.log  # Error logs
```

### MongoDB Commands

```bash
sudo systemctl status mongod  # Status
sudo systemctl restart mongod # Restart
mongosh -u gelis_user -p --authenticationDatabase gelis_db gelis_db  # Connect
```

### Update Aplikasi

```bash
cd /opt/gelis
git pull
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate
cd ../frontend && yarn install && yarn build
pm2 restart gelis-backend
sudo systemctl reload nginx
```

---

## 🔍 Troubleshooting Quick Fixes

### Backend Error

```bash
pm2 logs gelis-backend        # Cek logs
pm2 restart gelis-backend     # Restart
curl http://localhost:8001    # Test langsung
```

### Nginx 502 Error

```bash
sudo systemctl status nginx   # Nginx OK?
pm2 status                    # Backend running?
sudo nginx -t                 # Config OK?
```

### MongoDB Connection Error

```bash
sudo systemctl status mongod  # MongoDB running?
mongosh                       # Bisa connect?
cat /opt/gelis/backend/.env | grep MONGO_URL  # URL benar?
```

---

## 📱 Mobile Testing

1. Buka Chrome DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Test di:
   - iPhone SE (375px)
   - iPhone 12 (390px)
   - Samsung S20 (360px)
   - iPad (768px)

---

## 📞 Need Help?

1. **Cek logs terlebih dahulu**
2. **Baca error message dengan teliti**
3. **Lihat dokumentasi lengkap:**
   - `/app/INSTALASI_SERVER.md` - Instalasi detail
   - `/app/MOBILE_RESPONSIVE_GUIDE.md` - Mobile features
4. **Google error message**
5. **Check official docs:**
   - FastAPI: https://fastapi.tiangolo.com
   - React: https://react.dev
   - MongoDB: https://docs.mongodb.com

---

## ✅ Post-Installation Checklist

- [ ] Backend running di PM2
- [ ] Frontend build berhasil
- [ ] MongoDB authentication OK
- [ ] Nginx reverse proxy OK
- [ ] SSL certificate installed
- [ ] Domain pointing ke server
- [ ] Test login semua role
- [ ] Test create/edit di semua module
- [ ] Test di mobile device
- [ ] Setup auto backup
- [ ] Change default passwords
- [ ] Setup monitoring (optional)

---

**🎉 Selamat! Aplikasi GELIS Anda sudah siap digunakan!**

Akses: https://yourdomain.com

---

**Butuh instalasi detail?** Lihat `INSTALASI_SERVER.md`  
**Butuh info mobile features?** Lihat `MOBILE_RESPONSIVE_GUIDE.md`

---

**Dibuat dengan ❤️ untuk GELIS**
