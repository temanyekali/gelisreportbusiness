"""
Script untuk generate mock data PPOB dan Akunting yang realistic
Run: python3 /app/scripts/seed_ppob_accounting.py
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

# PPOB Products dengan harga realistic
PPOB_PRODUCTS = {
    'Pulsa': [
        {'nominal': 5000, 'harga': 5500},
        {'nominal': 10000, 'harga': 10500},
        {'nominal': 20000, 'harga': 20500},
        {'nominal': 25000, 'harga': 25500},
        {'nominal': 50000, 'harga': 50500},
        {'nominal': 100000, 'harga': 100500},
    ],
    'Listrik Token': [
        {'nominal': 20000, 'harga': 20500},
        {'nominal': 50000, 'harga': 50500},
        {'nominal': 100000, 'harga': 100500},
        {'nominal': 200000, 'harga': 200500},
        {'nominal': 500000, 'harga': 500500},
    ],
    'Paket Data': [
        {'nama': '1GB', 'harga': 15000},
        {'nama': '2GB', 'harga': 25000},
        {'nama': '5GB', 'harga': 45000},
        {'nama': '10GB', 'harga': 75000},
        {'nama': 'Unlimited', 'harga': 100000},
    ],
    'BPJS': [
        {'kelas': 'Kelas 1', 'harga': 150000},
        {'kelas': 'Kelas 2', 'harga': 100000},
        {'kelas': 'Kelas 3', 'harga': 35000},
    ],
}

PETUGAS_LOKET = ['Andi', 'Budi', 'Citra', 'Dewi']

async def clear_ppob_accounting_data():
    """Clear PPOB and accounting data"""
    print("🧹 Clearing PPOB and accounting data...")
    
    collections = [
        'ppob_loket_shifts',
        'ppob_kasir_reports',
        'transactions',
        'universal_income',
        'universal_expense'
    ]
    
    for collection in collections:
        result = await db[collection].delete_many({})
        print(f"   Deleted {result.deleted_count} documents from {collection}")

async def get_ppob_business():
    """Get PPOB business"""
    business = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if not business:
        print("❌ PPOB business not found!")
        return None
    return business

async def seed_ppob_shift_reports():
    """Generate realistic PPOB shift reports"""
    print("\n📊 Generating PPOB shift reports...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Generate for last 30 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)
    
    shift_count = 0
    
    current_date = start_date
    while current_date <= end_date:
        # 2 shift per hari
        for shift in [1, 2]:
            petugas = random.choice(PETUGAS_LOKET)
            
            # Generate penjualan per channel
            channels = []
            total_penjualan_shift = 0
            
            # Pulsa
            pulsa_trx = random.randint(15, 40)
            pulsa_total = sum(random.choice(PPOB_PRODUCTS['Pulsa'])['harga'] for _ in range(pulsa_trx))
            channels.append({
                'nama_channel': 'Pulsa',
                'saldo_awal': 500000,
                'saldo_inject': 0,
                'jumlah_transaksi': pulsa_trx,
                'total_penjualan': pulsa_total,
                'sisa_setoran': pulsa_total,
                'saldo_akhir': 500000 - pulsa_total
            })
            total_penjualan_shift += pulsa_total
            
            # Listrik Token
            listrik_trx = random.randint(20, 50)
            listrik_total = sum(random.choice(PPOB_PRODUCTS['Listrik Token'])['harga'] for _ in range(listrik_trx))
            channels.append({
                'nama_channel': 'Listrik Token',
                'saldo_awal': 1000000,
                'saldo_inject': 0,
                'jumlah_transaksi': listrik_trx,
                'total_penjualan': listrik_total,
                'sisa_setoran': listrik_total,
                'saldo_akhir': 1000000 - listrik_total
            })
            total_penjualan_shift += listrik_total
            
            # Paket Data
            data_trx = random.randint(10, 25)
            data_total = sum(random.choice(PPOB_PRODUCTS['Paket Data'])['harga'] for _ in range(data_trx))
            channels.append({
                'nama_channel': 'Paket Data',
                'saldo_awal': 300000,
                'saldo_inject': 0,
                'jumlah_transaksi': data_trx,
                'total_penjualan': data_total,
                'sisa_setoran': data_total,
                'saldo_akhir': 300000 - data_total
            })
            total_penjualan_shift += data_total
            
            # BPJS
            bpjs_trx = random.randint(3, 10)
            bpjs_total = sum(random.choice(PPOB_PRODUCTS['BPJS'])['harga'] for _ in range(bpjs_trx))
            channels.append({
                'nama_channel': 'BPJS',
                'saldo_awal': 500000,
                'saldo_inject': 0,
                'jumlah_transaksi': bpjs_trx,
                'total_penjualan': bpjs_total,
                'sisa_setoran': bpjs_total,
                'saldo_akhir': 500000 - bpjs_total
            })
            total_penjualan_shift += bpjs_total
            
            # Create shift report
            shift_report = {
                'id': generate_id(),
                'tanggal': current_date.strftime('%Y-%m-%d'),
                'shift': shift,
                'nama_petugas': petugas,
                'channels': channels,
                'total_penjualan': total_penjualan_shift,
                'total_sisa_setoran': total_penjualan_shift,
                'status_setoran': 'Sudah Disetor',
                'created_by': 'system',
                'created_at': current_date.isoformat()
            }
            
            await db.ppob_loket_shifts.insert_one(shift_report)
            
            # Create accounting transaction (AKUMULASI PER SHIFT)
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'business_id': ppob_business['id'],
                'transaction_type': 'income',
                'category': f'Penjualan PPOB Shift {shift}',
                'description': f'Akumulasi penjualan PPOB Shift {shift} - {petugas} (Pulsa: {pulsa_trx}x, Token: {listrik_trx}x, Data: {data_trx}x, BPJS: {bpjs_trx}x)',
                'amount': total_penjualan_shift,
                'payment_method': 'cash',
                'reference_number': f'PPOB-SHIFT-{current_date.strftime("%Y%m%d")}-{shift}',
                'order_id': None,
                'created_by': 'system',
                'created_at': current_date.isoformat()
            }
            
            await db.transactions.insert_one(transaction)
            shift_count += 1
        
        current_date += timedelta(days=1)
    
    print(f"   ✓ Generated {shift_count} PPOB shift reports with accounting entries")

async def seed_other_business_transactions():
    """Generate realistic transactions for other businesses"""
    print("\n💰 Generating transactions for other businesses...")
    
    businesses = await db.businesses.find({'category': {'$ne': 'PPOB'}}, {'_id': 0}).to_list(100)
    
    if not businesses:
        print("   ⚠ No other businesses found")
        return
    
    txn_count = 0
    
    for business in businesses:
        # Generate transactions for last 30 days
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        current_date = start_date
        while current_date <= end_date:
            # Random 1-3 transactions per day
            num_txns = random.randint(1, 3)
            
            for _ in range(num_txns):
                # Income
                if random.random() > 0.3:  # 70% income
                    amount = random.randint(500000, 5000000)
                    
                    descriptions = {
                        'PLN Installation': [
                            f'Pembayaran instalasi NIDI - {random.choice(["Rumah", "Ruko", "Pabrik"])}',
                            f'Pembayaran pasang baru {random.randint(450, 2200)}VA',
                            f'Pembayaran SLO instalasi listrik',
                            f'Pembayaran tambah daya {random.randint(900, 5500)}VA'
                        ],
                        'Travel Umroh': [
                            f'DP Paket Umroh {random.choice(["Reguler", "Premium", "VIP"])} - {random.randint(1, 4)} jamaah',
                            f'Pelunasan paket Umroh bulan {current_date.strftime("%B")}',
                            f'Pembayaran cicilan paket Umroh'
                        ],
                        'PDAM': [
                            f'Biaya pencatatan meter PDAM - {random.randint(50, 200)} rumah',
                            f'Biaya pasang baru PDAM',
                            f'Biaya balik nama sambungan PDAM'
                        ],
                        'Inventory': [
                            f'Penjualan material listrik - {random.choice(["Kabel", "MCB", "Stop Kontak", "Lampu"])}',
                            f'Penjualan perlengkapan instalasi',
                            f'Penjualan spare parts'
                        ]
                    }
                    
                    category_desc = descriptions.get(business['category'], ['Pembayaran layanan'])[0]
                    if business['category'] in descriptions:
                        category_desc = random.choice(descriptions[business['category']])
                    
                    transaction = {
                        'id': generate_id(),
                        'transaction_code': generate_code('TXN', 12),
                        'business_id': business['id'],
                        'transaction_type': 'income',
                        'category': 'sales',
                        'description': category_desc,
                        'amount': amount,
                        'payment_method': random.choice(['cash', 'transfer', 'card']),
                        'reference_number': generate_code('INV', 10),
                        'created_by': 'system',
                        'created_at': (current_date + timedelta(hours=random.randint(8, 16))).isoformat()
                    }
                    
                    await db.transactions.insert_one(transaction)
                    txn_count += 1
                
                # Expense
                else:  # 30% expense
                    amount = random.randint(200000, 2000000)
                    
                    expense_categories = {
                        'PLN Installation': [
                            f'Gaji teknisi bulan {current_date.strftime("%B")}',
                            f'Pembelian material instalasi (kabel, MCB, dll)',
                            f'Biaya transportasi teknisi',
                            f'Pemeliharaan peralatan kerja'
                        ],
                        'Travel Umroh': [
                            f'Pembayaran hotel di Saudi Arabia',
                            f'Pembelian tiket pesawat jamaah',
                            f'Biaya handling bandara',
                            f'Biaya tour guide dan muthawif'
                        ],
                        'PDAM': [
                            f'Gaji pencatat meter',
                            f'Biaya transportasi tim pencatat',
                            f'Pembelian alat tulis dan formulir'
                        ],
                        'Inventory': [
                            f'Pembelian stok barang dari supplier',
                            f'Biaya pengiriman barang',
                            f'Sewa gudang penyimpanan'
                        ]
                    }
                    
                    expense_desc = expense_categories.get(business['category'], ['Biaya operasional'])[0]
                    if business['category'] in expense_categories:
                        expense_desc = random.choice(expense_categories[business['category']])
                    
                    transaction = {
                        'id': generate_id(),
                        'transaction_code': generate_code('TXN', 12),
                        'business_id': business['id'],
                        'transaction_type': 'expense',
                        'category': random.choice(['operational', 'salary', 'purchase', 'maintenance']),
                        'description': expense_desc,
                        'amount': amount,
                        'payment_method': random.choice(['cash', 'transfer']),
                        'reference_number': generate_code('EXP', 10),
                        'created_by': 'system',
                        'created_at': (current_date + timedelta(hours=random.randint(8, 16))).isoformat()
                    }
                    
                    await db.transactions.insert_one(transaction)
                    txn_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"   ✓ Generated {txn_count} transactions for {len(businesses)} businesses")

async def main():
    print("=" * 60)
    print("🚀 SEED PPOB & ACCOUNTING DATA - PROFESSIONAL MOCKUP")
    print("=" * 60)
    
    # Clear existing data
    await clear_ppob_accounting_data()
    
    # Seed PPOB shift reports (with accounting entries)
    await seed_ppob_shift_reports()
    
    # Seed other business transactions
    await seed_other_business_transactions()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    ppob_shifts = await db.ppob_loket_shifts.count_documents({})
    transactions = await db.transactions.count_documents({})
    ppob_txns = await db.transactions.count_documents({'business_id': (await get_ppob_business())['id']}) if await get_ppob_business() else 0
    
    print(f"✓ PPOB Shift Reports: {ppob_shifts}")
    print(f"✓ Total Transactions: {transactions}")
    print(f"  - PPOB Transactions (per shift): {ppob_txns}")
    print(f"  - Other Business Transactions: {transactions - ppob_txns}")
    
    print("\n✅ Data seeding completed successfully!")
    print("=" * 60)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
