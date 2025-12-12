# 📊 Panduan Sinkronisasi Akuntansi Otomatis GELIS

## 🎯 Apa itu Auto-Sync Accounting?

Sistem **Sinkronisasi Akuntansi Otomatis** adalah fitur canggih GELIS yang **secara real-time** mencatat setiap transaksi keuangan dari order ke dalam sistem akuntansi. Tidak perlu input manual - semua terhubung otomatis!

---

## ✨ Fitur Utama

### 1. **Auto-Create Transaction dari Order**
Setiap kali order dibuat atau diupdate dengan pembayaran:
- ✅ Transaction record otomatis dibuat di database
- ✅ Langsung masuk ke laporan keuangan
- ✅ Real-time update di Financial Dashboard

### 2. **Financial Dashboard Real-Time**
Endpoint baru: `GET /api/financial/dashboard`

**Data yang ditampilkan:**
- 💰 Total Pemasukan (Income)
- 💸 Total Pengeluaran (Expense)
- 📈 Laba Bersih (Net Profit)
- 📊 Profit Margin (%)
- 📦 Ringkasan Orders (Total, Paid, Pending)
- 🎯 Payment Collection Rate
- 🔢 Jumlah Transaksi

### 3. **Tracking Pembayaran Bertahap**
Sistem mendukung pembayaran bertahap (DP + Pelunasan):
- DP Rp 2,000,000 → Transaction #1 dibuat
- Pelunasan Rp 3,000,000 → Transaction #2 dibuat (hanya selisih)
- Total tercatat: Rp 5,000,000 ✅

---

## 🚀 Cara Kerja

### Skenario 1: Order Baru dengan Pembayaran Langsung

**Request:**
```bash
POST /api/orders
{
  "business_id": "xxx",
  "customer_name": "Budi Santoso",
  "service_type": "Token Listrik",
  "total_amount": 100000,
  "paid_amount": 100000,
  "payment_method": "cash"
}
```

**Yang Terjadi Otomatis:**
1. ✅ Order dibuat dengan `payment_status: "paid"`
2. ✅ Transaction record dibuat:
   ```json
   {
     "transaction_type": "income",
     "category": "Order Payment",
     "amount": 100000,
     "description": "Pembayaran order ORD123... - Budi Santoso",
     "order_id": "xxx"
   }
   ```
3. ✅ Activity log tercatat
4. ✅ Financial dashboard langsung update

---

### Skenario 2: Pembayaran Bertahap (DP + Pelunasan)

**Step 1: Buat Order dengan DP**
```bash
POST /api/orders
{
  "total_amount": 5000000,
  "paid_amount": 2000000,  # DP 40%
  "payment_method": "transfer"
}
```

**Hasil:**
- Order dibuat dengan `payment_status: "partial"`
- Transaction #1: Rp 2,000,000 ✅

**Step 2: Update dengan Pelunasan**
```bash
PUT /api/orders/{order_id}?paid_amount=5000000&status=completed
```

**Hasil:**
- Order diupdate ke `payment_status: "paid"`
- Transaction #2: Rp 3,000,000 (selisih) ✅
- Total tercatat: Rp 5,000,000

---

## 📱 Integrasi dengan Module Lain

### **Loket Daily Reports**
Saat membuat laporan harian loket:
- Transaction otomatis dibuat untuk `total_setoran_shift`
- Category: "Setoran Loket"

### **Kasir Daily Reports**
Membaca data real-time dari transactions untuk:
- Total revenue hari itu
- Total expenses hari itu
- Net income

### **Orders Module**
- Setiap order paid/partial otomatis masuk ke transactions
- Link order_id ke transaction untuk traceability

---

## 🎨 Keunggulan Sistem

| Feature | Before | After (Auto-Sync) |
|---------|--------|-------------------|
| Input Manual | ✅ Perlu input 2x (Order + Transaction) | ❌ Cukup input Order |
| Real-time Data | ❌ Delay | ✅ Instant |
| Akurasi | ⚠️ Rawan human error | ✅ 100% akurat |
| Audit Trail | ⚠️ Susah dilacak | ✅ Full traceability via order_id |
| Pembayaran Bertahap | ❌ Ribet tracking | ✅ Auto-track semua cicilan |

---

## 📊 Financial Dashboard API

### **Endpoint:**
```
GET /api/financial/dashboard
```

### **Query Parameters (Optional):**
- `business_id`: Filter by business
- `start_date`: Format ISO (e.g., "2024-01-01T00:00:00")
- `end_date`: Format ISO (e.g., "2024-12-31T23:59:59")

### **Response:**
```json
{
  "period": {
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-12-31T23:59:59"
  },
  "financial_summary": {
    "total_income": 6928781062,
    "total_expense": 793122035,
    "net_profit": 6135659027,
    "profit_margin": 88.55
  },
  "income_breakdown": {
    "Order Payment": 5500000000,
    "Setoran Loket": 1428781062
  },
  "expense_breakdown": {
    "Gaji Karyawan": 450000000,
    "Material/Stock": 200000000,
    "Operasional": 143122035
  },
  "orders_summary": {
    "total_orders": 333,
    "total_order_amount": 7200000000,
    "paid_orders": 239,
    "pending_orders": 94,
    "payment_collection_rate": 71.8
  },
  "transaction_count": {
    "total": 904,
    "income_transactions": 663,
    "expense_transactions": 241
  }
}
```

---

## 🔐 Permission Control

**Role Access untuk Financial Dashboard:**
- ✅ Owner (Full access)
- ✅ Manager (Full access)
- ✅ Finance (Full access)
- ❌ Lainnya (Tidak bisa akses)

---

## 🧪 Testing

### Test Create Order dengan Pembayaran:
```bash
curl -X POST "$API_URL/api/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "xxx",
    "customer_name": "Test Customer",
    "service_type": "Token Listrik",
    "total_amount": 100000,
    "paid_amount": 100000,
    "payment_method": "cash"
  }'
```

### Test Financial Dashboard:
```bash
curl -X GET "$API_URL/api/financial/dashboard" \
  -H "Authorization: Bearer $TOKEN"
```

### Verify Transaction Created:
```bash
curl -X GET "$API_URL/api/transactions?transaction_type=income" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Mock Data

Script seed sudah diupdate untuk generate data yang **fully connected**:
- ✅ Setiap order dengan `paid_amount > 0` otomatis punya transaction
- ✅ 60 hari data historis
- ✅ Data realistis untuk bisnis PPOB, PLN, Travel, PDAM, Inventory

**Run seed:**
```bash
python /app/scripts/seed_complete_mockup.py
```

**Login credentials:**
- Owner: `owner` / `owner123`
- Finance: `finance` / `finance123`
- Manager: `manager` / `manager123`

---

## 🎯 Best Practices

1. **Selalu gunakan endpoint order** untuk transaksi pelanggan
   - Jangan buat transaction manual untuk pembayaran order
   - Biarkan sistem handle otomatis

2. **Manual transaction** hanya untuk:
   - Pengeluaran operasional (gaji, sewa, utilities)
   - Transfer antar akun
   - Adjustment/Koreksi

3. **Monitor Financial Dashboard** secara berkala
   - Daily: Cek collection rate
   - Weekly: Review profit margin
   - Monthly: Analisa breakdown per kategori

4. **Audit Trail**
   - Gunakan `order_id` di transaction untuk tracking
   - Check activity logs untuk investigasi

---

## 🚀 Deployment Ready

Sistem ini sudah production-ready dengan:
- ✅ Environment variables configured
- ✅ Auto-restart on code changes (hot reload)
- ✅ Full error handling
- ✅ Activity logging
- ✅ Permission control
- ✅ Real-time data sync

---

## 📞 Support

Untuk pertanyaan atau bantuan implementasi:
- 📧 Email: support@gelis.com
- 📱 Phone: 021-12345678
- 🌐 Web: https://gelis.com

---

**Dibuat:** 12 Desember 2024
**Versi:** 1.0.0
**Status:** ✅ Production Ready
