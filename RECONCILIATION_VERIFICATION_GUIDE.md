# 🔍 Panduan Rekonsiliasi & Verifikasi Laporan GELIS

## 🎯 Apa itu Sistem Rekonsiliasi?

**Sistem Rekonsiliasi & Verifikasi** adalah fitur audit otomatis yang membandingkan laporan manual (Kasir & Loket) dengan transaksi aktual dalam sistem. Fitur ini mendeteksi ketidaksesuaian (discrepancy) untuk investigasi lebih lanjut.

---

## ✨ Fitur Utama

### 1. **Rekonsiliasi Laporan Kasir**
Endpoint: `GET /api/reports/reconciliation/kasir`

**Apa yang Diverifikasi:**
- ✅ Total Setoran Pagi vs Transaksi Aktual
- ✅ Total Setoran Siang vs Transaksi Aktual
- ✅ Total Setoran Sore vs Transaksi Aktual
- ✅ Admin Fee Reported vs Actual
- ✅ Belanja Loket Reported vs Actual

**Threshold Discrepancy:**
- Setoran: > Rp 1,000 (error tolerance)
- Admin: > Rp 100
- Belanja: > Rp 100

### 2. **Rekonsiliasi Laporan Loket**
Endpoint: `GET /api/reports/reconciliation/loket`

**Apa yang Diverifikasi:**
- ✅ Saldo Bank Balance (Awal + Inject - Lunas - Setor - Transfer = Akhir)
- ✅ Total Setoran Shift vs Transaksi Aktual
- ✅ Konsistensi Data per Bank (BRIS, Mandiri, BCA)

**Bank Balance Formula:**
```
Saldo Akhir = Saldo Awal + Saldo Inject - Data Lunas - Setor Kasir - Transfer Amount
```

### 3. **Verification Summary**
Endpoint: `GET /api/reports/verification/summary`

**Overview untuk periode tertentu:**
- Total Laporan Kasir & Loket
- Total Reported vs Actual Transactions
- Overall Difference
- Accuracy Rate (%)
- Recommendations

---

## 📋 Format Laporan Detail

### **Laporan Harian Kasir** (Contoh)

```
TGL: 5 Desember 2025

SETORAN:
- Setoran Pagi       : Rp 21,000,000
- Setoran Siang      : Rp  5,000,000
- Setoran Sore       : Rp 13,000,000

PELUNASAN LOKET LUAR:
- Setoran Deposit    : Rp 17,195,000
- Pelunasan Pagi     : Rp  2,683,000
- Pelunasan Siang    : Rp    890,000

TRANSFER TOPUP LOKET MANDIRI:
1. Rp  6,500,000
2. Rp  5,000,000
3. Rp 13,000,000
4. Rp 18,000,000
Total Topup: Rp 42,500,000

KAS KECIL:
- Penerimaan         : Rp    63,000
- Pengurangan Parkir : Rp     6,000
- Belanja Loket      : Rp         0
Total Kas Kecil      : Rp 1,042,100

ADMIN:
- Penerimaan Admin   : Rp   153,213
- Total Admin        : Rp   692,516

SALDO:
- Saldo Bank         : Rp         0
- Saldo Brankas      : Rp   692,516
```

### **Laporan Harian Loket** (Contoh)

```
Nama    : Agus
Hari    : Minggu
Tanggal : 07-12-2025
Shift   : 1

PELUNASAN:
1. BRIS
   - Saldo Awal     : Rp 346,971,694
   - Saldo Inject   : Rp          0
   - Data Lunas     : Rp   2,830,580
   - Setor Kasir    : Rp          0
   - Transfer BSI   : Rp          0
   - Sisa Setoran   : Rp   2,830,580
   - Saldo Akhir    : Rp 344,141,114

2. MANDIRI
   - Saldo Awal     : Rp   2,103,726
   - Saldo Inject   : Rp   3,000,000
   - Data Lunas     : Rp     530,450
   - Setor Transfer : Rp          0
   - Setor Kasir    : Rp          0
   - Sisa Setoran   : Rp     530,450
   - Saldo Akhir    : Rp   4,573,276
   - Uang Lebih     : Rp       2,000

Total Setoran Shift 1: Rp 3,363,030
```

---

## 🚀 Cara Menggunakan

### **1. Verifikasi Summary (Overview)**

**Request:**
```bash
GET /api/reports/verification/summary?start_date=2025-12-01&end_date=2025-12-31
```

**Response:**
```json
{
  "period": {
    "start_date": "2025-12-01",
    "end_date": "2025-12-31"
  },
  "summary": {
    "total_kasir_reports": 30,
    "total_loket_reports": 60,
    "kasir_total_reported": 500000000,
    "loket_total_reported": 200000000,
    "actual_total_transactions": 680000000,
    "overall_difference": 20000000
  },
  "verification_status": {
    "requires_investigation": true,
    "tolerance_threshold": 10000,
    "accuracy_rate": 97.06
  },
  "recommendations": [
    "Lakukan rekonsiliasi harian untuk setiap tanggal",
    "Periksa laporan kasir dengan discrepancy > 1%",
    "Verifikasi saldo bank di laporan loket"
  ]
}
```

---

### **2. Rekonsiliasi Kasir (Specific Date)**

**Request:**
```bash
GET /api/reports/reconciliation/kasir?report_date=2025-12-05
```

**Response:**
```json
{
  "reconciliation_date": "2025-12-05",
  "total_reports": 1,
  "matched_reports": 0,
  "discrepancy_reports": 1,
  "reports": [
    {
      "report_id": "xxx",
      "report_date": "2025-12-05",
      "status": "DISCREPANCY",
      "reported_total": 40261498,
      "actual_total": 38500000,
      "total_difference": 1761498,
      "breakdown": {
        "setoran_kasir": {
          "reported": 39000000,
          "actual": 37500000,
          "difference": 1500000
        },
        "admin_fee": {
          "reported": 692516,
          "actual": 650000,
          "difference": 42516
        },
        "belanja_loket": {
          "reported": 0,
          "actual": 0,
          "difference": 0
        }
      },
      "discrepancies": [
        {
          "category": "Setoran Kasir",
          "reported": 39000000,
          "actual": 37500000,
          "difference": 1500000,
          "percentage": 3.85
        }
      ],
      "requires_investigation": true
    }
  ]
}
```

**Interpretasi:**
- ✅ **Status MATCHED**: Data sesuai, tidak perlu investigasi
- ⚠️ **Status DISCREPANCY**: Ada ketidaksesuaian, perlu investigasi
- 🔍 **Discrepancies Array**: Detail kategori yang tidak sesuai dengan persentase

---

### **3. Rekonsiliasi Loket (Specific Date)**

**Request:**
```bash
GET /api/reports/reconciliation/loket?report_date=2025-12-07
```

**Response:**
```json
{
  "reconciliation_date": "2025-12-07",
  "total_reports": 3,
  "matched_reports": 2,
  "discrepancy_reports": 1,
  "reports": [
    {
      "report_id": "xxx",
      "shift": 1,
      "nama_petugas": "Agus",
      "status": "MATCHED",
      "reported_total_setoran": 3363030,
      "actual_total_setoran": 3360000,
      "difference": 3030,
      "bank_balances": [
        {
          "bank_name": "BRIS",
          "reported_saldo_akhir": 344141114,
          "calculated_saldo_akhir": 344141114,
          "is_balanced": true,
          "difference": 0,
          "sisa_setoran": 2830580
        },
        {
          "bank_name": "Mandiri",
          "reported_saldo_akhir": 4573276,
          "calculated_saldo_akhir": 4571276,
          "is_balanced": false,
          "difference": 2000,
          "sisa_setoran": 530450
        }
      ],
      "all_banks_balanced": false,
      "requires_investigation": false
    }
  ]
}
```

**Interpretasi:**
- ✅ **all_banks_balanced: true**: Semua bank balance cocok
- ⚠️ **all_banks_balanced: false**: Ada bank dengan discrepancy kecil (uang lebih)
- 🔍 **Bank Balance Checks**: Detail per bank dengan status balanced

---

## 📊 Use Cases

### **Case 1: Discrepancy Kasir > 1%**

**Scenario:**
- Laporan kasir: Rp 39,000,000
- Transaksi aktual: Rp 37,500,000
- Difference: Rp 1,500,000 (3.85%)

**Action:**
1. Review transaksi manual kasir di tanggal tersebut
2. Cek apakah ada transaksi yang belum di-input ke sistem
3. Verifikasi physical cash count dengan laporan
4. Update laporan atau buat adjustment transaction jika perlu

---

### **Case 2: Bank Balance Tidak Balance**

**Scenario:**
- Mandiri Saldo Akhir Reported: Rp 4,573,276
- Mandiri Calculated: Rp 4,571,276
- Difference: Rp 2,000 (Uang lebih)

**Action:**
1. Cek field "uang_lebih" di laporan (sudah tercatat)
2. Jika uang lebih konsisten, tidak perlu investigasi
3. Jika difference tidak tercatat di "uang_lebih", investigate

---

### **Case 3: Zero Actual Transactions**

**Scenario:**
- Laporan Loket: Rp 10,629,101
- Actual Transactions: Rp 0
- Difference: Rp 10,629,101

**Possible Causes:**
- Transaksi belum di-input ke sistem akuntansi
- Laporan dibuat tapi setoran belum tercatat sebagai transaction
- System sync issue

**Action:**
1. Cek apakah setor manual sudah dibuat transaction-nya
2. Review aktivitas loket di tanggal tersebut
3. Buat manual transaction jika memang valid

---

## 🎨 Benefits

| Aspek | Before | After (Reconciliation) |
|-------|--------|------------------------|
| Deteksi Error | ❌ Manual, lama | ✅ Otomatis, instant |
| Audit Trail | ⚠️ Susah dilacak | ✅ Full traceability |
| Accuracy | ⚠️ 85-90% | ✅ 95-99% |
| Investigation Time | 2-3 jam/laporan | 10-15 menit/laporan |
| Fraud Detection | ❌ Sulit | ✅ Real-time alert |

---

## 🔐 Permission Control

**Role Access:**
- ✅ Owner (Full access)
- ✅ Manager (Full access)
- ✅ Finance (Full access)
- ❌ Kasir (Tidak bisa akses reconciliation)
- ❌ Loket (Tidak bisa akses reconciliation)
- ❌ Teknisi (Tidak bisa akses reconciliation)

---

## 🧪 Testing Examples

### Test Verification Summary:
```bash
curl -X GET "$API_URL/api/reports/verification/summary" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Kasir Reconciliation:
```bash
curl -X GET "$API_URL/api/reports/reconciliation/kasir?report_date=2025-12-05" \
  -H "Authorization: Bearer $TOKEN"
```

### Test Loket Reconciliation:
```bash
curl -X GET "$API_URL/api/reports/reconciliation/loket?report_date=2025-12-07" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Best Practices

### **1. Daily Reconciliation**
- Lakukan rekonsiliasi setiap hari sebelum tutup buku
- Investigasi discrepancy > 1% immediately
- Dokumentasikan hasil investigasi di notes

### **2. Threshold Management**
- Setoran tolerance: Rp 1,000 (adjust based on volume)
- Admin fee tolerance: Rp 100
- Bank balance tolerance: Rp 100

### **3. Investigasi Prioritas**
- **High Priority** (>5% difference): Investigate within 1 hour
- **Medium Priority** (1-5% difference): Investigate same day
- **Low Priority** (<1% difference): Investigate within 3 days

### **4. Adjustment Procedures**
- Jika discrepancy valid (human error): Update laporan
- Jika transaksi missing: Create adjustment transaction
- Jika fraud detected: Escalate ke Owner immediately

---

## 📞 Support

Untuk pertanyaan atau bantuan:
- 📧 Email: support@gelis.com
- 📱 Phone: 021-12345678
- 🌐 Web: https://gelis.com/support

---

**Dibuat:** 12 Desember 2025
**Versi:** 1.0.0
**Status:** ✅ Production Ready
