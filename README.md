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

### Default Credentials
```
Username: owner
Password: owner123
Role: Owner (full access)
```

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

### ✅ Implemented
1. **Login** - Full authentication dengan JWT
2. **Dashboard** - KPI cards, charts, analytics
3. **Layout** - Sidebar navigation, top bar, responsive

### 🚧 Backend API Ready, UI Placeholder
4. **Bisnis Management** - CRUD businesses
5. **Pesanan (Orders)** - Order management
6. **Transaksi** - Financial transactions
7. **Pengguna (Users)** - User management
8. **Laporan (Reports)** - Reports & exports
9. **Program Loyalitas** - Loyalty program
10. **Program CSR** - CSR initiatives
11. **Log Aktivitas** - Activity logs
12. **Pengaturan (Settings)** - System configuration

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

### Phase 3 - Advanced Features
- File uploads & document management
- Advanced filtering & search
- Bulk operations
- WebSocket real-time updates
- Mobile responsive optimization

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

**Version**: 1.0.0 MVP  
**Last Updated**: December 2024  
**Status**: Core Features Complete, UI Expansion in Progress
