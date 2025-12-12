# GELIS - Gerbang Elektronik Layanan Informasi Sistem

**GELIS** (Gerbang Elektronik Layanan Informasi Sistem) adalah platform terpadu untuk monitoring operasional multi-segmen usaha. Sistem ini bertindak sebagai **gerbang elektronik** yang mengkonsolidasi aliran informasi dari berbagai unit usaha ke dalam satu dashboard terpusat dengan visualisasi real-time.

Sistem monitoring operasional komprehensif untuk mengelola berbagai jenis bisnis (PPOB, PLN Installation, Travel Umroh, PDAM, Inventory, dan Custom Business) dengan fitur keuangan lengkap, RBAC, notifikasi real-time, dan business intelligence.

## 🚀 Fitur Utama

### 1. Multi-Business Management
- ✅ Kelola berbagai jenis bisnis dalam satu sistem
- ✅ Custom fields dinamis per kategori bisnis
- ✅ PPOB (Payment Point Online Bank)
- ✅ Instalasi PLN (NIDI, SLO)
- ✅ Travel Umroh
- ✅ Pencatatan meter PDAM
- ✅ Inventory / Pengadaan barang
- ✅ Custom business module (dapat ditambahkan sesuai kebutuhan)

### 2. Financial Management
- ✅ Transaction ledger dengan filtering advanced
- ✅ Cash position monitoring real-time
- ✅ Income & expense tracking
- ✅ Transfer antar akun
- ✅ Receivables & payables aging reports
- ✅ Monthly P&L by business unit
- ✅ Financial visualization (charts & graphs)

### 3. Order/Work Order Management
- ✅ Create, track, dan manage pesanan
- ✅ Status workflow (pending → processing → completed)
- ✅ Assignment ke teknisi
- ✅ Payment tracking (unpaid → partial → paid)
- ✅ Order history & audit trail

### 4. Role-Based Access Control (RBAC)
**7 User Roles:**
1. **Owner** - Full access ke semua fitur
2. **Manager** - Monitor operasional, approve transaksi
3. **Finance** - Kelola keuangan, payroll, laporan
4. **Customer Service** - Input order, kelola customer
5. **Kasir** - Process pembayaran, cash handling
6. **Loket** - Layani customer walk-in, PPOB
7. **Teknisi** - View assigned work orders, update progress

### 5. Payroll & Commission
- ✅ Process salary dengan komponen (base, overtime, bonus, deductions)
- ✅ Commission tracking berdasarkan sales/order
- ✅ Approval workflow
- ✅ Payment status tracking

### 6. Real-time Notifications
- ✅ In-app notifications dengan badge counter
- ✅ Konfigurasi untuk Email (ready for integration)
- ✅ Konfigurasi untuk WhatsApp/Telegram (ready for integration)
- ✅ Notification rules engine
- ✅ Read/unread status

### 7. Customer Loyalty Program
- ✅ Points system
- ✅ Tier levels (Bronze, Silver, Gold)
- ✅ Rewards & redemption
- ✅ Customer tracking

### 8. CSR Program Management
- ✅ Budget allocation & tracking
- ✅ Beneficiary management
- ✅ Impact reporting
- ✅ Documentation (photo/video)

### 9. Activity Logs & Audit Trail
- ✅ Comprehensive logging semua user actions
- ✅ IP address & device tracking
- ✅ Searchable & filterable
- ✅ 7-year retention untuk compliance

### 10. Dashboard & Analytics
- ✅ Executive dashboard dengan KPI cards
- ✅ Revenue & expense trend charts
- ✅ Business distribution pie chart
- ✅ Real-time data updates
- ✅ Data visualization menggunakan Recharts

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database untuk flexibility
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Bcrypt** - Password hashing

### Frontend
- **React 19** - UI library
- **React Router** - Routing
- **Recharts** - Data visualization
- **Shadcn/UI** - Component library
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Sonner** - Toast notifications
- **Lucide React** - Icons

### Database
- **MongoDB** (Development) - Collections untuk users, businesses, orders, transactions, dll
- **SQL Export Script** - Script untuk migrate ke MySQL/MariaDB

## 📦 Installation & Setup

### 🚀 Quick Start - Pilih Metode Instalasi

**1. Railway + Nixpacks** ⚡ SUPER MUDAH! (NEW!)
- ✅ PALING CEPAT (~20 menit)
- ✅ Zero configuration
- ✅ Auto-deploy dari GitHub
- ✅ Free tier available
- 📚 **[Tutorial Nixpacks →](NIXPACKS_DEPLOYMENT_GUIDE.md)**

**2. Coolify + Nixpacks** 🚀 Mudah!
- ✅ Cepat (~25 menit)
- ✅ Self-hosted
- ✅ Minimal config
- 📚 **[Tutorial Nixpacks →](NIXPACKS_DEPLOYMENT_GUIDE.md)**

**3. Coolify + Docker** 🔧 Flexible
- ✅ Full control (~40 menit)
- ✅ Custom configuration
- 📚 **[Tutorial Coolify Docker →](COOLIFY_DEPLOY_COMPLETE_GUIDE.md)**

**4. Manual Server** 🛠️ Advanced
- ✅ Complete control (2-3 jam)
- ✅ PM2 + Nginx
- 📚 **[Tutorial Manual →](INSTALASI_SERVER.md)**

**Dokumentasi Lainnya:**
- **[QUICK_START.md](QUICK_START.md)** - Quick reference instalasi
- **[MOBILE_RESPONSIVE_GUIDE.md](MOBILE_RESPONSIVE_GUIDE.md)** - Dokumentasi mobile features

### Default Credentials (Setelah Seed Data)
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

### API Endpoints
Backend API: `/api/*`
- Authentication: `/api/auth/*`
- Dashboard: `/api/dashboard/*`
- Business: `/api/businesses`
- Orders: `/api/orders`
- Transactions: `/api/transactions`
- Users: `/api/users`
- Notifications: `/api/notifications`
- Activity Logs: `/api/activity-logs`
- Settings: `/api/settings`

## 🔄 MongoDB to SQL Migration

Untuk migrate data dari MongoDB ke SQL database:

```bash
# Run export script
cd /app/scripts
python3 mongodb_to_sql_export.py

# Output file: /app/scripts/gelis_export.sql

# Import to MySQL/MariaDB
mysql -u username -p database_name < gelis_export.sql
```

Export script akan generate:
- Table CREATE statements dengan proper foreign keys
- INSERT statements untuk semua data
- Proper indexing untuk performance

## 🎨 Design Guidelines

Aplikasi menggunakan **Swiss & High-Contrast** design system:

### Typography
- **Headings**: Outfit (Google Fonts)
- **Body**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono (untuk kode/ID)

### Colors
- **Background**: #F8F9FA (Light Gray)
- **Primary**: #0F172A (Slate 900)
- **Accent**: #2563EB (Royal Blue)
- **Success**: #10B981 (Green)
- **Warning**: #F59E0B (Orange)
- **Danger**: #EF4444 (Red)

## 📱 Pages & Features Status

### ✅ Fully Implemented & Mobile-Optimized
1. **Login** - Full authentication dengan JWT
2. **Dashboard** - KPI cards, charts, analytics (📱 Mobile Responsive)
3. **Layout** - Sidebar navigation, top bar, bottom nav (📱 Mobile Responsive)
4. **Teknisi Dashboard** - Work management untuk teknisi (📱 Mobile Responsive)
5. **Orders Management** - Order tracking & management (📱 Mobile Responsive)

### ✅ Backend + Frontend Complete
6. **Bisnis Management** - CRUD businesses
7. **Transaksi (Accounting)** - Financial transactions dengan filters
8. **Pengguna (Users)** - User management dengan RBAC
9. **Laporan (Reports)** - Daily reports (Loket & Kasir) dengan edit permissions
10. **Program Loyalitas** - Loyalty program tracking
11. **Program CSR** - CSR initiatives management
12. **Log Aktivitas** - Activity logs & audit trail
13. **⭐ Settings (NEW!)** - Complete system configuration
    - Company Profile Settings
    - System & Regional Settings (Timezone, Currency, Language)
    - Notification Settings (Email, WhatsApp, Push)
    - Data Management (Backup, Restore, Clear Mock Data)
    - Security Settings (Session timeout, 2FA, Password policy)

### 📱 Mobile Responsive Features
- ✅ Auto-hide sidebar di mobile (< 768px)
- ✅ Bottom navigation bar (4 menu utama)
- ✅ Horizontal scroll untuk stats cards
- ✅ Touch-friendly buttons (minimum 44x44px)
- ✅ Responsive forms (full-screen di mobile)
- ✅ Adaptive typography & spacing
- ✅ One-hand friendly UI
- ✅ Swipe gestures support
- ✅ Click outside to close sidebar

## 🔔 Notification System

### ✅ In-App Notifications - Working
- Bell icon dengan badge counter
- Notification list
- Mark as read functionality
- Real-time updates

### ⏳ Email/WhatsApp/Telegram - Ready for Integration
- Backend support sudah ada
- Perlu konfigurasi credentials di Settings

## 📊 Database Structure

### Collections (MongoDB)
- `roles` - User roles & permissions
- `users` - System users
- `businesses` - Business entities
- `business_fields` - Dynamic custom fields
- `orders` - Customer orders/work orders
- `transactions` - Financial transactions
- `payroll` - Employee salary records
- `commissions` - Sales commissions
- `notifications` - System notifications
- `activity_logs` - User activity audit trail
- `settings` - System configuration
- `customers` - Customer data

## 🚧 Next Development Phases

### Phase 2 - Complete All UIs
- Business management UI
- Orders UI (create, list, detail, assign)
- Transactions UI (ledger, filters)
- Users management UI
- Reports UI dengan export
- Payroll & Commission UI
- Loyalty & CSR program UI

### Phase 3 - Advanced Features ✅ COMPLETED
- ✅ Mobile responsive optimization (DONE)
- ✅ Touch-friendly UI (44px+ buttons)
- ✅ Adaptive layouts untuk semua devices
- ✅ Bottom navigation untuk mobile
- ✅ Horizontal scroll stats cards
- File uploads & document management (Next)
- Advanced filtering & search (Next)
- Bulk operations (Next)
- WebSocket real-time updates (Next)

### Phase 4 - Integrations
- Payment gateway integration
- Email/WhatsApp notifications
- External API integrations
- Multi-tenant support

## 📈 Performance & Security

- **Async operations** di backend (FastAPI + Motor)
- **JWT-based** authentication
- **Password hashing** dengan bcrypt
- **RBAC** (Role-Based Access Control)
- **Activity logging** untuk audit
- **Indexed** MongoDB collections

## 📄 License

Proprietary - GELIS System © 2024

---

## 📚 Dokumentasi Lengkap

1. **[NIXPACKS_DEPLOYMENT_GUIDE.md](NIXPACKS_DEPLOYMENT_GUIDE.md)** - ⚡ Deploy dengan Nixpacks (NEW!)
   - Railway deployment (EASIEST - 20 menit)
   - Coolify dengan Nixpacks (25 menit)
   - Zero configuration deployment
   - Auto-detect framework
   - 3 metode deployment included

2. **[COOLIFY_DEPLOY_COMPLETE_GUIDE.md](COOLIFY_DEPLOY_COMPLETE_GUIDE.md)** - 🚀 Tutorial SUPER LENGKAP Coolify
   - Panduan DETAIL dari menu Coolify sampai app running
   - 7 PART lengkap: MongoDB → Backend → Frontend → Domain → SSL → Auto-deploy → Testing
   - Screenshot descriptions, form fills, expected outputs
   - Troubleshooting 6 common issues
   - Template Dockerfile included
   - Timeline: ~40 menit total

3. **[DEPLOY_COOLIFY_STEPBYSTEP.md](DEPLOY_COOLIFY_STEPBYSTEP.md)** - Tutorial Praktis Coolify
   - Panduan praktis 11 langkah
   - Timeline estimasi per step
   - Troubleshooting guide
   - Deployment checklist

2. **[INSTALASI_COOLIFY.md](INSTALASI_COOLIFY.md)** - Deploy dengan Coolify (Dokumentasi Lengkap)
   - Setup Coolify di server
   - Deploy dari GitHub dengan 1 klik
   - Auto-deploy & zero-downtime updates
   - Built-in SSL, monitoring, logs
   - Rollback & scaling
   - Troubleshooting Coolify

3. **[INSTALASI_SERVER.md](INSTALASI_SERVER.md)** - Panduan instalasi manual lengkap
   - Setup Ubuntu Server dari nol
   - Install Node.js, Python, MongoDB, Nginx
   - Konfigurasi SSL dengan Let's Encrypt
   - PM2 process management
   - Auto backup MongoDB
   - Troubleshooting guide lengkap

4. **[MOBILE_RESPONSIVE_GUIDE.md](MOBILE_RESPONSIVE_GUIDE.md)** - Dokumentasi fitur mobile responsive
   - Responsive breakpoints
   - Touch-friendly patterns
   - Performance tips
   - Testing guide di mobile
   - Best practices

5. **[QUICK_START.md](QUICK_START.md)** - Quick reference instalasi
   - Pilihan metode instalasi
   - TL;DR installation
   - Command cheat sheet
   - Quick fixes

6. **[MOCK_DATA_GUIDE.md](MOCK_DATA_GUIDE.md)** - Panduan Mock Data (NEW!)
   - 959 data mockup realistic untuk simulasi
   - 14 users, 5 businesses, 345 orders, 404 transactions
   - Clear mock data dengan 1 klik (Owner only)
   - Use cases: Demo, Training, Testing
   - Re-seed script included

---

**Version**: 1.0.0 Production Ready  
**Last Updated**: January 2025  
**Status**: ✅ Core Features Complete, ✅ Mobile Responsive, ✅ Production Ready
