# 🏢 GELIS - Gerbang Elektronik Layanan Informasi Sistem

> **Sistem Manajemen Bisnis Terintegrasi dengan PPOB**  
> FastAPI + React + MongoDB

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)

---

## 📖 Tentang GELIS

**GELIS** (Gerbang Elektronik Layanan Informasi Sistem) adalah platform terpadu untuk monitoring operasional multi-segmen usaha. Sistem ini bertindak sebagai **gerbang elektronik** yang mengkonsolidasi aliran informasi dari berbagai unit usaha ke dalam satu dashboard terpusat dengan visualisasi real-time.

### Fitur Unggulan

- ✅ **Multi-Role Access Control** - 7 role pengguna dengan permission granular
- ✅ **Multi-Business Management** - Kelola berbagai jenis bisnis dalam satu platform
- ✅ **PPOB Integration** - Transaksi pulsa, token listrik, PDAM, dll
- ✅ **Financial Management** - Income, expense, profit tracking dengan analytics
- ✅ **Technician Management** - Assign & track technical jobs
- ✅ **Executive Reports** - Advanced analytics dengan AI-powered insights
- ✅ **Developer Tools** - System monitoring & debugging tools

---

## 🎯 Fitur Lengkap

### 🔐 Role-Based Access Control (RBAC)

Sistem permission granular dengan 7 role berbeda:

| Role | Deskripsi | Akses |
|------|-----------|-------|
| **Owner** | Pemilik bisnis | Full access ke semua fitur |
| **Manager** | Manajer operasional | Kelola bisnis tertentu, monitor tim |
| **Finance** | Tim keuangan | Laporan keuangan & analytics lengkap |
| **Kasir** | Kasir/POS | Transaksi kasir, cash handling |
| **Loket** | Operator loket | PPOB transactions & customer service |
| **Teknisi** | Teknisi lapangan | Technical job management |
| **IT Developer** | IT support | System monitoring & debugging |

### 💼 Business Management

- **Multi-business support** - Kelola unlimited bisnis
- **Per-business accounting** - Laporan keuangan terpisah
- **Business analytics** - Performance tracking per unit
- **Custom fields** - Sesuaikan dengan kebutuhan
- **Category management** - PPOB, PLN, Travel, PDAM, Inventory, Custom

### 💰 Financial Management

- **Income & Expense Tracking** - Catat semua transaksi
- **Profit/Loss Reports** - Laporan laba rugi otomatis
- **Monthly/Yearly Analytics** - Trend analysis
- **Category-Based Reporting** - Laporan per kategori
- **Cash Position** - Monitor saldo real-time
- **Receivables & Payables** - Aging reports
- **Transfer Management** - Transfer antar akun
- **Financial Insights** - AI-powered recommendations

### 🔧 Technician Management

- **Job Assignment System** - Assign jobs ke teknisi
- **Real-time Tracking** - Monitor progress pekerjaan
- **Performance Metrics** - KPI teknisi
- **Job History** - Complete audit trail
- **Status Workflow** - Pending → Processing → Completed

### 📊 Executive Dashboard

- **Financial Trends** - Visualisasi trend pendapatan
- **Revenue Predictions** - Prediksi revenue
- **Strategic Recommendations** - Insight bisnis
- **KPI Monitoring** - Track semua KPI penting
- **Visual Charts** - Grafik interaktif (Recharts)

### 🛠️ Developer Tools

- **System Health Monitoring** - Check status services
- **Real-time Logs Viewer** - Lihat logs langsung
- **Service Status** - Monitor backend/database
- **Performance Metrics** - CPU, memory, disk usage

### 🔔 Order Management

- **Order Creation** - Buat pesanan baru
- **Status Tracking** - Track order status
- **Payment Tracking** - Unpaid → Partial → Paid
- **Assignment to Technician** - Auto-assign atau manual
- **Order History** - Complete history & audit trail

---

## 🚀 Quick Start

### Prerequisites

Pastikan Anda sudah install:

- **Python**: 3.11 atau lebih baru
- **Node.js**: 18.x atau lebih baru  
- **MongoDB**: 6.0 atau lebih baru
- **Yarn**: Package manager (recommended, bukan NPM)

### Installation

#### 1. Clone Repository

```bash
# Clone dari GitHub
git clone https://github.com/YOUR_USERNAME/gelis-app.git
cd gelis-app
```

> 📌 **Note**: Ganti `YOUR_USERNAME` dengan username GitHub Anda

#### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Setup Frontend

```bash
cd ../frontend

# Install dependencies dengan Yarn
yarn install

# JANGAN gunakan npm install!
```

#### 4. Configure Environment Variables

**Backend** (`backend/.env`):
```bash
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017/gelis_db
DB_NAME=gelis_db

# JWT Secret (generate dengan: python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=your_secret_key_here

# Application Settings
ENVIRONMENT=development
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend** (`frontend/.env`):
```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001
```

#### 5. Start MongoDB

```bash
# Linux
sudo systemctl start mongod

# macOS
brew services start mongodb-community

# Windows
net start MongoDB
```

#### 6. Seed Database

```bash
cd backend
source venv/bin/activate
python scripts/verify_roles_and_test.py
```

#### 7. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
```

### Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs (Swagger)**: http://localhost:8001/docs
- **API Docs (ReDoc)**: http://localhost:8001/redoc

### Default Login Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Owner | `owner` | `owner123` | Full access |
| Manager | `manager` | `manager123` | Business management |
| Finance | `finance` | `finance123` | Financial reports |
| Kasir | `kasir1` | `kasir123` | POS transactions |
| Loket | `loket1` | `loket123` | PPOB services |
| Teknisi | `indra` | `teknisi123` | Job management |
| IT Developer | `it` | `it123` | System tools |

⚠️ **PENTING**: Ganti semua password default setelah instalasi pertama!

---

## 📁 Project Structure

```
gelis-app/
├── backend/                    # FastAPI Backend
│   ├── server.py              # Main application
│   ├── models.py              # Pydantic models
│   ├── requirements.txt       # Python dependencies
│   ├── utils/
│   │   ├── auth.py           # Authentication utilities
│   │   └── report_generator.py
│   ├── scripts/
│   │   ├── verify_roles_and_test.py
│   │   ├── create_teknisi_jobs.py
│   │   └── seed_realistic_data.py
│   └── .env                   # Environment config
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.js
│   │   │   ├── OwnerDashboard.js
│   │   │   ├── ManagerDashboard.js
│   │   │   ├── FinanceDashboard.js
│   │   │   ├── KasirDashboard.js
│   │   │   ├── LoketDashboard.js
│   │   │   ├── TeknisiDashboard.js
│   │   │   ├── DeveloperTools.js
│   │   │   ├── ExecutiveReport.js
│   │   │   ├── BusinessManagement.js
│   │   │   ├── OrderManagement.js
│   │   │   ├── IncomeForm.js
│   │   │   ├── ExpenseForm.js
│   │   │   └── ui/
│   │   │       └── currency-input.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json           # Node dependencies
│   └── .env                   # Frontend config
│
├── scripts/                   # Utility scripts
│   └── seed_*.py
│
├── docs/                      # Documentation
│   ├── DEPLOYMENT_GUIDE.md   # Server deployment
│   ├── GITHUB_GUIDE.md       # Git & GitHub tutorial
│   └── CREDENTIALS.md        # User credentials
│
├── install.sh                 # Auto-installation script
├── README.md                  # This file
└── .gitignore
```

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | Latest | Modern Python web framework |
| **Python** | 3.11+ | Programming language |
| **MongoDB** | 6.0+ | NoSQL database |
| **Motor** | Latest | Async MongoDB driver |
| **Pydantic** | v2 | Data validation |
| **JWT** | Latest | Authentication |
| **bcrypt** | 4.1.3 | Password hashing |
| **Uvicorn** | Latest | ASGI server |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18 | UI framework |
| **React Router** | v6 | Routing |
| **Tailwind CSS** | Latest | Styling |
| **Recharts** | Latest | Data visualization |
| **Lucide React** | Latest | Icons |
| **Axios** | Latest | HTTP client |

### DevOps & Tools

- **Nginx** - Reverse proxy
- **Supervisor** - Process manager
- **Certbot** - SSL certificates
- **Git** - Version control
- **GitHub Actions** - CI/CD (coming soon)

---

## 🌐 Deployment

### Deployment ke Ubuntu Server

Ada 2 cara deployment:

#### Opsi 1: Automated Installation (Recommended)

```bash
# Upload script ke server
scp install.sh user@server-ip:/tmp/

# Login ke server
ssh user@server-ip

# Run installation
sudo bash /tmp/install.sh
```

Script akan otomatis:
- ✅ Install semua dependencies
- ✅ Setup MongoDB
- ✅ Clone dari GitHub
- ✅ Configure Nginx
- ✅ Setup SSL (optional)
- ✅ Start services

#### Opsi 2: Manual Installation

Ikuti step-by-step guide lengkap di: **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)**

### GitHub Repository Setup

Untuk deployment dari GitHub, baca tutorial lengkap: **[GITHUB_GUIDE.md](./GITHUB_GUIDE.md)**

Includes:
- Setup GitHub account
- Create repository
- Push code to GitHub
- Generate Personal Access Token
- Clone di server
- Auto-deploy workflow

### Production Checklist

- [ ] Server Ubuntu 20.04/22.04 LTS ready
- [ ] Domain name configured & pointed to server
- [ ] MongoDB installed & secured
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ & Yarn installed
- [ ] Nginx configured as reverse proxy
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Firewall configured (UFW)
- [ ] Supervisor running backend
- [ ] Environment variables set (production values)
- [ ] Database seeded with initial data
- [ ] All default passwords changed
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] GitHub repository created & synced

---

## 📚 Documentation

### Available Guides

| Document | Description |
|----------|-------------|
| **[README.md](./README.md)** | Project overview & quick start (this file) |
| **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** | Complete server deployment guide |
| **[GITHUB_GUIDE.md](./GITHUB_GUIDE.md)** | GitHub setup & Git workflow tutorial |
| **[CREDENTIALS.md](./CREDENTIALS.md)** | User credentials for testing |
| **[API Docs](http://localhost:8001/docs)** | Interactive API documentation (Swagger UI) |

### Quick Links

- **GitHub Repository**: https://github.com/YOUR_USERNAME/gelis-app
- **Issues**: https://github.com/YOUR_USERNAME/gelis-app/issues
- **Releases**: https://github.com/YOUR_USERNAME/gelis-app/releases

---

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/gelis-app.git
cd gelis-app

# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload

# Frontend (terminal baru)
cd frontend
yarn install
yarn start
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes & commit
git add .
git commit -m "Add new feature"

# Push to GitHub
git push origin feature/new-feature

# Create Pull Request di GitHub
```

### Code Quality Tools

```bash
# Python linting
cd backend
pip install flake8 black
flake8 server.py
black server.py --check

# JavaScript linting
cd frontend
yarn lint
yarn format
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
pytest --cov=.
```

### Frontend Tests

```bash
cd frontend
yarn test
yarn test --coverage
```

### Manual Testing

Test dengan credentials di atas untuk setiap role:
1. Login dengan credentials
2. Verify dashboard sesuai role
3. Test CRUD operations
4. Check permissions

---

## 🤝 Contributing

Kontribusi sangat diterima! Follow langkah berikut:

### 1. Fork Repository

Klik tombol **Fork** di GitHub

### 2. Clone Fork Anda

```bash
git clone https://github.com/YOUR_USERNAME/gelis-app.git
cd gelis-app
```

### 3. Create Feature Branch

```bash
git checkout -b feature/amazing-feature
```

### 4. Make Changes

Edit code, add features, fix bugs

### 5. Commit Changes

```bash
git add .
git commit -m "Add amazing feature

- Feature description
- Why it's needed
- How it works"
```

### 6. Push to GitHub

```bash
git push origin feature/amazing-feature
```

### 7. Create Pull Request

1. Buka repository di GitHub
2. Klik **"Pull requests"** → **"New pull request"**
3. Pilih branch Anda
4. Isi description lengkap
5. Submit PR

### Contribution Guidelines

- ✅ Follow existing code style
- ✅ Write meaningful commit messages
- ✅ Add tests for new features
- ✅ Update documentation
- ✅ Ensure all tests pass
- ✅ One feature per PR

---

## 🐛 Bug Reports & Feature Requests

### Report Bug

Buat issue di GitHub dengan informasi:

- **Title**: Clear & descriptive
- **Description**: Detailed bug description
- **Steps to Reproduce**: 
  1. Step 1
  2. Step 2
  3. ...
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**:
  - OS: Ubuntu 22.04
  - Python: 3.11.5
  - Node: 18.17.0
  - Browser: Chrome 120
- **Screenshots**: If applicable
- **Logs**: Backend/frontend error logs

### Request Feature

Create issue dengan:

- **Feature Description**: Clear description
- **Use Case**: Why you need it
- **Proposed Solution**: How it could work
- **Alternatives**: Other solutions considered
- **Additional Context**: Any other info

---

## 📝 Changelog

### Version 1.0.0 (December 2024)

#### ✨ Added
- Complete RBAC system with 7 user roles
- Multi-business management system
- PPOB transaction integration
- Financial tracking & reporting
- Technician job assignment & tracking
- Executive dashboard with AI insights
- Developer tools for monitoring
- Advanced currency input component
- Deployment automation script
- Comprehensive documentation

#### 🐛 Fixed
- bcrypt version compatibility (downgraded to 4.1.3)
- Pydantic v2 validation errors
- Frontend authorization race condition
- MongoDB ObjectId serialization issues
- Technician dashboard data synchronization
- Executive report 500 errors

#### 🔧 Changed
- Enhanced executive report with smart analytics
- Improved frontend authorization with RoleBasedRoute
- Optimized MongoDB queries (exclude _id)
- Better error handling across endpoints
- Upgraded UI components

#### 🗑️ Removed
- Hardcoded demo credentials from Login component
- Unused deprecated code

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 GELIS Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👥 Team

### Core Contributors

- **GELIS Development Team** - Initial development & maintenance

### Special Thanks

- FastAPI community
- React team
- MongoDB team
- All contributors

---

## 🙏 Acknowledgments

Terima kasih kepada:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[React](https://react.dev/)** - UI library
- **[MongoDB](https://www.mongodb.com/)** - NoSQL database
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS
- **[Recharts](https://recharts.org/)** - Charting library
- **[Lucide](https://lucide.dev/)** - Icon set
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server

---

## 📞 Support

Butuh bantuan?

### Documentation
- 📖 [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- 🐙 [GitHub Guide](./GITHUB_GUIDE.md)
- 🔑 [Credentials](./CREDENTIALS.md)
- 📚 [API Docs](http://localhost:8001/docs)

### Community
- 💬 **GitHub Issues**: [Report bugs & request features](https://github.com/YOUR_USERNAME/gelis-app/issues)
- 📧 **Email**: support@gelis-app.com
- 💼 **LinkedIn**: [GELIS Official](https://linkedin.com/company/gelis)
- 🐦 **Twitter**: [@GelisApp](https://twitter.com/gelisapp)

---

## 🔗 Useful Links

### Project
- **GitHub**: https://github.com/YOUR_USERNAME/gelis-app
- **Live Demo**: https://demo.gelis-app.com (coming soon)
- **Documentation**: https://docs.gelis-app.com (coming soon)

### Resources
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **MongoDB Docs**: https://docs.mongodb.com/
- **Tailwind Docs**: https://tailwindcss.com/docs
- **GitHub Docs**: https://docs.github.com/

---

## 🎯 Roadmap

### Q1 2025
- [ ] Mobile app (React Native)
- [ ] Push notifications
- [ ] Email notifications system
- [ ] SMS integration (Twilio)
- [ ] Multi-language support (EN, ID)
- [ ] Dark mode

### Q2 2025
- [ ] Payment gateway (Stripe, PayPal, Midtrans)
- [ ] Automated database backups
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Performance optimization
- [ ] Unit test coverage 80%+
- [ ] E2E tests with Playwright

### Q3 2025
- [ ] Advanced analytics & ML predictions
- [ ] API rate limiting
- [ ] Customer portal
- [ ] CRM integration
- [ ] Inventory management module
- [ ] HR & Payroll enhancements

### Q4 2025
- [ ] Mobile POS app
- [ ] Offline mode support
- [ ] Advanced security (2FA, OTP)
- [ ] Audit logging system
- [ ] Data export/import tools
- [ ] White-label solution

---

## ⭐ Star History

Jika project ini bermanfaat, please give it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/gelis-app&type=Date)](https://star-history.com/#YOUR_USERNAME/gelis-app&Date)

---

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/gelis-app?style=social)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/gelis-app?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/YOUR_USERNAME/gelis-app?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/gelis-app)
![GitHub repo size](https://img.shields.io/github/repo-size/YOUR_USERNAME/gelis-app)

---

**Made with ❤️ by GELIS Development Team**

*Empowering businesses with smart management solutions*

---

> 📌 **Quick Links:**  
> [Installation](#installation) • [Features](#-fitur-lengkap) • [Deployment](./DEPLOYMENT_GUIDE.md) • [GitHub Setup](./GITHUB_GUIDE.md) • [Contributing](#-contributing) • [License](#-license)

*Last Updated: December 2024 • Version 1.0.0*
