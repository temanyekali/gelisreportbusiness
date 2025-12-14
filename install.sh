#!/bin/bash

################################################################################
# GELIS Auto Installation Script for Ubuntu Server
# 
# This script automates the installation of GELIS on Ubuntu 20.04/22.04 LTS
# Stack: FastAPI (Python) + React + MongoDB
#
# Usage: sudo bash install.sh
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use: sudo bash install.sh)"
    exit 1
fi

echo "=================================================="
echo "  GELIS Auto Installation Script"
echo "  Ubuntu 20.04/22.04 LTS"
echo "=================================================="
echo ""

# Get configuration from user
read -p "Enter application user name [gelis]: " APP_USER
APP_USER=${APP_USER:-gelis}

read -p "Enter domain name (e.g., example.com) [localhost]: " DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-localhost}

read -p "Enter MongoDB password for 'gelis_user': " DB_PASSWORD
while [ -z "$DB_PASSWORD" ]; do
    log_error "Password cannot be empty!"
    read -p "Enter MongoDB password for 'gelis_user': " DB_PASSWORD
done

echo ""
log_info "GitHub Repository Setup:"
read -p "Clone from GitHub? (y/n) [y]: " USE_GITHUB
USE_GITHUB=${USE_GITHUB:-y}

if [ "$USE_GITHUB" = "y" ]; then
    read -p "Enter GitHub repository URL (e.g., https://github.com/user/repo.git): " GITHUB_REPO
    while [ -z "$GITHUB_REPO" ]; do
        log_error "Repository URL cannot be empty!"
        read -p "Enter GitHub repository URL: " GITHUB_REPO
    done
    
    read -p "Is this a private repository? (y/n) [n]: " IS_PRIVATE
    IS_PRIVATE=${IS_PRIVATE:-n}
    
    if [ "$IS_PRIVATE" = "y" ]; then
        read -p "Enter GitHub Personal Access Token: " GITHUB_TOKEN
        while [ -z "$GITHUB_TOKEN" ]; do
            log_error "Token cannot be empty for private repository!"
            read -p "Enter GitHub Personal Access Token: " GITHUB_TOKEN
        done
    fi
    
    read -p "Enter branch name [main]: " GITHUB_BRANCH
    GITHUB_BRANCH=${GITHUB_BRANCH:-main}
fi

read -p "Install SSL certificate? (y/n) [n]: " INSTALL_SSL
INSTALL_SSL=${INSTALL_SSL:-n}

echo ""
log_info "Configuration Summary:"
log_info "  - App User: $APP_USER"
log_info "  - Domain: $DOMAIN_NAME"
if [ "$USE_GITHUB" = "y" ]; then
    log_info "  - GitHub Repo: $GITHUB_REPO"
    log_info "  - Branch: $GITHUB_BRANCH"
    log_info "  - Private: $IS_PRIVATE"
fi
log_info "  - Install SSL: $INSTALL_SSL"
echo ""

read -p "Continue with installation? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    log_warning "Installation cancelled"
    exit 0
fi

################################################################################
# Step 1: Update System
################################################################################
log_info "Step 1: Updating system..."
apt update -qq
apt upgrade -y -qq
apt install -y build-essential software-properties-common curl wget git ufw
log_success "System updated"

################################################################################
# Step 2: Create Application User
################################################################################
log_info "Step 2: Creating application user..."
if id "$APP_USER" &>/dev/null; then
    log_warning "User $APP_USER already exists"
else
    adduser $APP_USER --disabled-password --gecos ""
    log_success "User $APP_USER created"
fi

################################################################################
# Step 3: Install Python 3.11
################################################################################
log_info "Step 3: Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt update -qq
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
log_success "Python 3.11 installed: $(python3.11 --version)"

################################################################################
# Step 4: Install Node.js & Yarn
################################################################################
log_info "Step 4: Installing Node.js 18 & Yarn..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - > /dev/null 2>&1
apt install -y nodejs
npm install -g yarn
log_success "Node.js installed: $(node --version)"
log_success "Yarn installed: $(yarn --version)"

################################################################################
# Step 5: Install MongoDB
################################################################################
log_info "Step 5: Installing MongoDB 6.0..."
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | \
    tee /etc/apt/sources.list.d/mongodb-org-6.0.list

apt update -qq
apt install -y mongodb-org
systemctl start mongod
systemctl enable mongod
log_success "MongoDB installed and started"

################################################################################
# Step 6: Install Nginx & Supervisor
################################################################################
log_info "Step 6: Installing Nginx & Supervisor..."
apt install -y nginx supervisor
systemctl enable nginx
systemctl enable supervisor
log_success "Nginx and Supervisor installed"

################################################################################
# Step 7: Setup MongoDB Database
################################################################################
log_info "Step 7: Configuring MongoDB..."

# Wait for MongoDB to be ready
sleep 3

# Create database and user
mongosh --quiet --eval "
use gelis_db
db.createUser({
  user: 'gelis_user',
  pwd: '$DB_PASSWORD',
  roles: [ { role: 'readWrite', db: 'gelis_db' } ]
})
print('MongoDB user created successfully')
"

log_success "MongoDB configured"

################################################################################
# Step 8: Setup Application Directory
################################################################################
log_info "Step 8: Setting up application directory..."

APP_DIR="/home/$APP_USER/app"

if [ "$USE_GITHUB" = "y" ]; then
    log_info "Cloning from GitHub repository..."
    
    # Switch to application user
    if [ "$IS_PRIVATE" = "y" ]; then
        # Clone private repository with token
        REPO_WITH_TOKEN=$(echo "$GITHUB_REPO" | sed "s|https://|https://$GITHUB_TOKEN@|")
        sudo -u $APP_USER git clone -b $GITHUB_BRANCH $REPO_WITH_TOKEN $APP_DIR
    else
        # Clone public repository
        sudo -u $APP_USER git clone -b $GITHUB_BRANCH $GITHUB_REPO $APP_DIR
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Repository cloned successfully from $GITHUB_REPO"
    else
        log_error "Failed to clone repository. Please check:"
        log_error "  1. Repository URL is correct"
        log_error "  2. Branch '$GITHUB_BRANCH' exists"
        log_error "  3. Access token is valid (for private repos)"
        exit 1
    fi
    
elif [ -d "/app" ]; then
    # Check if running in /app (Emergent environment)
    log_info "Detected Emergent environment, copying from /app..."
    mkdir -p $APP_DIR
    cp -r /app/* $APP_DIR/
    log_success "Application copied from /app"
else
    log_error "No application source found!"
    log_error "Please either:"
    log_error "  1. Re-run with GitHub repository option"
    log_error "  2. Or manually upload code to $APP_DIR"
    exit 1
fi

chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
log_success "Application directory ready: $APP_DIR"

# Verify directory structure
if [ ! -d "$APP_DIR/backend" ] || [ ! -d "$APP_DIR/frontend" ]; then
    log_error "Invalid application structure!"
    log_error "Expected directories 'backend' and 'frontend' not found in $APP_DIR"
    exit 1
fi

log_success "Application structure verified"

################################################################################
# Step 9: Setup Backend
################################################################################
log_info "Step 9: Setting up backend..."

cd $APP_DIR/backend

# Create virtual environment
sudo -u $APP_USER python3.11 -m venv venv
log_info "Virtual environment created"

# Install dependencies
sudo -u $APP_USER $APP_DIR/backend/venv/bin/pip install --upgrade pip -qq
sudo -u $APP_USER $APP_DIR/backend/venv/bin/pip install -r requirements.txt -qq
log_success "Backend dependencies installed"

# Create .env file
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

cat > $APP_DIR/backend/.env <<EOF
MONGO_URL=mongodb://gelis_user:$DB_PASSWORD@localhost:27017/gelis_db?authSource=gelis_db
DB_NAME=gelis_db
JWT_SECRET_KEY=$JWT_SECRET
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME
EOF

chown $APP_USER:$APP_USER $APP_DIR/backend/.env
log_success "Backend .env configured"

################################################################################
# Step 10: Setup Frontend
################################################################################
log_info "Step 10: Setting up frontend..."

cd $APP_DIR/frontend

# Create production .env
cat > $APP_DIR/frontend/.env.production <<EOF
REACT_APP_BACKEND_URL=https://$DOMAIN_NAME
EOF

chown $APP_USER:$APP_USER $APP_DIR/frontend/.env.production

# Install dependencies & build
log_info "Installing frontend dependencies (this may take 5-10 minutes)..."
sudo -u $APP_USER yarn install > /dev/null 2>&1

log_info "Building frontend (this may take 3-5 minutes)..."
sudo -u $APP_USER yarn build > /dev/null 2>&1

log_success "Frontend built successfully"

################################################################################
# Step 11: Setup Supervisor
################################################################################
log_info "Step 11: Configuring Supervisor..."

# Backend config
cat > /etc/supervisor/conf.d/gelis-backend.conf <<EOF
[program:gelis-backend]
command=$APP_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4
directory=$APP_DIR/backend
user=$APP_USER
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/gelis-backend.err.log
stdout_logfile=/var/log/supervisor/gelis-backend.out.log
environment=PYTHONUNBUFFERED=1
EOF

supervisorctl reread
supervisorctl update
supervisorctl start gelis-backend

log_success "Supervisor configured and services started"

################################################################################
# Step 12: Setup Nginx
################################################################################
log_info "Step 12: Configuring Nginx..."

cat > /etc/nginx/sites-available/gelis <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;

    # Frontend
    location / {
        root $APP_DIR/frontend/build;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    client_max_body_size 50M;
    
    access_log /var/log/nginx/gelis_access.log;
    error_log /var/log/nginx/gelis_error.log;
}
EOF

ln -sf /etc/nginx/sites-available/gelis /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl reload nginx

log_success "Nginx configured"

################################################################################
# Step 13: Setup Firewall
################################################################################
log_info "Step 13: Configuring firewall..."

ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

log_success "Firewall configured"

################################################################################
# Step 14: Install SSL (Optional)
################################################################################
if [ "$INSTALL_SSL" = "y" ]; then
    log_info "Step 14: Installing SSL certificate..."
    
    apt install -y certbot python3-certbot-nginx
    
    log_warning "To complete SSL setup, run:"
    log_warning "  sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME"
    
else
    log_info "Step 14: Skipping SSL installation"
fi

################################################################################
# Step 15: Seed Database (Optional)
################################################################################
log_info "Step 15: Seeding database with initial data..."

cd $APP_DIR/backend
sudo -u $APP_USER $APP_DIR/backend/venv/bin/python3 scripts/verify_roles_and_test.py

log_success "Database seeded"

################################################################################
# Installation Complete
################################################################################

echo ""
echo "=================================================="
echo "  Installation Complete! 🎉"
echo "=================================================="
echo ""
log_success "GELIS has been successfully installed!"
echo ""
log_info "Access your application:"
if [ "$INSTALL_SSL" = "y" ]; then
    log_info "  URL: https://$DOMAIN_NAME"
else
    log_info "  URL: http://$DOMAIN_NAME"
fi
echo ""
log_info "Default credentials:"
log_info "  Owner:        owner / owner123"
log_info "  Manager:      manager / manager123"
log_info "  Finance:      finance / finance123"
log_info "  IT Developer: it / it123"
echo ""
log_info "Service management:"
log_info "  Backend:  sudo supervisorctl status gelis-backend"
log_info "  Nginx:    sudo systemctl status nginx"
log_info "  MongoDB:  sudo systemctl status mongod"
echo ""
log_info "Logs location:"
log_info "  Backend:  /var/log/supervisor/gelis-backend.err.log"
log_info "  Nginx:    /var/log/nginx/gelis_error.log"
echo ""
log_warning "IMPORTANT: Change default passwords after first login!"
echo ""
log_info "Documentation: $APP_DIR/DEPLOYMENT_GUIDE.md"
echo ""
echo "=================================================="

# Test backend
sleep 2
if curl -s http://localhost:8001/api/health > /dev/null; then
    log_success "Backend is running!"
else
    log_error "Backend is not responding. Check logs:"
    log_error "  sudo tail -f /var/log/supervisor/gelis-backend.err.log"
fi

echo ""
log_info "Installation script completed!"
