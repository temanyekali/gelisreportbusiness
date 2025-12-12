# 🚀 Tutorial LENGKAP Deploy GELIS ke Coolify via GitHub

Panduan **SUPER DETAIL** step-by-step deploy aplikasi GELIS menggunakan Coolify dengan metode **Git-based (Public/Private Repository)**.

---

## 📋 Persiapan Sebelum Mulai

### Checklist Yang Harus Sudah Siap:

✅ **Server/VPS dengan Coolify terinstall**
   - IP Public: `XXX.XXX.XXX.XXX`
   - Coolify Dashboard: `http://IP_SERVER:8000`
   - Login credentials ready

✅ **Repository GitHub GELIS**
   - Code sudah di push ke GitHub
   - Public atau Private repository
   - URL: `https://github.com/USERNAME/gelis-app`

✅ **Domain (Optional tapi Recommended)**
   - Frontend: `gelis.yourdomain.com`
   - Backend API: `api.gelis.yourdomain.com`
   - DNS sudah pointing ke IP server

✅ **Files Penting di Repository:**
   ```
   ✓ /backend/Dockerfile
   ✓ /backend/requirements.txt
   ✓ /frontend/Dockerfile
   ✓ /frontend/nginx.conf
   ✓ /frontend/package.json
   ```

**Jika belum ada Dockerfile**, scroll ke bagian bawah untuk template!

---

## 🎯 PART 1: Setup MongoDB Database (5 menit)

### Step 1.1: Buka Coolify Dashboard

```
Browser → http://IP_SERVER_ANDA:8000
Login dengan credentials Anda
```

**Tampilan setelah login:**
- Sidebar kiri: Dashboard, Projects, Applications, Databases, Services, dll
- Main area: Overview statistics

### Step 1.2: Create New Service (MongoDB)

**Klik urutan:**
1. **Sidebar → "Services"**
2. **Klik tombol "+ New Service"** (tombol biru di pojok kanan atas)
3. **Pilih "MongoDB"** dari list databases

**Tampilan Pilihan Database:**
```
[MongoDB]  [PostgreSQL]  [MySQL]  [Redis]  [MariaDB]
[Elasticsearch]  [ClickHouse]  [KeyDB]  dll...
```

### Step 1.3: Configure MongoDB

**Form Configuration MongoDB:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Service Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Service Name: *
[gelis-mongodb                          ]

Version:
[7.0                 ▼]  ← Pilih 7.0

Database Name: *
[gelis_db                               ]

Database Username: *
[gelis_user                             ]

Database Password: *
[●●●●●●●●●●●●●]  🔄 Generate  ← Klik Generate!

Root Password: *
[●●●●●●●●●●●●●]  🔄 Generate  ← Klik Generate!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Create Service]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**IMPORTANT:**
- Klik tombol **"Generate"** untuk auto-generate password yang kuat
- **CATAT passwords** yang di-generate! Copy ke notepad.

### Step 1.4: Create & Wait

**Klik "Create Service"**

**Proses yang terjadi:**
```
1. [⏳] Pulling MongoDB image... (2-3 menit)
2. [⏳] Creating container...
3. [⏳] Starting MongoDB...
4. [✓] Health check passed!
5. [✓] Status: Running
```

**Indikator Sukses:**
- Status badge: **🟢 Running** (hijau)
- Health check: **✓ Healthy**

### Step 1.5: Get Connection String

**Setelah status Running:**

1. **Klik service "gelis-mongodb"** (dari list Services)
2. **Tab "Configuration"** atau **"Connection"**
3. **Lihat section "Connection String"**

**Connection String Format:**
```
mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
```

**📝 IMPORTANT - CATAT INFO INI:**
```
Service Name: gelis-mongodb
Database: gelis_db
Username: gelis_user
Password: [password yang di-generate]
Connection String: mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
```

**⚠️ PENTING:** 
- Hostname adalah **service name**: `gelis-mongodb` (BUKAN localhost atau IP!)
- Ini adalah internal Docker network
- Port 27017 TIDAK exposed ke internet (aman!)

---

## 🎯 PART 2: Deploy Backend FastAPI (10 menit)

### Step 2.1: Create New Application

**Klik urutan:**
1. **Sidebar → "Applications"**
2. **Klik "+ New Application"** (tombol biru pojok kanan atas)

### Step 2.2: Pilih Deployment Type

**Tampilan pilihan:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
How do you want to deploy?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌────────────────────────────────────────┐
│  📦 Git Based                          │
│                                        │
│  [Public Repository]                   │  ← Pilih ini jika repo public
│  [Private Repository (GitHub App)]    │  ← Pilih ini jika repo private
│  [Private Repository (Deploy Key)]    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│  🐳 Docker Based                       │
│                                        │
│  [Dockerfile]                          │
│  [Docker Compose]                      │
│  [Docker Image]                        │
└────────────────────────────────────────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**PILIH:**
- **"Public Repository"** - Jika GitHub repo Anda public
- **"Private Repository (GitHub App)"** - Jika private

### Step 2.3A: Public Repository Setup

**Jika pilih Public Repository:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connect Git Repository
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Git Repository URL: *
[https://github.com/USERNAME/gelis-app  ]

Branch:
[main                                   ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Continue]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Fill:**
- Git Repository URL: `https://github.com/USERNAME/gelis-app`
- Branch: `main` (atau `master` jika masih pakai master)

**Klik "Continue"**

### Step 2.3B: Private Repository Setup (GitHub App)

**Jika pilih Private Repository (GitHub App):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connect GitHub App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Install GitHub App]  ← Klik tombol ini
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Proses:**
1. **Klik "Install GitHub App"**
2. Browser redirect ke GitHub
3. **Login ke GitHub** (jika belum)
4. **Authorize Coolify** untuk akses repositories
5. **Pilih repositories** yang ingin di-akses:
   - Option A: All repositories
   - Option B: Selected repositories → Pilih `gelis-app`
6. **Klik "Install & Authorize"**
7. Redirect kembali ke Coolify

**Setelah authorize berhasil:**
```
✓ GitHub App connected
Select Repository: [gelis-app ▼]
Select Branch: [main]
```

### Step 2.4: Configure Backend Application

**Setelah repository connected, form configuration muncul:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Application Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Name: *
[gelis-backend                          ]

Base Directory:
[/backend                               ]  ← IMPORTANT!

Port: *
[8001                                   ]

Build Pack:
[Dockerfile                        ▼]

Dockerfile Path:
[./Dockerfile                           ]

Start Command: (optional)
[                                       ]
  ← Kosongkan, Dockerfile sudah ada CMD

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health Check Enabled: [✓]  ← Check ini!
Health Check Path:
[/                                      ]

Health Check Interval (seconds):
[30                                     ]

Health Check Timeout (seconds):
[10                                     ]

Health Check Retries:
[3                                      ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Continue]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**PENTING:**
- **Base Directory:** `/backend` - Karena backend ada di folder backend/
- **Port:** `8001` - Sesuai dengan EXPOSE di Dockerfile
- **Build Pack:** Dockerfile - Auto-detect dari file
- **Health Check Path:** `/` - Root endpoint

**Klik "Continue"**

### Step 2.5: Set Environment Variables

**Tampilan Environment Variables:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[+ Add Variable]

Name                    Value
────────────────────────────────────────
[MONGO_URL          ] [                ]
[DB_NAME            ] [                ]
[SECRET_KEY         ] [                ]
[ALGORITHM          ] [                ]
[ACCESS_TOKEN...    ] [                ]
[APP_NAME           ] [                ]
[ENVIRONMENT        ] [                ]
[DEBUG              ] [                ]
[CORS_ORIGINS       ] [                ]
[MAX_UPLOAD_SIZE    ] [                ]
[UPLOAD_DIR         ] [                ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Create Application]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Klik "+ Add Variable" untuk setiap env var berikut:**

**Environment Variables Backend:**

| Name | Value | Note |
|------|-------|------|
| `MONGO_URL` | `mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db` | Ganti PASSWORD! |
| `DB_NAME` | `gelis_db` | |
| `SECRET_KEY` | `[Generate 64 char random]` | See below ⬇️ |
| `ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `43200` | |
| `APP_NAME` | `GELIS` | |
| `ENVIRONMENT` | `production` | |
| `DEBUG` | `False` | |
| `CORS_ORIGINS` | `https://gelis.yourdomain.com` | Ganti domain! |
| `MAX_UPLOAD_SIZE` | `10485760` | |
| `UPLOAD_DIR` | `/app/uploads` | |

**Generate SECRET_KEY:**

```bash
# Cara 1: Python (di terminal local)
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Cara 2: OpenSSL
openssl rand -base64 64 | tr -d '\n'

# Cara 3: Online generator
# https://www.random.org/strings/
```

**Copy hasil generate ke value SECRET_KEY**

**⚠️ IMPORTANT:**
- **MONGO_URL:** Hostname HARUS `gelis-mongodb` (service name!)
- **CORS_ORIGINS:** Update dengan domain frontend Anda
- Jika belum ada domain, isi dengan IP: `http://IP_SERVER:3000`

### Step 2.6: Create & Deploy Backend

**Klik "Create Application"**

**Proses Deployment (Monitor di Logs):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deployment Logs - gelis-backend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[00:01] 🔄 Cloning repository...
[00:05] ✓ Repository cloned
[00:06] 🔄 Checking out branch: main
[00:07] ✓ Branch checked out
[00:08] 🔄 Building Docker image...
[00:10]   Step 1/10 : FROM python:3.10-slim
[00:15]   Step 2/10 : WORKDIR /app
[00:16]   Step 3/10 : RUN apt-get update...
[01:30]   Step 4/10 : COPY requirements.txt .
[01:31]   Step 5/10 : RUN pip install...
[03:45]   Step 6/10 : COPY . .
[03:46]   Step 7/10 : RUN mkdir -p uploads
[03:47]   Step 8/10 : EXPOSE 8001
[03:48]   Step 9/10 : HEALTHCHECK...
[03:49]   Step 10/10 : CMD ["uvicorn"...]
[03:50] ✓ Build completed successfully
[03:51] 🔄 Starting container...
[03:55] ✓ Container started
[03:56] 🔄 Running health check...
[04:01] ✓ Health check passed!
[04:02] ✓ Deployment successful!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: 🟢 Running | Health: ✓ Healthy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Timeline:**
- Clone: ~5 seconds
- Build: ~3-4 minutes (first time, karena pip install)
- Start: ~5 seconds
- Health check: ~5 seconds
- **Total: ~4-5 minutes**

**Indikator Sukses:**
- Status: **🟢 Running**
- Health: **✓ Healthy**
- Logs shows: `Application startup complete`

### Step 2.7: Test Backend

**Get Backend URL:**

Coolify auto-assign URL:
```
http://gelis-backend.coolify.yourdomain.com
atau
http://IP_SERVER:[random-port]
```

**Test di browser atau curl:**

```bash
# Test root endpoint
curl http://gelis-backend.coolify.yourdomain.com/

# Should return: {"detail":"Not Found"}
# (404 is OK, berarti FastAPI running!)

# Test actual endpoint
curl http://gelis-backend.coolify.yourdomain.com/api/

# Should return JSON response
```

---

## 🎯 PART 3: Deploy Frontend React (15 menit)

### Step 3.1: Create New Application (Frontend)

**Kembali ke Applications:**
1. **Sidebar → "Applications"**
2. **"+ New Application"**

### Step 3.2: Connect Repository (Same as Backend)

**Pilih:**
- Public Repository atau Private Repository (GitHub App)
- Same repository: `gelis-app`
- Same branch: `main`

### Step 3.3: Configure Frontend Application

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Application Configuration
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Application Name: *
[gelis-frontend                         ]

Base Directory:
[/frontend                              ]  ← IMPORTANT!

Port: *
[80                                     ]

Build Pack:
[Dockerfile                        ▼]

Dockerfile Path:
[./Dockerfile                           ]

Start Command: (optional)
[                                       ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health Check Enabled: [✓]
Health Check Path:
[/                                      ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Continue]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Fill:**
- **Application Name:** `gelis-frontend`
- **Base Directory:** `/frontend`
- **Port:** `80` (Nginx default)
- **Build Pack:** Dockerfile

### Step 3.4: Environment Variables Frontend

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment Variables
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name                         Value
────────────────────────────────────────
[REACT_APP_BACKEND_URL  ] [           ]
[REACT_APP_NAME         ] [           ]
[REACT_APP_VERSION      ] [           ]
[REACT_APP_ENVIRONMENT  ] [           ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Environment Variables:**

| Name | Value | Note |
|------|-------|------|
| `REACT_APP_BACKEND_URL` | `https://api.gelis.yourdomain.com` | Domain backend! |
| `REACT_APP_NAME` | `GELIS` | |
| `REACT_APP_VERSION` | `1.0.0` | |
| `REACT_APP_ENVIRONMENT` | `production` | |

**⚠️ CRITICAL:**
- `REACT_APP_BACKEND_URL` HARUS URL **public** backend Anda
- Jika belum setup domain, gunakan: `http://IP_SERVER:[backend-port]`
- Environment variables akan **di-embed** ke build, bukan runtime!

### Step 3.5: Deploy Frontend

**Klik "Create Application"**

**Proses Deployment:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deployment Logs - gelis-frontend
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[00:01] 🔄 Cloning repository...
[00:05] ✓ Repository cloned
[00:06] 🔄 Building Docker image...
[00:08]   Step 1/12 : FROM node:20-alpine AS builder
[00:30]   Step 2/12 : WORKDIR /app
[00:31]   Step 3/12 : COPY package.json yarn.lock
[00:32]   Step 4/12 : RUN yarn install...
[08:45]   ← LAMA! ~8 menit untuk yarn install
[08:46]   Step 5/12 : COPY . .
[08:50]   Step 6/12 : RUN yarn build...
[10:30]   ← Build production ~2 menit
[10:31]   Step 7/12 : FROM nginx:alpine
[10:35]   Step 8/12 : COPY build files...
[10:36]   Step 9/12 : COPY nginx.conf...
[10:37]   Step 10/12 : EXPOSE 80
[10:38]   Step 11/12 : HEALTHCHECK...
[10:39]   Step 12/12 : CMD nginx...
[10:40] ✓ Build completed!
[10:41] 🔄 Starting container...
[10:45] ✓ Container started
[10:46] 🔄 Health check...
[10:51] ✓ Health check passed!
[10:52] ✓ Deployment successful!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: 🟢 Running | Health: ✓ Healthy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Timeline:**
- Clone: ~5 seconds
- yarn install: ~8-10 minutes (first time!)
- yarn build: ~2-3 minutes
- Nginx setup: ~5 seconds
- **Total: ~12-15 minutes**

**Why so long?**
- `yarn install` download banyak node_modules
- React build mengcompile semua components
- Multi-stage build (builder + nginx)

---

## 🎯 PART 4: Setup Domain & SSL (10 menit)

### Step 4.1: Configure DNS Records

**Di Control Panel Domain Anda** (Cloudflare, Namecheap, dll):

**Add DNS Records:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DNS Management - yourdomain.com
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type  | Name  | Value          | TTL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A     | @     | IP_SERVER      | Auto
A     | www   | IP_SERVER      | Auto
A     | api   | IP_SERVER      | Auto

atau dengan subdomain:

A     | gelis     | IP_SERVER  | Auto
A     | api.gelis | IP_SERVER  | Auto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Contoh:**
```
A @ 123.456.789.012
A www 123.456.789.012
A api 123.456.789.012
```

**Save DNS records**

**Wait DNS Propagation:** 5 menit - 48 jam (usually < 1 jam)

**Check DNS:**
```bash
# Terminal
nslookup gelis.yourdomain.com
nslookup api.gelis.yourdomain.com

# Online tools
# https://dnschecker.org
```

### Step 4.2: Add Domain ke Backend

**Di Coolify:**

1. **Applications → gelis-backend**
2. **Tab "Domains"**
3. **Klik "+ Add Domain"**

**Form:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add Domain
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Domain:
[api.gelis.yourdomain.com              ]

Generate SSL Certificate: [✓]  ← Check!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Cancel]  [Add Domain]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Fill:**
- Domain: `api.gelis.yourdomain.com`
- Generate SSL: **Checked** ✓

**Klik "Add Domain"**

**Proses SSL Generation:**
```
[⏳] Validating domain...
[⏳] Requesting SSL from Let's Encrypt...
[⏳] Installing certificate...
[✓] SSL certificate installed!
```

**Duration:** ~1-2 menit

**Result:**
- Domain: ✓ `api.gelis.yourdomain.com`
- SSL: ✓ Valid (Let's Encrypt)
- Status: 🔒 Secure

### Step 4.3: Add Domain ke Frontend

**Repeat untuk Frontend:**

1. **Applications → gelis-frontend**
2. **Tab "Domains"**
3. **"+ Add Domain"**

**Add 2 domains:**

**Domain 1:**
```
Domain: gelis.yourdomain.com
Generate SSL: [✓]
```

**Domain 2:**
```
Domain: www.gelis.yourdomain.com
Generate SSL: [✓]
```

**SSL akan auto-generate untuk kedua domain**

### Step 4.4: Update Frontend Environment (CRITICAL!)

**⚠️ IMPORTANT:** Frontend environment variables di-embed saat build!

Setelah domain setup, **REBUILD frontend** dengan env var yang benar:

1. **Applications → gelis-frontend**
2. **Tab "Environment Variables"**
3. **Edit `REACT_APP_BACKEND_URL`:**
   ```
   Old: http://IP_SERVER:8001
   New: https://api.gelis.yourdomain.com
   ```
4. **Save**
5. **Tab "Deployments"**
6. **Klik "Redeploy"** atau **"Restart"**

Wait ~10-12 menit untuk rebuild.

### Step 4.5: Verify SSL

**Test di browser:**

```
https://gelis.yourdomain.com
https://api.gelis.yourdomain.com
```

**Should see:**
- 🔒 Padlock icon (secure)
- No SSL warnings
- Certificate issued by Let's Encrypt

**Test via curl:**
```bash
curl -I https://gelis.yourdomain.com
# HTTP/2 200
# ...

curl -I https://api.gelis.yourdomain.com
# HTTP/2 404 (OK, FastAPI running)
```

---

## 🎯 PART 5: Setup Auto-Deploy (3 menit)

### Step 5.1: Enable Webhook di Coolify

**Backend:**

1. **Applications → gelis-backend**
2. **Tab "Settings"** atau **"Webhooks"**
3. **Toggle "Auto Deploy on Git Push"** → **ON**
4. **Webhook URL muncul:**
   ```
   https://coolify.yourdomain.com/webhooks/xxx-xxx-xxx
   ```
5. **Klik "Copy"** - Copy webhook URL

**Frontend:**

Repeat untuk `gelis-frontend`:
1. **Applications → gelis-frontend**
2. **Tab "Webhooks"**
3. **Enable Auto Deploy**
4. **Copy webhook URL**

### Step 5.2: Add Webhook ke GitHub

**Di GitHub Repository:**

1. **Repository → Settings** (repo settings, bukan account settings)
2. **Left sidebar → "Webhooks"**
3. **"Add webhook"**

**Form Webhook (Backend):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Add Webhook
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Payload URL:
[https://coolify.yourdomain.com/webhooks/...]

Content type:
[application/json                  ▼]

Secret: (optional)
[                                      ]

Which events would you like to trigger this webhook?
○ Just the push event  ← Select this
○ Let me select individual events
○ Send me everything

Active: [✓]  ← Check!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         [Add webhook]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Klik "Add webhook"**

**Repeat untuk Frontend webhook**

**Result:**
- 2 webhooks added
- Status: ✓ Recent Delivery (after first trigger)

### Step 5.3: Test Auto-Deploy

**Test dengan commit baru:**

```bash
# Di local machine
cd /path/to/gelis-app

# Make a small change
echo "# Test auto-deploy" >> README.md

# Commit & push
git add README.md
git commit -m "Test auto-deploy"
git push origin main
```

**Watch Coolify:**
1. **Applications → gelis-backend**
2. **Tab "Deployments"**
3. **New deployment should appear automatically!**
4. **Status:** Building → Running

**Duration:** Same as manual deploy (~4 menit backend, ~12 menit frontend)

---

## 🎯 PART 6: Seed Mock Data (2 menit)

### Step 6.1: SSH ke Server

```bash
ssh root@IP_SERVER_ANDA
```

### Step 6.2: Find Backend Container

```bash
# List all containers
docker ps

# Find gelis-backend container
docker ps | grep gelis-backend

# Output example:
# abc123def456  gelis-backend  Up 10 minutes  0.0.0.0:8001->8001/tcp
```

**Get Container ID/Name:** `abc123def456` atau `gelis-backend-xxx`

### Step 6.3: Execute Seed Script

**Method 1: Via Docker Exec**

```bash
# Get into container
docker exec -it CONTAINER_ID bash

# Inside container
cd /app
python3 scripts/seed_complete_mockup.py

# Exit container
exit
```

**Method 2: Direct Execute**

```bash
docker exec CONTAINER_ID python3 /app/scripts/seed_complete_mockup.py
```

**Output:**
```
============================================================
🌱 GELIS COMPLETE MOCK DATA SEEDER
============================================================
🧹 Clearing ALL existing data...
   ✓ Deleted X documents...

👑 Creating roles...
   ✓ Created 7 roles

👥 Creating users...
   ✓ Created 14 users

... (more output)

============================================================
✅ SEED COMPLETED SUCCESSFULLY!
============================================================

📊 Summary:
   • Users: 14
   • Businesses: 5
   • Orders: 345
   • Transactions: 404
   ...
```

**Duration:** ~5-10 seconds

---

## 🎯 PART 7: Test Aplikasi (5 menit)

### Step 7.1: Test Backend API

**Via Browser:**
```
https://api.gelis.yourdomain.com/
```

**Expected:** 
```json
{"detail":"Not Found"}
```
(404 is OK! FastAPI running)

**Via curl:**
```bash
# Test health endpoint
curl https://api.gelis.yourdomain.com/api/

# Test with data
curl https://api.gelis.yourdomain.com/api/businesses
```

### Step 7.2: Test Frontend

**Open browser:**
```
https://gelis.yourdomain.com
```

**Expected:**
- ✓ GELIS Login page loads
- ✓ No HTTPS warnings
- ✓ No console errors (F12)
- ✓ Logo dan form visible

### Step 7.3: Login Test

**Demo Credentials:**
```
Username: owner
Password: owner123
```

**Click "Masuk"**

**Expected:**
- ✓ Redirect ke Dashboard
- ✓ Data muncul (dari mock data)
- ✓ Sidebar navigation working
- ✓ All modules accessible

### Step 7.4: Test All Modules

**Navigate:**
1. ✓ Dashboard - Shows stats cards, charts
2. ✓ Businesses - Lists 5 businesses
3. ✓ Orders - Lists 345 orders
4. ✓ Transactions - Lists 404 transactions
5. ✓ Reports - Lists loket & kasir reports
6. ✓ Users - Lists 14 users
7. ✓ Settings - Shows settings tabs

**Create Test:**
1. Orders → "+ Buat Pesanan"
2. Fill form
3. Submit
4. Verify order created

**Everything working = Deployment SUCCESS! 🎉**

---

## 📊 Monitoring & Maintenance

### View Logs

**Backend Logs:**
```
Applications → gelis-backend → Logs

Real-time logs akan muncul:
- API requests
- Database queries
- Errors (jika ada)
```

**Frontend Logs:**
```
Applications → gelis-frontend → Logs

Nginx access logs
```

### Resource Monitoring

**Applications → gelis-backend → Metrics**

**Shows:**
- CPU usage
- Memory usage
- Network I/O
- Disk usage

**Set Alerts:**
- CPU > 80%
- Memory > 90%
- Container stopped

### Restart Services

**If needed:**

```
Applications → gelis-backend → Actions → Restart
```

**Or via CLI:**
```bash
ssh root@server
docker restart gelis-backend-xxx
```

---

## 🐛 Troubleshooting

### Problem 1: "Build Failed - Dockerfile not found"

**Cause:** Base directory salah atau Dockerfile tidak ada

**Solution:**
```
1. Check Base Directory: MUST be /backend or /frontend
2. Check Dockerfile exists di repo: backend/Dockerfile
3. Check branch: MUST be correct branch (main)
```

### Problem 2: "Health Check Failed"

**Cause:** Backend tidak bisa start atau port salah

**Solution:**
```
1. Check logs: Applications → Logs
2. Verify MONGO_URL correct
3. Verify port 8001 exposed
4. Check Dockerfile CMD correct
```

### Problem 3: "Cannot Connect to MongoDB"

**Cause:** Connection string salah atau MongoDB not running

**Solution:**
```
1. Verify MongoDB status: Services → gelis-mongodb
2. Check MONGO_URL format:
   mongodb://gelis_user:PASSWORD@gelis-mongodb:27017/gelis_db?authSource=gelis_db
3. Hostname MUST be service name: gelis-mongodb
4. NOT localhost or 127.0.0.1!
```

### Problem 4: "Frontend CORS Error"

**Cause:** Backend CORS_ORIGINS tidak termasuk frontend domain

**Solution:**
```
1. Backend → Environment Variables
2. Edit CORS_ORIGINS: https://gelis.yourdomain.com
3. Restart backend
4. Test again
```

### Problem 5: "SSL Certificate Failed"

**Cause:** DNS belum propagate atau port 80/443 blocked

**Solution:**
```
1. Wait DNS propagation (up to 48h)
2. Test DNS: nslookup gelis.yourdomain.com
3. Check firewall: Port 80, 443 open
4. Disable Cloudflare proxy temporarily
5. Regenerate certificate: Domains → Regenerate SSL
```

### Problem 6: "Frontend Shows Old Code After Deploy"

**Cause:** Browser cache atau build cache

**Solution:**
```
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Clear browser cache
3. Rebuild frontend: Redeploy with --no-cache flag
```

---

## 📦 Template Files (If Missing)

### backend/Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

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

### frontend/Dockerfile

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

# Build for production
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy build files
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

### frontend/nginx.conf

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

---

## ✅ Deployment Checklist

Copy checklist ini dan check saat deploy:

### Pre-Deployment
- [ ] Server ready dengan Coolify installed
- [ ] Code pushed ke GitHub
- [ ] Dockerfile exists (backend + frontend)
- [ ] nginx.conf exists (frontend)
- [ ] Domain ready (optional)

### MongoDB Setup
- [ ] MongoDB service created
- [ ] Status: Running
- [ ] Connection string noted
- [ ] Passwords saved

### Backend Deployment
- [ ] Application created
- [ ] Repository connected
- [ ] Base directory: /backend
- [ ] Port: 8001
- [ ] Environment variables set
- [ ] MONGO_URL correct (service name!)
- [ ] Deployment status: Running
- [ ] Health check: Passed
- [ ] Test API endpoint

### Frontend Deployment
- [ ] Application created
- [ ] Repository connected
- [ ] Base directory: /frontend
- [ ] Port: 80
- [ ] REACT_APP_BACKEND_URL correct
- [ ] Deployment status: Running
- [ ] Health check: Passed
- [ ] Test frontend loads

### Domain & SSL
- [ ] DNS records added
- [ ] DNS propagated
- [ ] Backend domain added
- [ ] Backend SSL generated
- [ ] Frontend domain added
- [ ] Frontend SSL generated
- [ ] Frontend rebuilt with correct backend URL
- [ ] All https links working

### Auto-Deploy
- [ ] Backend webhook enabled
- [ ] Frontend webhook enabled
- [ ] GitHub webhooks added
- [ ] Test auto-deploy working

### Mock Data
- [ ] SSH to server
- [ ] Seed script executed
- [ ] Mock data visible in app

### Final Testing
- [ ] Login working
- [ ] Dashboard loads
- [ ] All modules accessible
- [ ] CRUD operations working
- [ ] No console errors
- [ ] Mobile responsive working

---

## 🎉 Selamat! Deployment Berhasil!

Aplikasi GELIS Anda sekarang running di:

**URLs:**
- Frontend: https://gelis.yourdomain.com
- Backend API: https://api.gelis.yourdomain.com
- Coolify Dashboard: http://IP_SERVER:8000

**Features:**
✅ Auto-deploy dari GitHub  
✅ Zero-downtime updates  
✅ SSL/HTTPS otomatis  
✅ Monitoring & logs  
✅ Easy rollback  
✅ Scalable  

**Next Steps:**
1. Ganti demo passwords
2. Configure backup schedule
3. Setup monitoring alerts
4. Add more users
5. Start using real data

---

**Happy Deploying! 🚀**

Butuh bantuan lebih lanjut? 
- Check logs di Coolify
- Review [MOCK_DATA_GUIDE.md](MOCK_DATA_GUIDE.md)
- Review [INSTALASI_COOLIFY.md](INSTALASI_COOLIFY.md)

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
