"""
Script untuk generate mock data realistic yang bisa di-update real-time
Run: python3 /app/scripts/seed_realistic_data.py
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
from pathlib import Path
import os

# Import utils
from utils.helpers import generate_id, generate_code, utc_now
from utils.auth import get_password_hash

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Data references
BUSINESS_CATEGORIES = ['PPOB', 'PLN Installation', 'Travel Umroh', 'PDAM', 'Inventory']
SERVICE_TYPES = {
    'PPOB': ['Pulsa', 'Listrik Token', 'BPJS', 'Internet', 'TV Kabel'],
    'PLN Installation': ['NIDI', 'SLO', 'Pasang Baru', 'Tambah Daya'],
    'Travel Umroh': ['Paket Reguler', 'Paket Premium', 'Paket VIP'],
    'PDAM': ['Pasang Baru', 'Balik Nama', 'Pencatatan Meter'],
    'Inventory': ['Kabel Listrik', 'MCB', 'Stop Kontak', 'Lampu LED']
}

CUSTOMER_NAMES = [
    'Budi Santoso', 'Siti Aminah', 'Agus Prasetyo', 'Dewi Lestari', 'Joko Widodo',
    'Rina Susanti', 'Bambang Hermawan', 'Sri Mulyani', 'Hendra Gunawan', 'Lina Marlina',
    'Andi Wijaya', 'Maya Sari', 'Dedi Firmansyah', 'Ningsih Wati', 'Rudi Hartono',
    'Yuni Astuti', 'Eko Prasetyo', 'Fitri Handayani', 'Irfan Hakim', 'Nurul Hidayah'
]

TEKNISI_NOTES = [
    'Lokasi mudah diakses, pekerjaan lancar',
    'Butuh material tambahan dari gudang',
    'Customer sangat kooperatif',
    'Kendala cuaca hujan, pekerjaan tertunda',
    'Instalasi selesai dengan baik',
    'Perlu koordinasi dengan PLN',
    'Material lengkap, pekerjaan cepat',
    'Komplain minor sudah diselesaikan'
]

BANK_NAMES = ['BRIS', 'MANDIRI', 'BCA', 'BNI', 'BSI']

async def clear_operational_data():
    """Clear existing operational data (keep users & roles)"""
    print("🧹 Clearing existing operational data...")
    
    collections = [
        'businesses', 'orders', 'transactions', 
        'loket_daily_reports', 'kasir_daily_reports',
        'activity_logs', 'notifications'
    ]
    
    for collection in collections:
        result = await db[collection].delete_many({})
        print(f"   Deleted {result.deleted_count} documents from {collection}")

async def seed_users():
    """Create users for all roles"""
    print("\n👥 Creating users...")
    
    # Check if users exist
    existing_count = await db.users.count_documents({})
    if existing_count > 0:
        print(f"   Users already exist ({existing_count}), skipping...")
        return
    
    users = [
        {
            'id': generate_id(),
            'username': 'owner',
            'email': 'owner@gelis.com',
            'password': get_password_hash('owner123'),
            'full_name': 'Owner GELIS',
            'phone': '081234567890',
            'role_id': 1,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'manager',
            'email': 'manager@gelis.com',
            'password': get_password_hash('manager123'),
            'full_name': 'Manager Operasional',
            'phone': '081234567891',
            'role_id': 2,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'finance',
            'email': 'finance@gelis.com',
            'password': get_password_hash('finance123'),
            'full_name': 'Finance Staff',
            'phone': '081234567892',
            'role_id': 3,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'kasir1',
            'email': 'kasir1@gelis.com',
            'password': get_password_hash('kasir123'),
            'full_name': 'Kasir Utama',
            'phone': '081234567893',
            'role_id': 5,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'loket1',
            'email': 'loket1@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Petugas Loket 1',
            'phone': '081234567894',
            'role_id': 6,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'loket2',
            'email': 'loket2@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Petugas Loket 2',
            'phone': '081234567895',
            'role_id': 6,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'teknisi1',
            'email': 'teknisi1@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Agus Teknisi',
            'phone': '081234567896',
            'role_id': 7,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        },
        {
            'id': generate_id(),
            'username': 'teknisi2',
            'email': 'teknisi2@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Budi Teknisi',
            'phone': '081234567897',
            'role_id': 7,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        }
    ]
    
    await db.users.insert_many(users)
    print(f"   ✅ Created {len(users)} users")
    return users

async def seed_businesses(owner_id):
    """Create realistic businesses"""
    print("\n🏢 Creating businesses...")
    
    businesses = []
    for category in BUSINESS_CATEGORIES:
        business = {
            'id': generate_id(),
            'name': f'Unit {category}',
            'category': category,
            'description': f'Unit bisnis untuk layanan {category}',
            'address': f'Jl. Bisnis {category} No. {random.randint(10, 99)}',
            'phone': f'021{random.randint(1000000, 9999999)}',
            'email': f'{category.lower().replace(" ", "")}@gelis.com',
            'settings': {
                'commission_rate': random.uniform(0.02, 0.10),
                'banks': random.sample(BANK_NAMES, 2)
            },
            'is_active': True,
            'created_by': owner_id,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat()
        }
        businesses.append(business)
    
    await db.businesses.insert_many(businesses)
    print(f"   ✅ Created {len(businesses)} businesses")
    return businesses

async def seed_orders(businesses, users):
    """Create realistic orders for the last 30 days"""
    print("\n📦 Creating orders...")
    
    teknisi_users = [u for u in users if u['role_id'] == 7]
    if not teknisi_users:
        teknisi_users = [users[0]]  # fallback to first user
    cs_users = [u for u in users if u['role_id'] == 4]
    if not cs_users:
        cs_users = [users[0]]  # fallback to first user
    
    orders = []
    
    # Generate orders for last 30 days
    for day_offset in range(30):
        target_date = datetime.now() - timedelta(days=day_offset)
        
        # Random number of orders per day (5-20)
        num_orders = random.randint(5, 20)
        
        for _ in range(num_orders):
            business = random.choice(businesses)
            service_type = random.choice(SERVICE_TYPES[business['category']])
            customer_name = random.choice(CUSTOMER_NAMES)
            
            # Random status distribution
            status_weights = [0.1, 0.3, 0.5, 0.1]  # pending, processing, completed, cancelled
            status = random.choices(['pending', 'processing', 'completed', 'cancelled'], weights=status_weights)[0]
            
            payment_status = 'paid' if status == 'completed' else random.choice(['unpaid', 'partial', 'paid'])
            
            amount = random.uniform(50000, 5000000)
            paid_amount = amount if payment_status == 'paid' else (amount * 0.5 if payment_status == 'partial' else 0)
            
            order = {
                'id': generate_id(),
                'order_number': generate_code('ORD', 12),
                'business_id': business['id'],
                'customer_name': customer_name,
                'customer_phone': f'08{random.randint(100000000, 999999999)}',
                'customer_email': f'{customer_name.lower().replace(" ", ".")}@email.com',
                'service_type': service_type,
                'order_details': {
                    'progress': 0 if status == 'pending' else (100 if status == 'completed' else random.randint(20, 80)),
                    'notes': random.choice(TEKNISI_NOTES) if status != 'pending' else ''
                },
                'total_amount': amount,
                'paid_amount': paid_amount,
                'payment_method': random.choice(['cash', 'transfer', 'qris', 'card']) if paid_amount > 0 else None,
                'notes': f'Order untuk {service_type}',
                'status': status,
                'payment_status': payment_status,
                'assigned_to': random.choice(teknisi_users)['id'] if status != 'pending' else None,
                'completion_date': target_date.isoformat() if status == 'completed' else None,
                'created_by': random.choice(cs_users)['id'],
                'created_at': target_date.replace(hour=random.randint(8, 17), minute=random.randint(0, 59)).isoformat(),
                'updated_at': target_date.replace(hour=random.randint(8, 17), minute=random.randint(0, 59)).isoformat()
            }
            
            orders.append(order)
    
    await db.orders.insert_many(orders)
    print(f"   ✅ Created {len(orders)} orders")
    return orders

async def seed_transactions(businesses, orders, users):
    """Create transactions based on orders"""
    print("\n💰 Creating transactions...")
    
    transactions = []
    
    for order in orders:
        if order['paid_amount'] > 0:
            # Create income transaction for paid order
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TRX', 12),
                'business_id': order['business_id'],
                'transaction_type': 'income',
                'category': 'Order Payment',
                'description': f"Pembayaran {order['service_type']} - {order['customer_name']}",
                'amount': order['paid_amount'],
                'payment_method': order['payment_method'],
                'reference_number': order['order_number'],
                'order_id': order['id'],
                'created_by': order['created_by'],
                'created_at': order['created_at']
            }
            transactions.append(transaction)
    
    # Add random expenses (10-20 per business)
    for business in businesses:
        for _ in range(random.randint(10, 20)):
            expense_date = datetime.now() - timedelta(days=random.randint(0, 30))
            expense_categories = ['Material', 'Transport', 'Maintenance', 'Office Supply', 'Utilities']
            
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TRX', 12),
                'business_id': business['id'],
                'transaction_type': 'expense',
                'category': random.choice(expense_categories),
                'description': f'Biaya {random.choice(expense_categories)}',
                'amount': random.uniform(50000, 500000),
                'payment_method': random.choice(['cash', 'transfer']),
                'reference_number': None,
                'order_id': None,
                'created_by': users[0]['id'],
                'created_at': expense_date.isoformat()
            }
            transactions.append(transaction)
    
    # Add transfer transactions (5-10 per business)
    for business in businesses:
        for _ in range(random.randint(5, 10)):
            transfer_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TRX', 12),
                'business_id': business['id'],
                'transaction_type': 'transfer',
                'category': 'Topup Loket',
                'description': f'Transfer topup ke loket',
                'amount': random.uniform(1000000, 20000000),
                'payment_method': 'transfer',
                'reference_number': None,
                'order_id': None,
                'created_by': users[0]['id'],
                'created_at': transfer_date.isoformat()
            }
            transactions.append(transaction)
    
    await db.transactions.insert_many(transactions)
    print(f"   ✅ Created {len(transactions)} transactions")
    return transactions

async def seed_reports(businesses, users):
    """Create realistic daily reports for loket and kasir"""
    print("\n📊 Creating daily reports...")
    
    loket_users = [u for u in users if u['role_id'] == 6]
    kasir_users = [u for u in users if u['role_id'] == 5]
    
    loket_reports = []
    kasir_reports = []
    
    # Generate reports for last 30 days
    for day_offset in range(30):
        target_date = datetime.now() - timedelta(days=day_offset)
        
        for business in businesses:
            # Loket reports (1-3 shifts per day)
            num_shifts = random.randint(1, 3)
            for shift in range(1, num_shifts + 1):
                loket_user = random.choice(loket_users)
                
                # Generate bank balances
                bank_balances = []
                total_setoran = 0
                
                for bank in business['settings'].get('banks', ['BRIS', 'MANDIRI']):
                    saldo_awal = random.uniform(100000000, 500000000)
                    saldo_inject = random.uniform(0, 10000000)
                    data_lunas = random.uniform(500000, 5000000)
                    setor_kasir = random.uniform(0, 1000000)
                    transfer_amount = random.uniform(0, 2000000)
                    sisa_setoran = data_lunas - setor_kasir - transfer_amount
                    saldo_akhir = saldo_awal + saldo_inject - sisa_setoran
                    uang_lebih = random.uniform(0, 10000) if random.random() > 0.7 else 0
                    
                    total_setoran += sisa_setoran
                    
                    bank_balances.append({
                        'bank_name': bank,
                        'saldo_awal': saldo_awal,
                        'saldo_inject': saldo_inject,
                        'data_lunas': data_lunas,
                        'setor_kasir': setor_kasir,
                        'transfer_amount': transfer_amount,
                        'sisa_setoran': sisa_setoran,
                        'saldo_akhir': saldo_akhir,
                        'uang_lebih': uang_lebih
                    })
                
                loket_report = {
                    'id': generate_id(),
                    'business_id': business['id'],
                    'report_date': target_date.isoformat(),
                    'nama_petugas': loket_user['full_name'],
                    'shift': shift,
                    'bank_balances': bank_balances,
                    'total_setoran_shift': total_setoran,
                    'notes': f'Laporan shift {shift} - operasional normal',
                    'created_by': loket_user['id'],
                    'created_at': target_date.replace(hour=8+shift*4, minute=0).isoformat()
                }
                
                loket_reports.append(loket_report)
            
            # Kasir report (1 per day per business)
            kasir_user = random.choice(kasir_users) if kasir_users else users[0]
            
            setoran_pagi = random.uniform(10000000, 30000000)
            setoran_siang = random.uniform(5000000, 20000000)
            setoran_sore = random.uniform(8000000, 25000000)
            setoran_deposit = random.uniform(10000000, 25000000)
            pelunasan_pagi = random.uniform(1000000, 5000000)
            pelunasan_siang = random.uniform(500000, 3000000)
            
            # Generate topup transactions
            num_topup = random.randint(3, 10)
            topup_transactions = []
            for i in range(num_topup):
                topup_transactions.append({
                    'amount': random.uniform(2000000, 20000000),
                    'description': f'Transfer topup loket {i+1}'
                })
            
            total_topup = sum(t['amount'] for t in topup_transactions)
            penerimaan_kas = random.uniform(50000, 200000)
            pengurangan_kas = random.uniform(10000, 50000)
            belanja_loket = random.uniform(50000, 500000)
            total_kas_kecil = penerimaan_kas - pengurangan_kas - belanja_loket
            
            penerimaan_admin = random.uniform(100000, 500000)
            total_admin = penerimaan_admin
            saldo_bank = random.uniform(50000000, 200000000)
            saldo_brankas = penerimaan_admin
            
            kasir_report = {
                'id': generate_id(),
                'business_id': business['id'],
                'report_date': target_date.isoformat(),
                'setoran_pagi': setoran_pagi,
                'setoran_siang': setoran_siang,
                'setoran_sore': setoran_sore,
                'setoran_deposit_loket_luar': setoran_deposit,
                'setoran_pelunasan_pagi': pelunasan_pagi,
                'setoran_pelunasan_siang': pelunasan_siang,
                'topup_transactions': topup_transactions,
                'total_topup': total_topup,
                'penerimaan_kas_kecil': penerimaan_kas,
                'pengurangan_kas_kecil': pengurangan_kas,
                'belanja_loket': belanja_loket,
                'total_kas_kecil': total_kas_kecil,
                'penerimaan_admin': penerimaan_admin,
                'total_admin': total_admin,
                'saldo_bank': saldo_bank,
                'saldo_brankas': saldo_brankas,
                'notes': 'Laporan harian kasir - operasional normal',
                'created_by': kasir_user['id'],
                'created_at': target_date.replace(hour=17, minute=0).isoformat()
            }
            
            kasir_reports.append(kasir_report)
    
    if loket_reports:
        await db.loket_daily_reports.insert_many(loket_reports)
        print(f"   ✅ Created {len(loket_reports)} loket reports")
    
    if kasir_reports:
        await db.kasir_daily_reports.insert_many(kasir_reports)
        print(f"   ✅ Created {len(kasir_reports)} kasir reports")

async def main():
    print("=" * 60)
    print("🚀 GELIS - Realistic Data Seeding")
    print("=" * 60)
    
    try:
        # Check if roles exist
        role_count = await db.roles.count_documents({})
        if role_count == 0:
            print("\n⚠️  Roles tidak ditemukan. Jalankan /api/init-data terlebih dahulu!")
            return
        
        # Seed users
        users = await seed_users()
        if not users:
            users = await db.users.find({}, {'_id': 0}).to_list(100)
        
        owner = next((u for u in users if u['role_id'] == 1), users[0])
        
        # Clear old operational data
        await clear_operational_data()
        
        # Seed data
        businesses = await seed_businesses(owner['id'])
        orders = await seed_orders(businesses, users)
        transactions = await seed_transactions(businesses, orders, users)
        await seed_reports(businesses, users)
        
        print("\n" + "=" * 60)
        print("✅ Data seeding completed successfully!")
        print("=" * 60)
        print("\n📋 Summary:")
        print(f"   • Users: {len(users)}")
        print(f"   • Businesses: {len(businesses)}")
        print(f"   • Orders: {len(orders)}")
        print(f"   • Transactions: {len(transactions)}")
        print("\n🔑 Login Credentials:")
        print("   • Owner: owner / owner123")
        print("   • Manager: manager / manager123")
        print("   • Finance: finance / finance123")
        print("   • Kasir: kasir1 / kasir123")
        print("   • Loket: loket1 / loket123")
        print("   • Teknisi: teknisi1 / teknisi123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(main())
