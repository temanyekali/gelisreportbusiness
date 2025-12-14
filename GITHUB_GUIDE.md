# 🐙 Panduan Lengkap GitHub untuk GELIS

> **Tutorial Setup GitHub Repository & Deploy ke Server Ubuntu**

---

## 📋 Daftar Isi

1. [Pengenalan GitHub](#pengenalan-github)
2. [Setup GitHub Account](#setup-github-account)
3. [Membuat Repository Baru](#membuat-repository-baru)
4. [Push Code ke GitHub](#push-code-ke-github)
5. [GitHub Personal Access Token](#github-personal-access-token)
6. [Clone Repository di Server](#clone-repository-di-server)
7. [Update & Deploy dari GitHub](#update--deploy-dari-github)
8. [Git Workflow untuk Tim](#git-workflow-untuk-tim)
9. [Troubleshooting](#troubleshooting)

---

## Pengenalan GitHub

### Apa itu GitHub?

GitHub adalah platform untuk menyimpan dan mengelola code dengan **Git version control**. 

### Kenapa Perlu GitHub?

✅ **Backup Otomatis**: Code tersimpan aman di cloud  
✅ **Version Control**: Track semua perubahan code  
✅ **Collaboration**: Kerja sama tim dengan mudah  
✅ **Easy Deployment**: Deploy update dengan `git pull`  
✅ **Rollback**: Kembali ke versi sebelumnya  
✅ **CI/CD**: Automasi testing & deployment  

---

## Setup GitHub Account

### 1. Buat Account GitHub

1. Buka: https://github.com/signup
2. Isi form registrasi:
   - Email address: `your_email@example.com`
   - Password: (gunakan password kuat)
   - Username: `your-username`
3. Verify email
4. Setup profile (optional tapi recommended)

### 2. Install Git di Komputer Lokal

**Windows:**
- Download: https://git-scm.com/download/win
- Jalankan installer
- Pilih default options

**macOS:**
```bash
# Install via Homebrew
brew install git

# Atau download installer
# https://git-scm.com/download/mac
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install git
```

**Verify Installation:**
```bash
git --version
# Output: git version 2.x.x
```

### 3. Configure Git

```bash
# Set nama dan email
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"

# Verify
git config --list
```

---

## Membuat Repository Baru

### Option 1: Buat Repository di GitHub (Recommended)

1. **Login ke GitHub**: https://github.com
2. **Klik tombol "New"** (atau "+" di top-right → "New repository")
3. **Isi form**:
   ```
   Repository name: gelis-app
   Description: GELIS - Gerbang Elektronik Layanan Informasi Sistem
   Visibility: ✅ Private (recommended untuk production app)
   
   JANGAN centang:
   ❌ Add a README file
   ❌ Add .gitignore
   ❌ Choose a license
   
   (Karena kita akan push existing code)
   ```
4. **Klik "Create repository"**
5. **Copy URL repository**:
   ```
   HTTPS: https://github.com/username/gelis-app.git
   SSH:   git@github.com:username/gelis-app.git
   ```

### Option 2: Import dari Emergent

Jika Anda menggunakan Emergent platform:

1. **Gunakan fitur "Save to GitHub"** di Emergent UI
2. Follow on-screen instructions
3. Repository akan otomatis dibuat

---

## Push Code ke GitHub

### 1. Persiapan Code

```bash
# Masuk ke directory aplikasi
cd /path/to/gelis-app

# Check apakah sudah ada .git folder
ls -la | grep .git

# Jika belum ada, initialize git
git init
```

### 2. Buat .gitignore

File `.gitignore` mencegah file sensitive ter-upload ke GitHub:

```bash
# Buat file .gitignore
cat > .gitignore <<'EOF'
# ===================================
# GELIS .gitignore
# ===================================

# Environment Variables (PENTING!)
.env
.env.*
*.env
!.env.example

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp/
.pnp.js
package-lock.json

# React Build
frontend/build/
frontend/dist/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
/var/log/

# Database
*.db
*.sqlite
*.sqlite3

# Temporary files
tmp/
temp/
*.tmp

# System
.emergent/
*.bak
*.cache
EOF
```

### 3. Add & Commit Files

```bash
# Add semua file
git add .

# Check status (apa yang akan di-commit)
git status

# Commit pertama
git commit -m "Initial commit: GELIS application

- FastAPI backend
- React frontend  
- MongoDB integration
- Complete RBAC system with 7 roles
- Executive reports & analytics
- Technician job management"
```

### 4. Link ke GitHub Repository

```bash
# Add remote repository
git remote add origin https://github.com/username/gelis-app.git

# Verify
git remote -v
# Output:
# origin  https://github.com/username/gelis-app.git (fetch)
# origin  https://github.com/username/gelis-app.git (push)
```

### 5. Push ke GitHub

**Untuk Public Repository:**
```bash
# Push ke branch main
git push -u origin main

# Atau jika default branch adalah 'master'
git push -u origin master
```

**Untuk Private Repository:**

Anda perlu **Personal Access Token** (bukan password GitHub):

```bash
# Push
git push -u origin main

# Saat diminta:
Username: your-github-username
Password: ghp_xxxxxxxxxxxxxxxxxxxx (Personal Access Token)
```

### 6. Verify di GitHub

Buka browser: `https://github.com/username/gelis-app`

Pastikan semua file sudah ter-upload! ✅

---

## GitHub Personal Access Token

### Kenapa Perlu Personal Access Token?

GitHub tidak lagi menerima password biasa untuk Git operations. Anda harus menggunakan **Personal Access Token (PAT)**.

### Cara Membuat Personal Access Token

1. **Login ke GitHub**
2. **Buka Settings**:
   - Klik profile picture (kanan atas)
   - Pilih **"Settings"**
3. **Developer Settings**:
   - Scroll ke bawah
   - Klik **"Developer settings"**
4. **Personal Access Tokens**:
   - Klik **"Personal access tokens"**
   - Pilih **"Tokens (classic)"**
5. **Generate Token**:
   - Klik **"Generate new token"** → **"Generate new token (classic)"**
   
   **Form:**
   ```
   Note: GELIS Production Deployment
   Expiration: No expiration (atau 90 days untuk security)
   
   Select scopes:
   ✅ repo (Full control of private repositories)
   ✅ workflow (Update GitHub Action workflows)
   ✅ admin:public_key (untuk SSH key management)
   ```
6. **Generate & Copy Token**:
   - Klik **"Generate token"**
   - Copy token: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   
   ⚠️ **PENTING**: Token ini HANYA ditampilkan SEKALI! Simpan di tempat aman!

### Simpan Token di Git Credential Manager

Agar tidak perlu input token setiap kali:

**Linux/macOS:**
```bash
# Setup credential helper
git config --global credential.helper store

# Saat pertama kali push/pull, input:
Username: your-username
Password: ghp_xxxxxxxxxx (token)

# Token akan tersimpan di ~/.git-credentials
```

**Windows:**
```bash
# Git for Windows sudah include Git Credential Manager
# Token otomatis tersimpan setelah pertama kali input
```

### Clone dengan Token di URL (Alternative)

```bash
# Format
git clone https://TOKEN@github.com/username/repo.git

# Contoh
git clone https://ghp_xxxxxxxxxxxx@github.com/johndoe/gelis-app.git
```

---

## Clone Repository di Server

### 1. Setup SSH Key (Recommended untuk Production)

SSH key lebih aman daripada token:

```bash
# Login ke server
ssh user@your-server-ip

# Switch ke application user
sudo su - gelis

# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Press Enter untuk default location: /home/gelis/.ssh/id_ed25519
# Set passphrase (optional tapi recommended)

# Copy public key
cat ~/.ssh/id_ed25519.pub
```

**Add SSH Key ke GitHub:**

1. Copy output dari command di atas
2. Buka GitHub: https://github.com/settings/keys
3. Klik **"New SSH key"**
   ```
   Title: GELIS Production Server
   Key type: Authentication Key
   Key: ssh-ed25519 AAAAC3NzaC1... your_email@example.com
   ```
4. Klik **"Add SSH key"**

**Test SSH Connection:**
```bash
ssh -T git@github.com
# Output: Hi username! You've successfully authenticated...
```

### 2. Clone Repository

**With SSH (Recommended):**
```bash
cd /home/gelis
git clone git@github.com:username/gelis-app.git app
```

**With HTTPS + Token:**
```bash
cd /home/gelis
git clone https://TOKEN@github.com/username/gelis-app.git app
```

**Clone Specific Branch:**
```bash
git clone -b production git@github.com:username/gelis-app.git app
```

### 3. Verify Clone

```bash
cd /home/gelis/app

# Check files
ls -la

# Check git remote
git remote -v

# Check current branch
git branch
```

---

## Update & Deploy dari GitHub

### 1. Pull Latest Changes

```bash
# Login ke server
ssh user@server-ip

# Switch ke app user
sudo su - gelis
cd /home/gelis/app

# Check current status
git status

# Check what will be updated
git fetch origin
git log HEAD..origin/main --oneline

# Pull latest changes
git pull origin main
```

### 2. Update Backend

```bash
cd /home/gelis/app/backend

# Activate virtual environment
source venv/bin/activate

# Update dependencies (jika ada perubahan)
pip install -r requirements.txt

# Run migrations (jika ada)
# python scripts/migration.py
```

### 3. Update Frontend

```bash
cd /home/gelis/app/frontend

# Install new dependencies
yarn install

# Rebuild production
yarn build
```

### 4. Restart Services

```bash
# Exit dari user gelis
exit

# Restart backend
sudo supervisorctl restart gelis-backend

# Reload nginx (untuk static files baru)
sudo systemctl reload nginx

# Verify
sudo supervisorctl status
```

### 5. Auto-Deploy Script

Buat script untuk automate process:

```bash
sudo nano /home/gelis/deploy.sh
```

```bash
#!/bin/bash
set -e

echo "🚀 Deploying GELIS from GitHub..."

cd /home/gelis/app

# Backup .env files
cp backend/.env backend/.env.backup
cp frontend/.env.production frontend/.env.production.backup

# Pull latest code
git stash
git pull origin main

# Restore .env files
cp backend/.env.backup backend/.env
cp frontend/.env.production.backup frontend/.env.production

# Backend update
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend update
cd ../frontend
yarn install
yarn build

# Restart services
cd ..
sudo supervisorctl restart gelis-backend
sudo systemctl reload nginx

echo "✅ Deployment complete!"
sudo supervisorctl status gelis-backend
```

Make executable:
```bash
sudo chmod +x /home/gelis/deploy.sh

# Run deployment
sudo /home/gelis/deploy.sh
```

---

## Git Workflow untuk Tim

### Branch Strategy

```
main (production)
├── develop (staging)
│   ├── feature/user-authentication
│   ├── feature/payment-integration
│   └── fix/login-bug
```

### 1. Create Feature Branch

```bash
# Update main
git checkout main
git pull origin main

# Create new branch
git checkout -b feature/new-feature

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "Add new feature: description"

# Push to GitHub
git push origin feature/new-feature
```

### 2. Create Pull Request

1. Buka GitHub repository
2. Klik **"Pull requests"** → **"New pull request"**
3. Base: `main` ← Compare: `feature/new-feature`
4. Tambahkan description
5. Request review dari team member
6. Klik **"Create pull request"**

### 3. Code Review & Merge

1. Team member review code
2. Fix issues (jika ada)
3. Approve PR
4. Merge ke `main`

### 4. Deploy ke Production

```bash
# Di server
cd /home/gelis/app
git checkout main
git pull origin main
sudo /home/gelis/deploy.sh
```

### Common Git Commands

```bash
# Check status
git status

# Check commit history
git log --oneline -10

# Check differences
git diff

# Discard local changes
git checkout -- file.txt
git reset --hard HEAD

# Switch branch
git checkout branch-name

# Create & switch
git checkout -b new-branch

# Delete branch
git branch -d branch-name

# Update from remote
git fetch origin
git pull origin main

# Push changes
git add .
git commit -m "message"
git push origin branch-name

# Merge branch
git checkout main
git merge feature-branch

# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## Troubleshooting

### Error: Authentication Failed

**Problem:** `fatal: Authentication failed`

**Solution:**
```bash
# Option 1: Use Personal Access Token
git remote set-url origin https://TOKEN@github.com/user/repo.git

# Option 2: Setup SSH key
ssh-keygen -t ed25519 -C "email@example.com"
# Add to GitHub: https://github.com/settings/keys
git remote set-url origin git@github.com:user/repo.git
```

### Error: Permission Denied (publickey)

**Problem:** `Permission denied (publickey)`

**Solution:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "email@example.com"

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub settings
```

### Error: Repository Not Found

**Problem:** `fatal: repository 'https://github.com/user/repo.git' not found`

**Causes & Solutions:**
1. **Typo di URL**: Check spelling
2. **Private repo tanpa token**: Add token to URL
3. **No access**: Check repository permissions

### Error: Conflicts When Pulling

**Problem:** `CONFLICT (content): Merge conflict in file.txt`

**Solution:**
```bash
# Option 1: Stash local changes
git stash
git pull origin main
git stash pop

# Option 2: Discard local changes
git reset --hard HEAD
git pull origin main

# Option 3: Resolve manually
# Edit file, remove conflict markers
git add file.txt
git commit -m "Resolve merge conflict"
```

### Error: Refusing to Merge Unrelated Histories

**Problem:** `fatal: refusing to merge unrelated histories`

**Solution:**
```bash
git pull origin main --allow-unrelated-histories
```

### Reset Git Credentials

```bash
# Remove saved credentials
rm ~/.git-credentials

# Or for specific repo
cd /path/to/repo
git config --unset credential.helper

# Next push will ask for credentials again
```

### Check Remote URL

```bash
# Show current remote
git remote -v

# Change remote URL
git remote set-url origin NEW_URL

# Example with token
git remote set-url origin https://TOKEN@github.com/user/repo.git

# Example with SSH
git remote set-url origin git@github.com:user/repo.git
```

---

## 📚 Resources

### Official Documentation
- **Git Documentation**: https://git-scm.com/doc
- **GitHub Docs**: https://docs.github.com/
- **GitHub CLI**: https://cli.github.com/

### Interactive Tutorials
- **Learn Git Branching**: https://learngitbranching.js.org/
- **GitHub Skills**: https://skills.github.com/
- **Git Exercises**: https://gitexercises.fracz.com/

### Cheat Sheets
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub Flow**: https://guides.github.com/introduction/flow/

### Video Tutorials
- **Git & GitHub for Beginners**: https://www.youtube.com/watch?v=RGOj5yH7evk
- **Advanced Git**: https://www.youtube.com/watch?v=qsTthZi23VE

---

## ✅ Checklist

### Setup GitHub (First Time)
- [ ] Create GitHub account
- [ ] Install Git di local machine
- [ ] Configure Git user & email
- [ ] Generate SSH key
- [ ] Add SSH key to GitHub
- [ ] Test SSH connection
- [ ] Create repository
- [ ] Push initial code

### Deploy ke Server (First Time)
- [ ] Setup SSH key di server
- [ ] Add server SSH key to GitHub
- [ ] Clone repository to server
- [ ] Create deployment script
- [ ] Test deployment

### Regular Workflow
- [ ] Pull latest changes
- [ ] Create feature branch
- [ ] Make changes & commit
- [ ] Push to GitHub
- [ ] Create pull request
- [ ] Code review
- [ ] Merge to main
- [ ] Deploy to production
- [ ] Test production

---

**Happy Coding! 🎉**

*Last Updated: December 2024*
