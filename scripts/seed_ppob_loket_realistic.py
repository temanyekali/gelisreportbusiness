"""
Script untuk generate mock data PPOB Loket yang REALISTIC dan BENAR
Berdasarkan contoh real laporan harian loket
Run: python3 /app/scripts/seed_ppob_loket_realistic.py
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

async def clear_ppob_loket_data():
    """Clear existing PPOB loket data"""
    print("🧹 Clearing existing PPOB loket shift data...")
    
    result1 = await db.ppob_loket_shifts.delete_many({})
    result2 = await db.transactions.delete_many({'category': {'$regex': 'Penjualan PPOB Shift', '$options': 'i'}})
    
    print(f"   Deleted {result1.deleted_count} loket shift reports")
    print(f"   Deleted {result2.deleted_count} PPOB accounting transactions")

async def get_ppob_business():
    """Get PPOB business"""
    business = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if not business:
        print("❌ PPOB business not found!")
        return None
    return business

def generate_loket_shift_data(tanggal_obj, shift, petugas):
    """Generate realistic loket shift data"""
    
    # Pilih 2-3 bank yang digunakan per shift (tidak semua bank aktif setiap shift)
    num_banks = random.randint(2, 3)
    active_banks = random.sample(BANK_CHANNELS, num_banks)
    
    channels = []
    total_data_lunas = 0
    
    for bank in active_banks:
        # Saldo awal (modal kerja)
        saldo_awal = random.randint(*SALDO_AWAL_RANGE[bank])
        
        # Saldo inject (kadang ada, kadang tidak)
        # 30% kemungkinan ada inject
        saldo_inject = 0
        if random.random() < 0.3:
            saldo_inject = random.choice([1000000, 2000000, 3000000, 5000000])
        
        # DATA LUNAS = PEMASUKAN (hasil penjualan)
        data_lunas = random.randint(*DATA_LUNAS_RANGE[bank])
        
        # Setor kasir (kadang disetor di shift ini, kadang belum)
        # 20% kemungkinan sudah disetor
        setor_kasir = 0
        if random.random() < 0.2:
            setor_kasir = data_lunas
        
        # Transfer BSI/antar bank (jarang terjadi)
        # 10% kemungkinan ada transfer
        tf_bank = 0
        if random.random() < 0.1 and bank != 'BRIS':
            tf_bank = random.randint(100000, 500000)
        
        # Sisa setoran = Data lunas - Setor kasir - Transfer
        sisa_setoran = data_lunas - setor_kasir - tf_bank
        
        # Saldo akhir = Saldo awal + Inject - Data lunas (karena uang penjualan keluar dari rekening untuk beli produk)
        saldo_akhir = saldo_awal + saldo_inject - data_lunas
        
        # Uang lebih (kadang ada selisih kecil dari pembulatan)
        # 15% kemungkinan ada uang lebih
        uang_lebih = 0
        if random.random() < 0.15:
            uang_lebih = random.randint(500, 5000)
        
        channel_data = {
            'nama_channel': bank,
            'saldo_awal': saldo_awal,
            'saldo_inject': saldo_inject,
            'data_lunas': data_lunas,  # INI PEMASUKAN!
            'setor_kasir': setor_kasir,
            'transfer_bank': tf_bank,
            'sisa_setoran': sisa_setoran + uang_lebih,  # Termasuk uang lebih
            'saldo_akhir': saldo_akhir,
            'uang_lebih': uang_lebih,
            'jumlah_transaksi': random.randint(15, 50)  # Estimasi jumlah transaksi
        }
        
        channels.append(channel_data)
        total_data_lunas += data_lunas
    
    # Total sisa setoran (yang harus disetor ke kasir)
    total_sisa_setoran = sum(ch['sisa_setoran'] for ch in channels)
    
    return {
        'channels': channels,
        'total_penjualan': total_data_lunas,  # TOTAL PEMASUKAN
        'total_sisa_setoran': total_sisa_setoran
    }

async def seed_ppob_loket_reports():
    """Generate realistic PPOB loket shift reports"""
    print("\n📊 Generating realistic PPOB loket shift reports...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Generate for last 30 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    shift_count = 0
    total_pemasukan = 0
    
    current_date = start_date
    while current_date <= end_date:
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
                'status_setoran': random.choice(['Sudah Disetor', 'Sudah Disetor', 'Belum Disetor']),  # 66% sudah disetor
                'created_by': 'system',
                'created_at': current_date.isoformat()
            }
            
            await db.ppob_loket_shifts.insert_one(shift_report)
            
            # Create accounting transaction (AKUMULASI PER SHIFT)
            # Breakdown detail per channel
            channel_details = []
            for ch in shift_data['channels']:
                detail = f"{ch['nama_channel']}: Rp {ch['data_lunas']:,.0f} ({ch['jumlah_transaksi']} trx"
                if ch['uang_lebih'] > 0:
                    detail += f", +Rp {ch['uang_lebih']:,} lebih"
                detail += ")"
                channel_details.append(detail)
            
            description = (
                f"Akumulasi penjualan PPOB Shift {shift} - {petugas} ({hari}, {current_date.strftime('%d-%m-%Y')})\n"
                f"Detail: {' | '.join(channel_details)}\n"
                f"Total Setoran: Rp {shift_data['total_sisa_setoran']:,.0f}"
            )
            
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'business_id': ppob_business['id'],
                'transaction_type': 'income',
                'category': f'Penjualan PPOB Shift {shift}',
                'description': description,
                'amount': shift_data['total_penjualan'],  # TOTAL PEMASUKAN (DATA LUNAS)
                'payment_method': 'cash',
                'reference_number': f"PPOB-SHIFT-{current_date.strftime('%Y%m%d')}-{shift}",
                'order_id': None,
                'created_by': 'system',
                'created_at': current_date.isoformat()
            }
            
            await db.transactions.insert_one(transaction)
            
            shift_count += 1
            total_pemasukan += shift_data['total_penjualan']
        
        current_date += timedelta(days=1)
    
    print(f"   ✓ Generated {shift_count} realistic loket shift reports")
    print(f"   ✓ Total pemasukan PPOB: Rp {total_pemasukan:,.0f}")

async def show_sample_reports():
    """Show sample reports untuk verifikasi"""
    print("\n📋 Sample Laporan Loket (untuk verifikasi):")
    print("=" * 70)
    
    # Ambil 2 sample reports
    samples = await db.ppob_loket_shifts.find({}, {'_id': 0}).limit(2).to_list(2)
    
    for idx, report in enumerate(samples, 1):
        print(f"\n🔸 Sample {idx}")
        print(f"Nama Petugas: {report['nama_petugas']}")
        print(f"Hari/Tanggal: {report['hari']}, {report['tanggal']}")
        print(f"Shift ke: {report['shift']}")
        print(f"\nDetail Channel:")
        
        for ch in report['channels']:
            print(f"\n  📌 {ch['nama_channel']}")
            print(f"     Saldo Awal: Rp {ch['saldo_awal']:,}")
            print(f"     Saldo Inject: Rp {ch['saldo_inject']:,}")
            print(f"     Data Lunas (PEMASUKAN): Rp {ch['data_lunas']:,} ✅")
            print(f"     Jumlah Transaksi: {ch['jumlah_transaksi']} trx")
            print(f"     Setor Kasir: Rp {ch['setor_kasir']:,}")
            if ch.get('transfer_bank', 0) > 0:
                print(f"     Transfer Bank: Rp {ch['transfer_bank']:,}")
            print(f"     Sisa Setoran: Rp {ch['sisa_setoran']:,}")
            print(f"     Saldo Akhir: Rp {ch['saldo_akhir']:,}")
            if ch.get('uang_lebih', 0) > 0:
                print(f"     Uang Lebih: Rp {ch['uang_lebih']:,}")
        
        print(f"\n  💰 TOTAL PEMASUKAN SHIFT {report['shift']}: Rp {report['total_penjualan']:,}")
        print(f"  💸 TOTAL SISA SETORAN: Rp {report['total_sisa_setoran']:,}")
        print(f"  📊 Status: {report['status_setoran']}")
        print("=" * 70)

async def main():
    print("=" * 70)
    print("🚀 SEED PPOB LOKET DATA - REALISTIC & PROFESSIONAL")
    print("=" * 70)
    
    # Clear existing data
    await clear_ppob_loket_data()
    
    # Seed PPOB loket reports
    await seed_ppob_loket_reports()
    
    # Show samples
    await show_sample_reports()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    loket_shifts = await db.ppob_loket_shifts.count_documents({})
    ppob_txns = await db.transactions.count_documents({'category': {'$regex': 'Penjualan PPOB Shift', '$options': 'i'}})
    
    # Hitung total pemasukan
    pipeline = [
        {'$match': {'category': {'$regex': 'Penjualan PPOB Shift', '$options': 'i'}}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    result = await db.transactions.aggregate(pipeline).to_list(1)
    total_pemasukan = result[0]['total'] if result else 0
    
    print(f"✓ PPOB Loket Shift Reports: {loket_shifts}")
    print(f"✓ PPOB Accounting Transactions: {ppob_txns}")
    print(f"✓ Total Pemasukan PPOB: Rp {total_pemasukan:,.0f}")
    print(f"\n✅ Realistic data seeding completed!")
    print("=" * 70)
    
    print("\n💡 CATATAN PENTING:")
    print("   - Saldo Awal + Inject = MODAL (bukan pemasukan)")
    print("   - Data Lunas = PEMASUKAN (hasil penjualan)")
    print("   - Sisa Setoran = Uang yang belum disetor ke kasir")
    print("   - Saldo Akhir = Sisa modal setelah transaksi")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
