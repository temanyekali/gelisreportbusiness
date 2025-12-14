"""
Script untuk generate mock data PPOB Loket dan Kasir yang REALISTIC dan LOGIS
- Loket: Setoran harus masuk akal (tidak minus)
- Kasir: Sesuai format real dengan setoran, topup, kas kecil, admin
Run: python3 /app/scripts/seed_ppob_realistic_final.py
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
import random
from dotenv import load_dotenv
from pathlib import Path
import os

# Import utils
from utils.helpers import generate_id, generate_code, utc_now

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Data realistic
PETUGAS_LOKET = ['Agus', 'Budi', 'Citra', 'Dewi', 'Eko']
HARI_INDONESIA = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BANK_CHANNELS = ['BRIS', 'MANDIRI', 'BNI', 'BCA']

# Saldo awal realistic per bank (modal kerja)
SALDO_AWAL_RANGE = {
    'BRIS': (300000000, 400000000),      # 300-400 juta (bank utama)
    'MANDIRI': (1500000, 3000000),       # 1.5-3 juta
    'BNI': (2000000, 4000000),          # 2-4 juta
    'BCA': (1000000, 2500000)           # 1-2.5 juta
}

# Data lunas (pemasukan) per shift - realistic
DATA_LUNAS_RANGE = {
    'BRIS': (2000000, 4000000),         # 2-4 juta per shift
    'MANDIRI': (400000, 800000),        # 400-800k per shift
    'BNI': (500000, 1000000),          # 500k-1juta per shift
    'BCA': (300000, 600000)            # 300-600k per shift
}

async def clear_all_data():
    """Clear existing PPOB data"""
    print("🧹 Clearing existing PPOB data...")
    
    result1 = await db.ppob_loket_shifts.delete_many({})
    result2 = await db.ppob_kasir_reports.delete_many({})
    result3 = await db.transactions.delete_many({'category': {'$regex': 'PPOB', '$options': 'i'}})
    
    print(f"   Deleted {result1.deleted_count} loket shift reports")
    print(f"   Deleted {result2.deleted_count} kasir reports")
    print(f"   Deleted {result3.deleted_count} PPOB transactions")

async def get_ppob_business():
    """Get PPOB business"""
    business = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if not business:
        print("❌ PPOB business not found!")
        return None
    return business

def generate_loket_shift_data(tanggal_obj, shift, petugas):
    """Generate realistic loket shift data - LOGIS, tidak ada minus"""
    
    # Pilih 2-3 bank yang digunakan per shift
    num_banks = random.randint(2, 3)
    active_banks = random.sample(BANK_CHANNELS, num_banks)
    
    channels = []
    total_data_lunas = 0
    
    for bank in active_banks:
        # Saldo awal (modal kerja)
        saldo_awal = random.randint(*SALDO_AWAL_RANGE[bank])
        
        # Saldo inject (kadang ada, kadang tidak)
        saldo_inject = 0
        if random.random() < 0.3:  # 30% kemungkinan ada inject
            saldo_inject = random.choice([1000000, 2000000, 3000000, 5000000])
        
        # DATA LUNAS = PEMASUKAN (hasil penjualan)
        data_lunas = random.randint(*DATA_LUNAS_RANGE[bank])
        
        # LOGIKA SETORAN: Harus <= data_lunas agar tidak minus!
        # Setor kasir: 50-80% dari data lunas (sisanya belum disetor)
        setor_kasir_pct = random.uniform(0.5, 0.8)
        setor_kasir = int(data_lunas * setor_kasir_pct)
        
        # Transfer bank (jarang, hanya 10% kemungkinan)
        tf_bank = 0
        if random.random() < 0.1 and bank != 'BRIS':
            # Transfer maksimal 20% dari sisa
            max_tf = int((data_lunas - setor_kasir) * 0.2)
            tf_bank = random.randint(100000, min(500000, max_tf)) if max_tf > 100000 else 0
        
        # Sisa setoran = Data lunas - Setor kasir - Transfer
        sisa_setoran = data_lunas - setor_kasir - tf_bank
        
        # Pastikan tidak minus!
        if sisa_setoran < 0:
            # Adjust setor kasir agar tidak minus
            setor_kasir = data_lunas - tf_bank
            sisa_setoran = 0
        
        # Saldo akhir = Saldo awal + Inject - Data lunas
        saldo_akhir = saldo_awal + saldo_inject - data_lunas
        
        # Uang lebih (kadang ada selisih kecil dari pembulatan)
        uang_lebih = 0
        if random.random() < 0.15:
            uang_lebih = random.randint(500, 5000)
            sisa_setoran += uang_lebih
        
        channel_data = {
            'nama_channel': bank,
            'saldo_awal': saldo_awal,
            'saldo_inject': saldo_inject,
            'data_lunas': data_lunas,
            'setor_kasir': setor_kasir,
            'transfer_bank': tf_bank,
            'sisa_setoran': sisa_setoran,
            'saldo_akhir': saldo_akhir,
            'uang_lebih': uang_lebih,
            'jumlah_transaksi': random.randint(15, 50)
        }
        
        channels.append(channel_data)
        total_data_lunas += data_lunas
    
    # Total sisa setoran
    total_sisa_setoran = sum(ch['sisa_setoran'] for ch in channels)
    total_setor_kasir = sum(ch['setor_kasir'] for ch in channels)
    
    return {
        'channels': channels,
        'total_penjualan': total_data_lunas,
        'total_sisa_setoran': total_sisa_setoran,
        'total_setor_kasir': total_setor_kasir
    }

async def seed_ppob_loket_reports():
    """Generate realistic PPOB loket shift reports"""
    print("\n📊 Generating PPOB loket shift reports...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Generate for last 30 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    shift_count = 0
    all_shifts_data = []  # Store for kasir report generation
    
    current_date = start_date
    while current_date <= end_date:
        daily_shifts = []
        
        # 2 shift per hari
        for shift in [1, 2]:
            petugas = random.choice(PETUGAS_LOKET)
            hari = HARI_INDONESIA[current_date.weekday()]
            
            # Generate shift data
            shift_data = generate_loket_shift_data(current_date, shift, petugas)
            
            # Create shift report
            shift_report = {
                'id': generate_id(),
                'tanggal': current_date.strftime('%Y-%m-%d'),
                'hari': hari,
                'shift': shift,
                'nama_petugas': petugas,
                'channels': shift_data['channels'],
                'total_penjualan': shift_data['total_penjualan'],
                'total_sisa_setoran': shift_data['total_sisa_setoran'],
                'total_setor_kasir': shift_data['total_setor_kasir'],
                'status_setoran': 'Sudah Disetor' if shift_data['total_setor_kasir'] > 0 else 'Belum Disetor',
                'created_by': 'system',
                'created_at': current_date.isoformat()
            }
            
            await db.ppob_loket_shifts.insert_one(shift_report)
            daily_shifts.append(shift_data)
            shift_count += 1
        
        # Store daily data for kasir report
        all_shifts_data.append({
            'tanggal': current_date.strftime('%Y-%m-%d'),
            'shifts': daily_shifts
        })
        
        current_date += timedelta(days=1)
    
    print(f"   ✓ Generated {shift_count} realistic loket shift reports")
    return all_shifts_data

async def seed_ppob_kasir_reports(all_shifts_data):
    """Generate realistic PPOB kasir reports based on loket shifts"""
    print("\n📊 Generating PPOB kasir reports...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    kasir_count = 0
    
    for daily_data in all_shifts_data:
        tanggal = daily_data['tanggal']
        shifts = daily_data['shifts']
        
        # SETORAN DARI LOKET (dari shift pagi dan siang)
        setoran_pagi = shifts[0]['total_setor_kasir'] if len(shifts) > 0 else 0
        setoran_siang = shifts[1]['total_setor_kasir'] if len(shifts) > 1 else 0
        total_setoran_loket = setoran_pagi + setoran_siang
        
        # SETORAN LOKET LUAR (simulasi loket di luar outlet utama)
        setoran_deposit_luar = random.randint(10000000, 20000000) if random.random() > 0.3 else 0
        setoran_pelunasan_pagi = random.randint(1000000, 3000000) if random.random() > 0.5 else 0
        setoran_pelunasan_siang = random.randint(500000, 2000000) if random.random() > 0.5 else 0
        total_setoran_luar = setoran_deposit_luar + setoran_pelunasan_pagi + setoran_pelunasan_siang
        
        # TOTAL UANG MASUK KE KASIR
        total_uang_masuk = total_setoran_loket + total_setoran_luar
        
        # TRANSFER TOPUP LOKET (pengeluaran untuk modal loket)
        # Generate 2-4 topup dengan total sekitar 30-40% dari setoran
        num_topup = random.randint(2, 4)
        topup_amounts = []
        total_target = int(total_uang_masuk * random.uniform(0.3, 0.4))
        
        for i in range(num_topup):
            if i == num_topup - 1:
                # Last topup = sisa
                amount = total_target - sum(topup_amounts)
            else:
                amount = random.randint(3000000, 15000000)
            topup_amounts.append(max(0, amount))
        
        total_topup = sum(topup_amounts)
        
        # KAS KECIL
        penerimaan_kas_kecil = random.randint(50000, 100000)
        pengurangan_parkir = random.randint(5000, 10000)
        belanja_loket = random.randint(0, 50000)
        total_kas_kecil = penerimaan_kas_kecil - pengurangan_parkir - belanja_loket
        
        # UANG ADMIN
        penerimaan_admin = random.randint(100000, 200000)
        total_admin = penerimaan_admin + random.randint(500000, 1000000)  # Akumulasi
        
        # SALDO AKHIR
        total_pengeluaran = total_topup + pengurangan_parkir + belanja_loket
        saldo_brangkas = total_uang_masuk - total_pengeluaran + penerimaan_kas_kecil + penerimaan_admin
        saldo_bank = 0  # Uang sudah ditransfer ke loket
        
        # Create kasir report
        kasir_report = {
            'id': generate_id(),
            'tanggal': tanggal,
            'setoran_loket_pagi': setoran_pagi,
            'setoran_loket_siang': setoran_siang,
            'setoran_deposit_luar': setoran_deposit_luar,
            'setoran_pelunasan_luar_pagi': setoran_pelunasan_pagi,
            'setoran_pelunasan_luar_siang': setoran_pelunasan_siang,
            'transfer_topup_loket': topup_amounts,
            'total_topup': total_topup,
            'penerimaan_kas_kecil': penerimaan_kas_kecil,
            'pengurangan_kas_kecil_parkir': pengurangan_parkir,
            'belanja_loket': belanja_loket,
            'total_kas_kecil': total_kas_kecil,
            'penerimaan_admin': penerimaan_admin,
            'total_admin': total_admin,
            'saldo_bank': saldo_bank,
            'saldo_brangkas': saldo_brangkas,
            'created_by': 'system',
            'created_at': tanggal + 'T17:00:00'
        }
        
        await db.ppob_kasir_reports.insert_one(kasir_report)
        kasir_count += 1
        
        # Create accounting transaction for kasir report
        # Income: Setoran
        if total_uang_masuk > 0:
            await db.transactions.insert_one({
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'business_id': ppob_business['id'],
                'transaction_type': 'income',
                'category': 'Setoran Kasir PPOB',
                'description': f'Setoran dari loket (Pagi: Rp {setoran_pagi:,}, Siang: Rp {setoran_siang:,}) + Loket Luar: Rp {total_setoran_luar:,}',
                'amount': total_uang_masuk,
                'payment_method': 'cash',
                'reference_number': f'PPOB-KASIR-{tanggal}',
                'created_by': 'system',
                'created_at': tanggal + 'T17:00:00'
            })
        
        # Expense: Topup loket
        if total_topup > 0:
            await db.transactions.insert_one({
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'business_id': ppob_business['id'],
                'transaction_type': 'expense',
                'category': 'Topup Modal Loket',
                'description': f'Transfer topup loket ({num_topup}x transfer): {", ".join([f"Rp {amt:,}" for amt in topup_amounts[:3]])}',
                'amount': total_topup,
                'payment_method': 'transfer',
                'reference_number': f'PPOB-TOPUP-{tanggal}',
                'created_by': 'system',
                'created_at': tanggal + 'T17:00:00'
            })
    
    print(f"   ✓ Generated {kasir_count} realistic kasir reports")

async def main():
    print("="*70)
    print("🚀 SEED PPOB DATA - REALISTIC & LOGIS (FINAL)")
    print("="*70)
    
    # Clear existing data
    await clear_all_data()
    
    # Seed loket reports
    all_shifts_data = await seed_ppob_loket_reports()
    
    # Seed kasir reports (based on loket data)
    await seed_ppob_kasir_reports(all_shifts_data)
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    loket_shifts = await db.ppob_loket_shifts.count_documents({})
    kasir_reports = await db.ppob_kasir_reports.count_documents({})
    ppob_txns = await db.transactions.count_documents({'category': {'$regex': 'PPOB', '$options': 'i'}})
    
    print(f"✓ PPOB Loket Shift Reports: {loket_shifts}")
    print(f"✓ PPOB Kasir Reports: {kasir_reports}")
    print(f"✓ PPOB Accounting Transactions: {ppob_txns}")
    
    print("\n✅ Realistic & logical data seeding completed!")
    print("="*70)
    
    print("\n💡 CATATAN PENTING:")
    print("   ✓ Setoran kasir <= Data Lunas (tidak ada minus)")
    print("   ✓ Laporan kasir sesuai format real")
    print("   ✓ Topup loket sebagai pengeluaran")
    print("   ✓ Saldo akhir logis dan terukur")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
