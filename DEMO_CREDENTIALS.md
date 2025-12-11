# GELIS - Demo User Credentials

## 🎯 Tentang GELIS

**GELIS** (Gerbang Elektronik Layanan Informasi Sistem) adalah platform terpadu untuk monitoring operasional multi-segmen usaha. Sistem ini bertindak sebagai gerbang elektronik yang mengkonsolidasi aliran informasi dari berbagai unit usaha (PPOB, PLN, Travel Umroh, PDAM, Inventory) ke dalam satu dashboard terpusat dengan visualisasi real-time.

📖 **Baca lebih lengkap:** `/app/ABOUT_GELIS.md`

---

## 🔐 User Accounts

Semua password menggunakan format: `{username}123`

### 1. Owner (Full Access)
```
Username: owner
Password: owner123
Role: Owner
Access: Full system access
```

**Capabilities:**
- ✅ Manage all businesses
- ✅ Create/update/delete users
- ✅ Approve all transactions
- ✅ View all reports
- ✅ System configuration
- ✅ Activity logs monitoring

---

### 2. Manager (Operational Management)
```
Username: manager
Password: manager123
Role: Manager
Access: Monitor & manage operations
```

**Capabilities:**
- ✅ View all businesses
- ✅ Manage orders
- ✅ Approve transactions (with limits)
- ✅ View comprehensive reports
- ✅ Assign work to technicians
- ❌ Cannot add/delete users
- ❌ Cannot access system configuration

---

### 3. Finance (Financial Management)
```
Username: finance
Password: finance123
Role: Finance
Access: Financial operations & reporting
```

**Capabilities:**
- ✅ Access all financial data
- ✅ Generate financial reports
- ✅ Process transactions
- ✅ Manage payroll
- ✅ Bank reconciliation
- ❌ Cannot manage users
- ❌ Cannot approve budget changes

---

### 4. Customer Service
```
Username: cs1
Password: cs123
Role: Customer Service
Access: Customer & order management
```

**Capabilities:**
- ✅ Create new orders
- ✅ Update customer information
- ✅ Check order status
- ✅ Generate quotations
- ❌ Cannot process payments
- ❌ Cannot view financial reports

---

### 5. Kasir (Cashier)
```
Username: kasir
Password: kasir123
Role: Kasir
Access: Payment processing
```

**Capabilities:**
- ✅ Process all payments
- ✅ Generate receipts
- ✅ Daily cash reconciliation
- ✅ View daily sales summary
- ❌ Cannot edit transactions
- ❌ Cannot approve large refunds

---

### 6. Loket (Front Office)
```
Username: loket
Password: loket123
Role: Loket
Access: Counter services (PPOB, payments)
```

**Capabilities:**
- ✅ Process PPOB transactions
- ✅ Receive customer payments
- ✅ Print receipts
- ✅ Check customer balance
- ❌ Cannot process refunds
- ❌ Cannot view total revenue

---

### 7. Teknisi 1 (Field Technician)
```
Username: teknisi1
Password: teknisi123
Role: Teknisi
Access: Work order management
```

**Capabilities:**
- ✅ View assigned work orders
- ✅ Update job status
- ✅ Upload progress documentation
- ✅ Complete job reports
- ❌ Can only see assigned jobs
- ❌ Cannot view pricing details

---

### 8. Teknisi 2 (Field Technician)
```
Username: teknisi2
Password: teknisi123
Role: Teknisi
Access: Work order management
```

**Capabilities:**
- ✅ View assigned work orders
- ✅ Update job status
- ✅ Upload progress documentation
- ✅ Complete job reports
- ❌ Can only see assigned jobs
- ❌ Cannot view pricing details

---

## 📊 Mock Data Summary

### Businesses (7 total)
1. **Loket PPOB Pusat** (PPOB)
2. **Instalasi PLN Mandiri** (PLN)
3. **Travel Umroh Berkah** (Travel)
4. **Layanan PDAM** (PDAM)
5. **Toko Serbaguna** (Inventory)
6. Plus 2 demo businesses from initial setup

### Orders (50 total)
- **Status Distribution:**
  - Pending: ~8 orders
  - Processing: ~9 orders
  - Completed: ~33 orders
- **Date Range:** Last 3 months
- **Total Revenue:** Rp 305+ Million

### Transactions (64 total)
- **Income Transactions:** From paid orders
- **Expense Transactions:** Gaji, Operasional, Utilities, etc.
- **Categories:** Sales, Salaries, Operations, Marketing, Transport, Supplies

### Customers (10 total)
- Budi Santoso, Siti Aminah, Ahmad Yani
- Dewi Lestari, Rudi Hartono, Linda Wijaya
- Joko Widodo, Sri Mulyani, Bambang Susilo, Rina Setiawan

### Notifications (20 total)
- Various types: info, success, warning
- Mix of read/unread status
- Date range: Last 30 days

---

## 🎯 Testing Scenarios

### Scenario 1: Create New Order (as CS)
1. Login with `cs1 / cs123`
2. Go to "Pesanan" page
3. Click "Buat Pesanan"
4. Fill order details
5. Submit order
6. Verify notification sent to manager

### Scenario 2: Process Payment (as Kasir)
1. Login with `kasir / kasir123`
2. Go to "Pesanan" page
3. Find pending payment order
4. Click "Update"
5. Update payment status
6. Verify receipt generated

### Scenario 3: Assign Work (as Manager)
1. Login with `manager / manager123`
2. Go to "Pesanan" page
3. Find pending order
4. Click "Update"
5. Assign to teknisi1 or teknisi2
6. Verify notification sent to technician

### Scenario 4: View Financial Reports (as Finance)
1. Login with `finance / finance123`
2. Go to "Dashboard"
3. View revenue trends
4. Check business distribution
5. Export reports (when available)

### Scenario 5: Monitor Activity (as Owner)
1. Login with `owner / owner123`
2. Go to "Log Aktivitas"
3. Filter by user or action
4. View detailed audit trail
5. Check security logs

---

## 🔄 Re-generate Mock Data

To regenerate mock data:

```bash
cd /app/scripts
python3 generate_mock_data.py
```

This will:
- ✅ Create 7 demo users (all roles)
- ✅ Create 5 businesses
- ✅ Create 10 customers
- ✅ Generate 50 orders
- ✅ Generate 64 transactions
- ✅ Create 20 notifications

---

## 📝 Notes

- All passwords are for **DEMO purposes only**
- Change passwords before production deployment
- Mock data is randomly generated
- Financial amounts are realistic ranges:
  - PPOB: Rp 50,000 - 2,000,000
  - PLN Installation: Rp 5,000,000 - 15,000,000
  - Travel Umroh: Rp 20,000,000 - 35,000,000
  - PDAM: Rp 50,000 - 2,000,000
  - Inventory: Rp 50,000 - 2,000,000

---

**Version:** 1.0.0  
**Last Updated:** December 2024
