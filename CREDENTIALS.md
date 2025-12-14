# 🔐 GELIS - Credentials & Role Documentation

> **IMPORTANT**: This file contains sensitive credentials. Keep it secure and DO NOT commit to public repositories.

---

## 📋 Daftar Role di Sistem

| Role ID | Nama Role | Deskripsi | Akses Level |
|---------|-----------|-----------|-------------|
| **1** | Owner | Pemilik sistem dengan akses penuh | Full Access |
| **2** | Manager | Manajer operasional | High Access |
| **3** | Finance | Staff keuangan | Finance Access |
| **4** | Customer Service | Customer Service | Limited Access |
| **5** | Kasir | Kasir | Operational Access |
| **6** | Loket | Petugas Loket | Operational Access |
| **7** | Teknisi | Teknisi Lapangan | Job-specific Access |

---

## 👥 User Accounts (Default)

### 🔹 Role ID: 1 - Owner
```
Username: owner
Password: owner123
Email:    owner@gelis.com
Name:     Owner GELIS
Status:   ✅ Active
```

**Access Rights:**
- ✅ Full system access
- ✅ User management (create, edit, delete all users)
- ✅ Business management (full CRUD)
- ✅ Financial reports & accounting
- ✅ System settings
- ✅ All operational features

---

### 🔹 Role ID: 2 - Manager
```
Username: manager
Password: manager123
Email:    manager@gelis.com
Name:     Manager User
Status:   ✅ Active
```

**Access Rights:**
- ✅ Dashboard & analytics
- ✅ Business management (full CRUD)
- ✅ User management (except Owner)
- ✅ Accounting & reports
- ✅ Assign technicians to jobs
- ✅ Order management

---

### 🔹 Role ID: 3 - Finance
```
Username: finance
Password: finance123
Email:    finance@gelis.com
Name:     Finance User
Status:   ✅ Active
```

**Access Rights:**
- ✅ Dashboard (financial overview)
- ✅ Accounting & transactions
- ✅ Financial reports
- ✅ Business data (read-only)
- ❌ User management
- ❌ Business CRUD

---

### 🔹 Role ID: 5 - Kasir (Cashier)
```
Username: kasir1
Password: kasir123
Email:    kasir1@gelis.com
Name:     Kasir User
Status:   ✅ Active
```

**Access Rights:**
- ✅ Dashboard (daily stats)
- ✅ Order management
- ✅ Daily cashier reports
- ✅ Business data (read-only)
- ❌ User management
- ❌ Full accounting access

---

### 🔹 Role ID: 6 - Loket (Counter)
```
Username: loket1
Password: loket123
Email:    loket1@gelis.com
Name:     Loket User
Status:   ✅ Active
```

**Access Rights:**
- ✅ Dashboard (daily stats)
- ✅ Order management
- ✅ Daily counter reports
- ✅ Business data (read-only)
- ❌ User management
- ❌ Full accounting access

---

### 🔹 Role ID: 7 - Teknisi (Technician)
```
Username: indra
Password: teknisi123
Email:    indra@gelis.com
Name:     Indra (Teknisi)
Status:   ✅ Active
```

**Access Rights:**
- ✅ Dashboard (job overview)
- ✅ Pekerjaan Teknisi (assigned jobs only)
- ✅ Update job progress
- ✅ View job details
- ❌ All other features

---

## 🔐 Important Security Notes

### 1. **Role-Based Access Control (RBAC)**
Sistem menggunakan **`role_id`** (bukan nama role) untuk menentukan akses:
```python
# ✅ CORRECT - Using role_id
if user['role_id'] in [1, 2]:  # Owner, Manager
    # Allow access
    
# ❌ WRONG - Using role name
if user['role_name'] == 'Owner':  # Don't use this!
    # This will fail
```

### 2. **Adding New Users**
Saat menambah user baru:
- ✅ **GUNAKAN** `role_id` dari tabel Role (1-7)
- ❌ **JANGAN** gunakan nama role sebagai patokan
- ✅ Pastikan `role_id` sesuai dengan daftar role yang ada
- ✅ Set `is_active: true` untuk user aktif

**Contoh penambahan user baru:**
```javascript
{
  username: "budi",
  password: "budi123",
  full_name: "Budi Santoso",
  email: "budi@gelis.com",
  role_id: 7,  // ✅ Use role_id (7 = Teknisi)
  is_active: true
}
```

### 3. **Password Policy**
- Default format: `[username]123`
- **WAJIB** diubah saat first login (production)
- Minimum 6 karakter
- Hash menggunakan bcrypt

### 4. **Permission Matrix**

| Feature | Owner (1) | Manager (2) | Finance (3) | Kasir (5) | Loket (6) | Teknisi (7) |
|---------|-----------|-------------|-------------|-----------|-----------|-------------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Businesses | ✅ Full | ✅ Full | ✅ Read | ✅ Read | ✅ Read | ❌ |
| Orders | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| Accounting | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Reports | ✅ | ✅ | ✅ | ✅ Daily | ✅ Daily | ❌ |
| Users | ✅ Full | ✅ Limited | ❌ | ❌ | ❌ | ❌ |
| Teknisi Jobs | ✅ All | ✅ All | ❌ | ❌ | ❌ | ✅ Assigned |
| Assign Teknisi | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 🚀 Quick Start for Testing

### Test Each Role:
```bash
# 1. Owner - Full Access
Username: owner / Password: owner123

# 2. Manager - Management Access
Username: manager / Password: manager123

# 3. Finance - Financial Access
Username: finance / Password: finance123

# 4. Kasir - Operational Access
Username: kasir1 / Password: kasir123

# 5. Loket - Counter Access
Username: loket1 / Password: loket123

# 6. Teknisi - Job Access
Username: indra / Password: teknisi123
```

---

## 📝 Notes

- **Demo credentials telah dihapus** dari layar login
- Semua permission check menggunakan `role_id` (verified ✅)
- Sistem telah ditest untuk semua 6 role (100% working ✅)
- Database menggunakan `role_id` sebagai foreign key di tabel users

---

**Last Updated**: 2025-12-14  
**System Version**: GELIS v1.0  
**Status**: Production Ready ✅
