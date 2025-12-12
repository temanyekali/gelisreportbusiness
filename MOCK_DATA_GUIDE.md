# 📊 Panduan Mock Data GELIS

Dokumentasi lengkap tentang data mockup/simulasi di aplikasi GELIS untuk keperluan demo, testing, dan training.

---

## 🎯 Apa itu Mock Data?

**Mock Data** adalah data simulasi yang dibuat untuk meniru kondisi operasional real aplikasi GELIS. Data ini digunakan untuk:

✅ **Demo & Presentasi** - Tunjukkan fitur lengkap tanpa data real  
✅ **Training Karyawan** - Latihan menggunakan aplikasi dengan data realistic  
✅ **Testing & QA** - Test semua fitur dengan berbagai scenario  
✅ **Development** - Develop fitur baru dengan data yang konsisten  

---

## 📦 Data Mock yang Tersedia

### 1. **Users (14 Pengguna)**

| Role | Username | Password | Jumlah |
|------|----------|----------|--------|
| Owner | owner | owner123 | 1 (NOT mock) |
| Manager | manager | manager123 | 1 |
| Finance | finance | finance123 | 1 |
| Admin/CS | admin1 | admin123 | 1 |
| Kasir | kasir1-3 | kasir123 | 3 |
| Loket | loket1-3 | loket123 | 3 |
| Teknisi | teknisi1-4 | teknisi123 | 4 |

**Total:** 14 users (1 Owner real + 13 mock users)

### 2. **Businesses (5 Unit Bisnis)**

1. **Loket PPOB Pusat** - PPOB (Pulsa, Token Listrik, BPJS, Internet, TV Kabel)
2. **PLN Installation Service** - PLN (NIDI, SLO, Pasang Baru, Tambah Daya)
3. **Travel Umroh Barokah** - Travel (Paket Umroh & Haji)
4. **PDAM Service Center** - PDAM (Pasang Baru, Balik Nama, Pencatatan Meter)
5. **Toko Listrik Jaya** - Inventory (Material Listrik)

### 3. **Orders (~345 Orders)**

**Distribusi:**
- 60 hari terakhir: 3-8 orders per hari
- Berbagai status: pending, processing, completed, cancelled
- Customer: 40 customer unique dengan nama realistic
- Service types: Sesuai kategori business
- Amounts: Rp 5.000 - Rp 60.000.000

**Status Distribution:**
- Completed: ~70%
- Processing: ~15%
- Pending: ~10%
- Cancelled: ~5%

**Teknisi Assignment:**
- Orders PLN & PDAM: Assigned to teknisi
- Progress tracking: 0% (pending), 50% (processing), 100% (completed)

### 4. **Transactions (~404 Transaksi)**

**Revenue Transactions (~284):**
- Dari completed orders
- Payment methods: Cash, Transfer, QRIS, Debit Card, Credit Card
- Bank names: BRIS, MANDIRI, BCA, BNI, BSI, BRI, CIMB, Permata

**Expense Transactions (~120):**
- Operating costs spread 60 hari
- Categories:
  - Gaji Karyawan (Rp 5jt - 15jt)
  - Pembelian Material (Rp 2jt - 8jt)
  - Biaya Operasional (Rp 500rb - 3jt)
  - Sewa Kantor (Rp 3jt - 10jt)
  - Transport, Utilitas, Marketing, dll

**Total Revenue:** ~Rp 800jt - 1.2M  
**Total Expenses:** ~Rp 150jt - 250jt  
**Net Profit:** ~Rp 650jt - 950jt  

### 5. **Daily Reports**

**Loket Reports (~102):**
- 1-2 reports per day
- Shift: Pagi, Siang, Malam
- Opening/Closing balance
- Cash, Transfer, QRIS breakdown
- Transaction count & total revenue

**Kasir Reports (~84):**
- 1-2 reports per day
- Revenue vs Expenses
- Net income calculation
- Cash in hand & bank deposits
- Discrepancy tracking (<5% reports)

### 6. **Loyalty Programs (3 Programs)**

1. **Member Gold**
   - Min transaction: Rp 500.000
   - Cashback: 5%
   - Points: 50 per transaction
   - Benefits: Cashback, Priority Support, Free Konsultasi

2. **Member Platinum**
   - Min transaction: Rp 2.000.000
   - Cashback: 10%
   - Points: 100 per transaction
   - Benefits: 24/7 Support, Free Survey, Diskon Material

3. **Member Diamond**
   - Min transaction: Rp 5.000.000
   - Cashback: 15%
   - Points: 200 per transaction
   - Benefits: Dedicated AM, Free Maintenance

**Total Members:** 50-200 per program

### 7. **CSR Programs (3 Programs)**

1. **Bantuan Instalasi Listrik Gratis untuk Dhuafa**
   - Target: 50 beneficiaries
   - Budget: Rp 25jt
   - Category: Sosial

2. **Pelatihan Teknisi Listrik untuk Pemuda**
   - Target: 30 beneficiaries
   - Budget: Rp 15jt
   - Category: Pendidikan

3. **Beasiswa Anak Karyawan Berprestasi**
   - Target: 20 beneficiaries
   - Budget: Rp 40jt
   - Category: Pendidikan

**Progress:** 30%-90% completed

---

## 🔄 Cara Generate Mock Data

### Method 1: Via Script (Recommended)

```bash
# SSH ke server
ssh root@your-server

# Navigate ke project
cd /app

# Run seed script
python3 /app/scripts/seed_complete_mockup.py
```

**Proses:**
1. Clear semua existing data
2. Create roles (7 roles)
3. Create users (14 users)
4. Create businesses (5 businesses)
5. Generate orders (345 orders, 60 hari)
6. Generate transactions (404 transactions)
7. Generate reports (186 reports)
8. Create loyalty programs (3)
9. Create CSR programs (3)
10. Set mock data flag = true

**Duration:** ~5-10 seconds

### Method 2: Via API (Future)

```bash
# POST endpoint (akan ditambahkan)
curl -X POST https://api.gelis.com/api/data/seed-mock \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json"
```

---

## 🗑️ Cara Menghapus Mock Data

### Via Settings UI (Recommended)

**Langkah-langkah:**

1. **Login sebagai Owner**
   ```
   Username: owner
   Password: owner123
   ```

2. **Navigate ke Settings**
   - Klik menu "Settings" di sidebar
   - Atau akses: https://gelis.com/settings

3. **Lihat Warning Banner**
   - Banner orange akan muncul jika mock data aktif
   - Banner menunjukkan: "Mode Simulasi Aktif"

4. **Klik "Hapus Data Mockup"**
   - Button: "Hapus Data Mockup & Mulai Data Real"
   - Konfirmasi dialog akan muncul

5. **Konfirmasi Penghapusan**
   - Dialog menampilkan semua data yang akan dihapus:
     * Semua users (kecuali Owner)
     * Semua businesses
     * Semua orders (345)
     * Semua transactions (404)
     * Semua reports (186)
     * Semua loyalty programs (3)
     * Semua CSR programs (3)
   
6. **Klik "Ya, Hapus Semua Data Mockup"**
   - Proses delete ~2-3 detik
   - Toast notification: "Data mockup berhasil dihapus"

7. **Verify**
   - Warning banner hilang
   - Dashboard menunjukkan data kosong
   - Only Owner user tersisa
   - Ready untuk input data real

### Via API (Advanced)

```bash
# POST /api/data/clear-mock
curl -X POST https://api.gelis.com/api/data/clear-mock \
  -H "Authorization: Bearer OWNER_TOKEN" \
  -H "Content-Type: application/json"
```

**Response:**
```json
{
  "message": "Data mockup berhasil dihapus! Aplikasi sekarang siap untuk data real.",
  "summary": {
    "deleted_users": 13,
    "deleted_businesses": 5,
    "deleted_orders": 345,
    "deleted_transactions": 404,
    "deleted_loket_reports": 102,
    "deleted_kasir_reports": 84,
    "deleted_loyalty_programs": 3,
    "deleted_csr_programs": 3,
    "total_deleted": 959
  }
}
```

---

## 🎓 Use Cases Mock Data

### 1. Demo ke Client/Investor

**Scenario:** Presentasi fitur lengkap GELIS

**Steps:**
1. Login sebagai Owner
2. Tunjukkan Dashboard dengan data lengkap
3. Navigate ke Orders → Lihat berbagai status
4. Navigate ke Transactions → Lihat revenue & expenses
5. Navigate ke Reports → Lihat laporan harian
6. Navigate ke Users → Lihat struktur user roles
7. Navigate ke Settings → Explain fitur clear mock data

**Benefit:** Client dapat melihat aplikasi dengan data realistic tanpa privacy concerns

### 2. Training Karyawan Baru

**Scenario:** Onboarding karyawan baru (Loket, Kasir, Teknisi)

**Steps:**
1. Berikan credentials sesuai role (loket1/loket123)
2. Minta latihan buat order baru
3. Minta latihan update status order
4. Minta latihan buat laporan harian
5. Review hasil latihan

**Benefit:** Karyawan belajar tanpa takut merusak data real

### 3. Testing Fitur Baru

**Scenario:** Developer test fitur baru

**Steps:**
1. Run seed script untuk data fresh
2. Test fitur dengan berbagai scenario
3. Verify behavior dengan data existing
4. Clear mock data setelah testing

**Benefit:** Testing dengan data consistent dan reproducible

### 4. Performance Testing

**Scenario:** Load testing dengan data volume

**Steps:**
1. Generate mock data (345 orders + 404 transactions)
2. Test query performance
3. Test pagination
4. Test export functionality
5. Measure response time

**Benefit:** Simulate production load

---

## ⚙️ Mock Data Configuration

### Customization

Edit `/app/scripts/seed_complete_mockup.py` untuk customize:

**Jumlah Orders per Hari:**
```python
# Line ~400
daily_orders = random.randint(3, 8)  # Ubah range sesuai kebutuhan
```

**Date Range:**
```python
# Line ~390
for days_ago in range(60, -1, -1):  # 60 hari, ubah jadi 90 untuk 3 bulan
```

**Customer Names:**
```python
# Line ~38-43
CUSTOMER_NAMES = [
    # Tambah customer names sesuai kebutuhan
]
```

**Service Types & Prices:**
```python
# Line ~48-86
SERVICE_TYPES = {
    'PPOB': [
        ('Pulsa Telkomsel', 5000, 50000),
        # Tambah service baru
    ]
}
```

### Re-run After Customization

```bash
python3 /app/scripts/seed_complete_mockup.py
```

---

## 🔍 Identifikasi Mock Data

Semua mock data memiliki flag `is_mock: true` di database.

**Query MongoDB:**

```javascript
// Count mock users
db.users.countDocuments({ is_mock: true })

// Count mock orders
db.orders.countDocuments({ is_mock: true })

// Find all mock data
db.users.find({ is_mock: true })
```

**Via API:**

```bash
# Get all orders (mock + real)
GET /api/orders

# Response includes is_mock field
{
  "id": "...",
  "order_number": "ORD-...",
  "is_mock": true,
  ...
}
```

---

## 🚫 Apa yang TIDAK Dihapus

Saat clear mock data, beberapa data tetap dipertahankan:

✅ **Owner User** (is_mock: false)  
✅ **Roles** (diperlukan untuk system)  
✅ **Settings** (konfigurasi system)  
✅ **Activity Logs** (untuk audit trail)  

**Reason:** Data ini essential untuk operasional system

---

## 📊 Mock Data Statistics

### Database Size

```
• Users: ~2 KB
• Businesses: ~1 KB
• Orders: ~200 KB
• Transactions: ~150 KB
• Reports: ~100 KB
• Loyalty: ~2 KB
• CSR: ~2 KB
• Activity Logs: ~50 KB
-------------------------
Total Mock Data: ~507 KB (~0.5 MB)
```

### Query Performance

```
• List orders (345): ~50-100ms
• List transactions (404): ~60-120ms
• Dashboard aggregate: ~80-150ms
• Reports daily: ~30-80ms
```

**Note:** Performance tergantung server specs

---

## 🔐 Security & Best Practices

### 1. **Production Environment**

⚠️ **PENTING:** Hapus mock data sebelum go-live production!

```bash
# Steps:
1. Login sebagai Owner
2. Settings → Clear Mock Data
3. Verify: Dashboard harus kosong
4. Input data real pertama
5. Test dengan data real
```

### 2. **Demo Environment**

✅ **Maintain** mock data di demo server untuk:
- Client presentations
- Sales demos
- Training sessions

### 3. **Development Environment**

✅ **Re-seed** mock data regularly:
- After major code changes
- Before feature testing
- Weekly refresh

### 4. **Testing Environment**

✅ **Automate** seed & clear di CI/CD:
```yaml
# Example GitHub Actions
- name: Seed Test Data
  run: python3 scripts/seed_complete_mockup.py

- name: Run Tests
  run: pytest

- name: Clear Test Data
  run: python3 scripts/clear_mock_data.py
```

---

## 🆘 Troubleshooting

### Problem 1: "Data mockup tidak muncul"

**Solution:**
```bash
# Check MongoDB
mongosh
use gelis_db
db.orders.countDocuments({ is_mock: true })

# If 0, run seed again
python3 /app/scripts/seed_complete_mockup.py
```

### Problem 2: "Error saat hapus mock data"

**Solution:**
```bash
# Check user role
# Only Owner can delete mock data

# Verify via API
curl https://api.gelis.com/api/auth/me \
  -H "Authorization: Bearer TOKEN"

# Response should show role_id: 1 (Owner)
```

### Problem 3: "Data tidak konsisten setelah seed"

**Solution:**
```bash
# Clear dan re-seed
python3 /app/scripts/seed_complete_mockup.py

# Script akan auto-clear existing data terlebih dahulu
```

### Problem 4: "Performance lambat setelah seed banyak data"

**Solution:**
```bash
# Check database indexes
mongosh
use gelis_db
db.orders.getIndexes()

# Add indexes if needed
db.orders.createIndex({ "created_at": -1 })
db.orders.createIndex({ "business_id": 1 })
db.orders.createIndex({ "status": 1 })
```

---

## 📝 Changelog

### Version 1.0.0 (2025-01-XX)
- ✅ Initial mock data seeder
- ✅ 14 users (7 roles)
- ✅ 5 businesses
- ✅ 345 orders (60 hari)
- ✅ 404 transactions
- ✅ 186 reports
- ✅ 3 loyalty programs
- ✅ 3 CSR programs
- ✅ Clear mock data via Settings UI
- ✅ Mock data flag tracking

---

## 🎯 Kesimpulan

Mock data di GELIS dirancang untuk:

✅ **Realistic** - Menyerupai kondisi operasional real  
✅ **Comprehensive** - Mencakup semua module  
✅ **Flexible** - Mudah di-customize  
✅ **Manageable** - Hapus dengan 1 klik  
✅ **Trackable** - Flag `is_mock` di semua data  

**Gunakan mock data untuk:**
- Demo & presentasi
- Training karyawan
- Testing & QA
- Development

**Hapus mock data saat:**
- Go-live production
- Input data real pertama
- Deployment ke client

---

**Happy Testing dengan Mock Data! 🎉**

---

**Dibuat dengan ❤️ untuk GELIS**  
**Versi: 1.0.0**  
**Tanggal: 2025**
