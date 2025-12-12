"""
Script untuk generate COMPLETE MOCK DATA untuk semua module GELIS
Data realistic, saling terhubung, dan bisa dihapus dengan 1 klik

Run: python3 /app/scripts/seed_complete_mockup.py
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
db = client[os.environ.get('DB_NAME', 'gelis_db')]

# ==================== DATA CONSTANTS ====================

BUSINESS_DATA = [
    {
        'name': 'Loket PPOB Pusat',
        'category': 'PPOB',
        'description': 'Layanan pembayaran PPOB (listrik, air, pulsa, internet, TV kabel)',
        'address': 'Jl. Sudirman No. 123, Jakarta Pusat',
        'phone': '021-12345678',
        'email': 'ppob@gelis.com'
    },
    {
        'name': 'PLN Installation Service',
        'category': 'PLN',
        'description': 'Jasa instalasi listrik rumah dan komersial (NIDI, SLO, Pasang Baru)',
        'address': 'Jl. Gatot Subroto No. 45, Jakarta Selatan',
        'phone': '021-87654321',
        'email': 'pln@gelis.com'
    },
    {
        'name': 'Travel Umroh Barokah',
        'category': 'Travel',
        'description': 'Paket umroh dan haji dengan berbagai pilihan (Reguler, Premium, VIP)',
        'address': 'Jl. MH Thamrin No. 78, Jakarta Pusat',
        'phone': '021-99887766',
        'email': 'umroh@gelis.com'
    },
    {
        'name': 'PDAM Service Center',
        'category': 'PDAM',
        'description': 'Layanan pasang baru, balik nama, dan pencatatan meter PDAM',
        'address': 'Jl. Rasuna Said No. 90, Jakarta Selatan',
        'phone': '021-55443322',
        'email': 'pdam@gelis.com'
    },
    {
        'name': 'Toko Listrik Jaya',
        'category': 'Inventory',
        'description': 'Penjualan material listrik (kabel, MCB, stop kontak, lampu LED)',
        'address': 'Jl. Jend. Sudirman No. 234, Jakarta Barat',
        'phone': '021-66778899',
        'email': 'inventory@gelis.com'
    }
]

SERVICE_TYPES = {
    'PPOB': [
        ('Pulsa Telkomsel', 5000, 50000),
        ('Token Listrik', 20000, 500000),
        ('BPJS Kesehatan', 80000, 150000),
        ('Internet IndiHome', 200000, 500000),
        ('TV Kabel First Media', 150000, 350000),
        ('Pulsa XL', 5000, 50000),
        ('Pulsa Indosat', 5000, 50000),
        ('Pulsa Tri', 5000, 50000),
        ('Pulsa Smartfren', 5000, 50000),
        ('Telkom (Telepon)', 50000, 200000)
    ],
    'PLN': [
        ('NIDI (Nota Izin Dinas Instalasi)', 2000000, 5000000),
        ('SLO (Sertifikat Laik Operasi)', 1500000, 3500000),
        ('Pasang Baru 450VA', 3000000, 4000000),
        ('Pasang Baru 900VA', 4000000, 6000000),
        ('Pasang Baru 1300VA', 5000000, 7500000),
        ('Pasang Baru 2200VA', 7000000, 10000000),
        ('Tambah Daya 900 ke 1300', 2500000, 4000000),
        ('Tambah Daya 1300 ke 2200', 3500000, 5500000),
        ('Instalasi Rumah Sederhana', 5000000, 8000000),
        ('Instalasi Rumah Mewah', 15000000, 30000000)
    ],
    'Travel': [
        ('Paket Umroh Reguler 9 Hari', 25000000, 30000000),
        ('Paket Umroh Premium 12 Hari', 35000000, 40000000),
        ('Paket Umroh VIP 15 Hari', 50000000, 60000000),
        ('Paket Haji Reguler', 45000000, 55000000),
        ('Paket Haji Plus', 75000000, 90000000),
        ('Paket Umroh Ramadhan', 40000000, 50000000)
    ],
    'PDAM': [
        ('Pasang Baru PDAM', 1500000, 3000000),
        ('Balik Nama PDAM', 500000, 1000000),
        ('Pencatatan Meter', 100000, 300000),
        ('Perbaikan Pipa Bocor', 800000, 2000000),
        ('Instalasi Meter Baru', 1200000, 2500000)
    ],
    'Inventory': [
        ('Kabel NYA 1.5mm', 50000, 150000),
        ('Kabel NYM 2x1.5mm', 80000, 200000),
        ('MCB 2A', 25000, 50000),
        ('MCB 4A', 30000, 60000),
        ('MCB 6A', 35000, 70000),
        ('MCB 10A', 40000, 80000),
        ('Stop Kontak Universal', 15000, 35000),
        ('Saklar Engkel', 8000, 20000),
        ('Saklar Seri', 12000, 30000),
        ('Lampu LED 5W', 20000, 40000),
        ('Lampu LED 10W', 30000, 60000),
        ('Lampu LED 15W', 40000, 80000)
    ]
}

CUSTOMER_NAMES = [
    'Budi Santoso', 'Siti Aminah', 'Agus Prasetyo', 'Dewi Lestari', 'Joko Widodo',
    'Rina Susanti', 'Bambang Hermawan', 'Sri Mulyani', 'Hendra Gunawan', 'Lina Marlina',
    'Andi Wijaya', 'Maya Sari', 'Dedi Firmansyah', 'Ningsih Wati', 'Rudi Hartono',
    'Yuni Astuti', 'Eko Prasetyo', 'Fitri Handayani', 'Irfan Hakim', 'Nurul Hidayah',
    'Rahman Abdullah', 'Putri Maharani', 'Tono Suratman', 'Mega Wulandari', 'Adi Nugroho',
    'Ratna Sari', 'Darmawan Putra', 'Indah Permata', 'Gunawan Wijaya', 'Santi Puspita',
    'Budi Haryanto', 'Citra Dewi', 'Eko Susilo', 'Farida Hanum', 'Gita Gutawa',
    'Hadi Pranoto', 'Iis Dahlia', 'Jono Sumarno', 'Kartini Mulia', 'Lestari Indah'
]

CUSTOMER_PHONES = [f'08{random.randint(1000000000, 9999999999)}' for _ in range(len(CUSTOMER_NAMES))]
CUSTOMER_EMAILS = [name.lower().replace(' ', '.') + '@example.com' for name in CUSTOMER_NAMES]

ADDRESSES = [
    'Jl. Merdeka No. 123, Jakarta Pusat',
    'Jl. Sudirman No. 45, Jakarta Selatan',
    'Jl. Gatot Subroto No. 78, Jakarta Barat',
    'Jl. HR Rasuna Said No. 90, Jakarta Timur',
    'Jl. MH Thamrin No. 234, Jakarta Utara',
    'Jl. Kuningan Raya No. 56, Jakarta Selatan',
    'Jl. TB Simatupang No. 12, Jakarta Selatan',
    'Jl. Ahmad Yani No. 89, Bekasi',
    'Jl. Pajajaran No. 45, Bogor',
    'Jl. Raya Serpong No. 123, Tangerang'
]

TEKNISI_NOTES = [
    'Lokasi mudah diakses, pekerjaan lancar dan selesai tepat waktu',
    'Butuh material tambahan dari gudang, sudah koordinasi',
    'Customer sangat kooperatif dan membantu proses instalasi',
    'Kendala cuaca hujan, pekerjaan tertunda 1 hari',
    'Instalasi selesai dengan baik, customer puas',
    'Perlu koordinasi dengan PLN untuk sambungan',
    'Material lengkap, pekerjaan cepat selesai',
    'Komplain minor sudah diselesaikan di tempat',
    'Survei lokasi selesai, menunggu approval',
    'Pekerjaan tambahan disetujui customer'
]

PAYMENT_METHODS = ['Cash', 'Transfer', 'QRIS', 'Debit Card', 'Credit Card']
BANK_NAMES = ['BRIS', 'MANDIRI', 'BCA', 'BNI', 'BSI', 'BRI', 'CIMB', 'Permata']

ORDER_STATUS_FLOW = ['pending', 'processing', 'completed', 'cancelled']

TRANSACTION_TYPES = ['revenue', 'expense']
EXPENSE_CATEGORIES = [
    'Gaji Karyawan', 'Biaya Operasional', 'Pembelian Material', 
    'Biaya Transport', 'Utilitas (Listrik, Air)', 'Marketing',
    'Pemeliharaan Kendaraan', 'Sewa Kantor', 'Pajak', 'Lain-lain'
]

LOYALTY_PROGRAMS = [
    {
        'name': 'Member Gold',
        'description': 'Cashback 5% untuk setiap transaksi diatas Rp 500.000',
        'points_per_transaction': 50,
        'min_transaction': 500000,
        'cashback_percentage': 5,
        'benefits': 'Cashback 5%, Priority Support, Free Konsultasi'
    },
    {
        'name': 'Member Platinum',
        'description': 'Cashback 10% untuk setiap transaksi diatas Rp 2.000.000',
        'points_per_transaction': 100,
        'min_transaction': 2000000,
        'cashback_percentage': 10,
        'benefits': 'Cashback 10%, 24/7 Support, Free Survey, Diskon Material'
    },
    {
        'name': 'Member Diamond',
        'description': 'Cashback 15% untuk setiap transaksi diatas Rp 5.000.000',
        'points_per_transaction': 200,
        'min_transaction': 5000000,
        'cashback_percentage': 15,
        'benefits': 'Cashback 15%, Dedicated Account Manager, Free Maintenance'
    }
]

CSR_PROGRAMS = [
    {
        'name': 'Bantuan Instalasi Listrik Gratis untuk Dhuafa',
        'description': 'Program bantuan instalasi listrik gratis untuk keluarga kurang mampu',
        'target_beneficiaries': 50,
        'budget': 25000000,
        'category': 'Sosial'
    },
    {
        'name': 'Pelatihan Teknisi Listrik untuk Pemuda',
        'description': 'Program pelatihan gratis teknisi listrik untuk pemuda putus sekolah',
        'target_beneficiaries': 30,
        'budget': 15000000,
        'category': 'Pendidikan'
    },
    {
        'name': 'Beasiswa Anak Karyawan Berprestasi',
        'description': 'Beasiswa pendidikan untuk anak karyawan yang berprestasi',
        'target_beneficiaries': 20,
        'budget': 40000000,
        'category': 'Pendidikan'
    }
]

# ==================== HELPER FUNCTIONS ====================

def random_date(start_days_ago=60, end_days_ago=0):
    """Generate random datetime within range"""
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = end - start
    random_days = random.random() * delta.days
    random_seconds = random.random() * 86400
    return start + timedelta(days=random_days, seconds=random_seconds)

def random_time_today():
    """Generate random time today"""
    now = datetime.now()
    random_hour = random.randint(8, 17)
    random_minute = random.randint(0, 59)
    return now.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

# ==================== SEED FUNCTIONS ====================

async def clear_all_data():
    """Clear ALL data including users (for fresh start)"""
    print("🧹 Clearing ALL existing data...")
    
    collections = [
        'users', 'roles', 'businesses', 'orders', 'accounting',
        'loket_reports', 'kasir_reports', 'loyalty_programs', 
        'loyalty_members', 'csr_programs', 'activity_logs', 
        'settings', 'notifications'
    ]
    
    for collection in collections:
        result = await db[collection].delete_many({})
        print(f"   ✓ Deleted {result.deleted_count} documents from {collection}")

async def seed_roles():
    """Create all roles"""
    print("\n👑 Creating roles...")
    
    roles = [
        {'id': 1, 'name': 'Owner', 'description': 'Pemilik sistem dengan akses penuh', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 2, 'name': 'Manager', 'description': 'Manajer operasional', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 3, 'name': 'Finance', 'description': 'Staff keuangan', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 4, 'name': 'Customer Service', 'description': 'Customer Service / Admin', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 5, 'name': 'Kasir', 'description': 'Kasir', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 6, 'name': 'Loket', 'description': 'Petugas Loket', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 7, 'name': 'Teknisi', 'description': 'Teknisi Lapangan', 'permissions': {}, 'created_at': utc_now().isoformat()},
    ]
    
    await db.roles.insert_many(roles)
    print(f"   ✓ Created {len(roles)} roles")

async def seed_users():
    """Create users for all roles"""
    print("\n👥 Creating users...")
    
    users = [
        # Owner
        {
            'id': generate_id(),
            'username': 'owner',
            'email': 'owner@gelis.com',
            'password': get_password_hash('owner123'),
            'full_name': 'Pak Budi Santoso (Owner)',
            'phone': '081234567890',
            'role_id': 1,
            'is_active': True,
            'is_mock': False,  # Owner is NOT mock data
            'created_at': (datetime.now() - timedelta(days=90)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': utc_now().isoformat()
        },
        # Manager
        {
            'id': generate_id(),
            'username': 'manager',
            'email': 'manager@gelis.com',
            'password': get_password_hash('manager123'),
            'full_name': 'Ibu Siti Aminah (Manager)',
            'phone': '081234567891',
            'role_id': 2,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=85)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=2)).isoformat()
        },
        # Finance
        {
            'id': generate_id(),
            'username': 'finance',
            'email': 'finance@gelis.com',
            'password': get_password_hash('finance123'),
            'full_name': 'Dewi Lestari (Finance)',
            'phone': '081234567892',
            'role_id': 3,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=80)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=5)).isoformat()
        },
        # Customer Service / Admin
        {
            'id': generate_id(),
            'username': 'admin1',
            'email': 'admin1@gelis.com',
            'password': get_password_hash('admin123'),
            'full_name': 'Agus Prasetyo (Admin)',
            'phone': '081234567893',
            'role_id': 4,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=75)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=1)).isoformat()
        },
        # Kasir (3 users)
        {
            'id': generate_id(),
            'username': 'kasir1',
            'email': 'kasir1@gelis.com',
            'password': get_password_hash('kasir123'),
            'full_name': 'Rina Susanti (Kasir 1)',
            'phone': '081234567894',
            'role_id': 5,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=70)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': utc_now().isoformat()
        },
        {
            'id': generate_id(),
            'username': 'kasir2',
            'email': 'kasir2@gelis.com',
            'password': get_password_hash('kasir123'),
            'full_name': 'Bambang Hermawan (Kasir 2)',
            'phone': '081234567895',
            'role_id': 5,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=65)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(days=1)).isoformat()
        },
        {
            'id': generate_id(),
            'username': 'kasir3',
            'email': 'kasir3@gelis.com',
            'password': get_password_hash('kasir123'),
            'full_name': 'Sri Mulyani (Kasir 3)',
            'phone': '081234567896',
            'role_id': 5,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=60)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=3)).isoformat()
        },
        # Loket (3 users)
        {
            'id': generate_id(),
            'username': 'loket1',
            'email': 'loket1@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Hendra Gunawan (Loket 1)',
            'phone': '081234567897',
            'role_id': 6,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=55)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': utc_now().isoformat()
        },
        {
            'id': generate_id(),
            'username': 'loket2',
            'email': 'loket2@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Lina Marlina (Loket 2)',
            'phone': '081234567898',
            'role_id': 6,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=50)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=4)).isoformat()
        },
        {
            'id': generate_id(),
            'username': 'loket3',
            'email': 'loket3@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Andi Wijaya (Loket 3)',
            'phone': '081234567899',
            'role_id': 6,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=45)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(days=2)).isoformat()
        },
        # Teknisi (4 users)
        {
            'id': generate_id(),
            'username': 'teknisi1',
            'email': 'teknisi1@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Dedi Firmansyah (Teknisi 1)',
            'phone': '081234567800',
            'role_id': 7,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=40)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': utc_now().isoformat()
        },
        {
            'id': generate_id(),
            'username': 'teknisi2',
            'email': 'teknisi2@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Rudi Hartono (Teknisi 2)',
            'phone': '081234567801',
            'role_id': 7,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=35)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=6)).isoformat()
        },
        {
            'id': generate_id(),
            'username': 'teknisi3',
            'email': 'teknisi3@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Eko Prasetyo (Teknisi 3)',
            'phone': '081234567802',
            'role_id': 7,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(hours=8)).isoformat()
        },
        {
            'id': generate_id(),
            'username': 'teknisi4',
            'email': 'teknisi4@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Irfan Hakim (Teknisi 4)',
            'phone': '081234567803',
            'role_id': 7,
            'is_active': True,
            'is_mock': True,
            'created_at': (datetime.now() - timedelta(days=25)).isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
    
    await db.users.insert_many(users)
    print(f"   ✓ Created {len(users)} users (1 Owner + {len(users)-1} mock users)")
    
    return users

async def seed_businesses(owner_id):
    """Create businesses"""
    print("\n🏢 Creating businesses...")
    
    businesses = []
    for biz_data in BUSINESS_DATA:
        business = {
            'id': generate_id(),
            'name': biz_data['name'],
            'category': biz_data['category'],
            'description': biz_data['description'],
            'address': biz_data['address'],
            'phone': biz_data['phone'],
            'email': biz_data['email'],
            'settings': {'commission_rate': round(random.uniform(0.03, 0.08), 2)},
            'is_active': True,
            'is_mock': True,
            'created_by': owner_id,
            'created_at': random_date(80, 60).isoformat(),
            'updated_at': utc_now().isoformat()
        }
        businesses.append(business)
    
    await db.businesses.insert_many(businesses)
    print(f"   ✓ Created {len(businesses)} businesses")
    
    return businesses

async def seed_orders(businesses, users):
    """Create realistic orders with various statuses"""
    print("\n📦 Creating orders...")
    
    # Get teknisi users
    teknisi_users = [u for u in users if u['role_id'] == 7]
    loket_users = [u for u in users if u['role_id'] == 6]
    
    orders = []
    order_count = 0
    
    # Generate orders for last 60 days
    for days_ago in range(60, -1, -1):
        # Random 3-8 orders per day
        daily_orders = random.randint(3, 8)
        
        for _ in range(daily_orders):
            business = random.choice(businesses)
            service_name, min_amount, max_amount = random.choice(SERVICE_TYPES[business['category']])
            
            # Random customer
            customer_idx = random.randint(0, len(CUSTOMER_NAMES) - 1)
            customer_name = CUSTOMER_NAMES[customer_idx]
            customer_phone = CUSTOMER_PHONES[customer_idx]
            customer_email = CUSTOMER_EMAILS[customer_idx]
            
            total_amount = random.randint(min_amount, max_amount)
            paid_amount = total_amount if random.random() > 0.3 else random.randint(int(total_amount * 0.3), int(total_amount * 0.7))
            
            # Status distribution
            if days_ago > 7:
                status = random.choices(['completed', 'cancelled'], weights=[0.9, 0.1])[0]
            elif days_ago > 2:
                status = random.choices(['completed', 'processing', 'cancelled'], weights=[0.7, 0.2, 0.1])[0]
            else:
                status = random.choices(['pending', 'processing', 'completed'], weights=[0.3, 0.4, 0.3])[0]
            
            order_date = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            # Determine if needs technician
            requires_technician = business['category'] in ['PLN', 'PDAM']
            assigned_technician = random.choice(teknisi_users)['id'] if requires_technician else None
            
            # Auto-set payment status based on paid_amount (consistent with server.py logic)
            if paid_amount >= total_amount:
                payment_status = 'paid'
            elif paid_amount > 0:
                payment_status = 'partial'
            else:
                payment_status = 'unpaid'
            
            order = {
                'id': generate_id(),
                'order_number': generate_code('ORD'),
                'business_id': business['id'],
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'customer_email': customer_email,
                'customer_address': random.choice(ADDRESSES),
                'service_type': service_name,
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'payment_method': random.choice(PAYMENT_METHODS),
                'payment_status': payment_status,  # Added payment_status field
                'status': status,
                'notes': f'Order {service_name} untuk {customer_name}',
                'requires_technician': requires_technician,
                'assigned_technician_id': assigned_technician,
                'order_details': {
                    'progress': 100 if status == 'completed' else (50 if status == 'processing' else 0),
                    'technician_notes': random.choice(TEKNISI_NOTES) if requires_technician and status in ['processing', 'completed'] else None,
                    'completion_date': (order_date + timedelta(days=random.randint(1, 7))).isoformat() if status == 'completed' else None
                },
                'is_mock': True,
                'created_by': random.choice(loket_users)['id'],
                'created_at': order_date.isoformat(),
                'updated_at': (order_date + timedelta(hours=random.randint(1, 48))).isoformat()
            }
            
            orders.append(order)
            order_count += 1
    
    await db.orders.insert_many(orders)
    print(f"   ✓ Created {order_count} orders")
    
    return orders

async def seed_transactions(businesses, orders, users):
    """Create accounting transactions - TERHUBUNG dengan orders secara real-time"""
    print("\n💰 Creating transactions...")
    
    transactions = []
    
    # AUTO-CREATE income transactions from ALL PAID ORDERS (realistic sync)
    for order in orders:
        if order.get('paid_amount', 0) > 0:  # Any payment creates transaction
            business = next(b for b in businesses if b['id'] == order['business_id'])
            
            # Income transaction (follows same logic as server.py)
            trans = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN'),
                'business_id': business['id'],
                'transaction_type': 'income',  # Changed to match server.py
                'category': 'Order Payment',  # Consistent with auto-create in server.py
                'amount': order['paid_amount'],
                'description': f"Pembayaran order {order['order_number']} - {order['customer_name']}",
                'payment_method': order.get('payment_method', 'cash'),
                'reference_number': order['order_number'],
                'order_id': order['id'],  # Links back to order
                'is_mock': True,
                'created_by': order['created_by'],
                'created_at': order['created_at']
            }
            transactions.append(trans)
    
    # Expense transactions (operating costs)
    finance_user = next(u for u in users if u['role_id'] == 3)
    
    for days_ago in range(60, -1, -1):
        # Random 1-3 expenses per day
        daily_expenses = random.randint(1, 3)
        
        for _ in range(daily_expenses):
            business = random.choice(businesses)
            category = random.choice(EXPENSE_CATEGORIES)
            
            # Amount based on category
            if 'Gaji' in category:
                amount = random.randint(5000000, 15000000)
            elif 'Material' in category:
                amount = random.randint(2000000, 8000000)
            elif 'Sewa' in category:
                amount = random.randint(3000000, 10000000)
            else:
                amount = random.randint(500000, 3000000)
            
            trans_date = (datetime.now() - timedelta(days=days_ago)).replace(
                hour=random.randint(8, 17),
                minute=random.randint(0, 59)
            )
            
            trans = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN'),  # Consistent field name
                'business_id': business['id'],
                'transaction_type': 'expense',
                'category': category,
                'amount': amount,
                'description': f"{category} - {business['name']}",
                'payment_method': random.choice(['cash', 'transfer']),  # Lowercase for consistency
                'reference_number': generate_code('EXP'),
                'order_id': None,  # No related order for expenses
                'is_mock': True,
                'created_by': finance_user['id'],
                'created_at': trans_date.isoformat()
            }
            transactions.append(trans)
    
    await db.transactions.insert_many(transactions)  # Changed to 'transactions' collection
    print(f"   ✓ Created {len(transactions)} transactions ({sum(1 for t in transactions if t['transaction_type'] == 'income')} revenue, {sum(1 for t in transactions if t['transaction_type'] == 'expense')} expense)")
    
    return transactions

async def seed_reports(businesses, users, transactions):
    """Create daily reports for Loket and Kasir"""
    print("\n📊 Creating daily reports...")
    
    loket_users = [u for u in users if u['role_id'] == 6]
    kasir_users = [u for u in users if u['role_id'] == 5]
    
    loket_reports = []
    kasir_reports = []
    
    for days_ago in range(60, -1, -1):
        report_date = (datetime.now() - timedelta(days=days_ago)).date()
        
        # Loket Reports (1-2 per day)
        for _ in range(random.randint(1, 2)):
            business = random.choice(businesses)
            loket_user = random.choice(loket_users)
            
            # Get transactions for this day and business (using created_at field)
            day_transactions = [t for t in transactions 
                              if t['business_id'] == business['id'] 
                              and t['created_at'].startswith(str(report_date))]
            
            total_revenue = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'income')
            total_transactions_count = len([t for t in day_transactions if t['transaction_type'] == 'income'])
            
            cash_total = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'income' and t['payment_method'] == 'cash')
            transfer_total = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'income' and t['payment_method'] == 'transfer')
            qris_total = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'income' and t['payment_method'] == 'qris')
            
            report = {
                'id': generate_id(),
                'report_number': generate_code('LRPT'),
                'business_id': business['id'],
                'report_date': report_date.isoformat(),
                'shift': random.choice(['Pagi', 'Siang', 'Malam']),
                'opening_balance': random.randint(500000, 2000000),
                'closing_balance': random.randint(1000000, 5000000),
                'total_transactions': total_transactions_count,
                'total_revenue': total_revenue,
                'cash_total': cash_total,
                'transfer_total': transfer_total,
                'qris_total': qris_total,
                'notes': f'Operasional normal, {total_transactions_count} transaksi hari ini',
                'is_mock': True,
                'submitted_by': loket_user['id'],
                'submitted_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=18)).isoformat(),
                'created_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=18)).isoformat(),
                'updated_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=18)).isoformat()
            }
            loket_reports.append(report)
        
        # Kasir Reports (1-2 per day)
        for _ in range(random.randint(1, 2)):
            business = random.choice(businesses)
            kasir_user = random.choice(kasir_users)
            
            day_transactions = [t for t in transactions 
                              if t['business_id'] == business['id'] 
                              and t['transaction_date'].startswith(str(report_date))]
            
            total_revenue = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'revenue')
            total_expenses = sum(t['amount'] for t in day_transactions if t['transaction_type'] == 'expense')
            
            report = {
                'id': generate_id(),
                'report_number': generate_code('KRPT'),
                'business_id': business['id'],
                'report_date': report_date.isoformat(),
                'shift': random.choice(['Pagi', 'Siang', 'Malam']),
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': total_revenue - total_expenses,
                'cash_in_hand': random.randint(1000000, 5000000),
                'bank_deposits': random.randint(5000000, 20000000),
                'discrepancy': random.randint(-50000, 50000) if random.random() > 0.8 else 0,
                'notes': 'Kas sesuai, tidak ada selisih' if random.random() > 0.2 else 'Selisih kecil sudah diklarifikasi',
                'is_mock': True,
                'submitted_by': kasir_user['id'],
                'submitted_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=19)).isoformat(),
                'created_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=19)).isoformat(),
                'updated_at': (datetime.combine(report_date, datetime.min.time()) + timedelta(hours=19)).isoformat()
            }
            kasir_reports.append(report)
    
    if loket_reports:
        await db.loket_reports.insert_many(loket_reports)
    if kasir_reports:
        await db.kasir_reports.insert_many(kasir_reports)
    
    print(f"   ✓ Created {len(loket_reports)} loket reports and {len(kasir_reports)} kasir reports")

async def seed_loyalty_programs(businesses, users):
    """Create loyalty programs"""
    print("\n🎁 Creating loyalty programs...")
    
    manager_user = next(u for u in users if u['role_id'] == 2)
    
    programs = []
    for prog_data in LOYALTY_PROGRAMS:
        business = random.choice(businesses)
        
        program = {
            'id': generate_id(),
            'program_code': generate_code('LYL'),
            'business_id': business['id'],
            'name': prog_data['name'],
            'description': prog_data['description'],
            'points_per_transaction': prog_data['points_per_transaction'],
            'min_transaction': prog_data['min_transaction'],
            'cashback_percentage': prog_data['cashback_percentage'],
            'benefits': prog_data['benefits'],
            'is_active': True,
            'start_date': (datetime.now() - timedelta(days=180)).date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=180)).date().isoformat(),
            'total_members': random.randint(50, 200),
            'is_mock': True,
            'created_by': manager_user['id'],
            'created_at': random_date(180, 150).isoformat(),
            'updated_at': utc_now().isoformat()
        }
        programs.append(program)
    
    await db.loyalty_programs.insert_many(programs)
    print(f"   ✓ Created {len(programs)} loyalty programs")
    
    return programs

async def seed_csr_programs(businesses, users):
    """Create CSR programs"""
    print("\n❤️ Creating CSR programs...")
    
    manager_user = next(u for u in users if u['role_id'] == 2)
    
    programs = []
    for prog_data in CSR_PROGRAMS:
        business = random.choice(businesses)
        
        current_beneficiaries = random.randint(0, prog_data['target_beneficiaries'])
        spent_budget = random.randint(int(prog_data['budget'] * 0.3), int(prog_data['budget'] * 0.9))
        
        program = {
            'id': generate_id(),
            'program_code': generate_code('CSR'),
            'business_id': business['id'],
            'name': prog_data['name'],
            'description': prog_data['description'],
            'category': prog_data['category'],
            'target_beneficiaries': prog_data['target_beneficiaries'],
            'current_beneficiaries': current_beneficiaries,
            'budget': prog_data['budget'],
            'spent': spent_budget,
            'remaining': prog_data['budget'] - spent_budget,
            'status': 'active' if current_beneficiaries < prog_data['target_beneficiaries'] else 'completed',
            'start_date': (datetime.now() - timedelta(days=120)).date().isoformat(),
            'end_date': (datetime.now() + timedelta(days=120)).date().isoformat(),
            'is_mock': True,
            'created_by': manager_user['id'],
            'created_at': random_date(120, 100).isoformat(),
            'updated_at': utc_now().isoformat()
        }
        programs.append(program)
    
    await db.csr_programs.insert_many(programs)
    print(f"   ✓ Created {len(programs)} CSR programs")
    
    return programs

async def seed_settings(owner_id):
    """Create initial settings"""
    print("\n⚙️ Creating settings...")
    
    settings = [
        {'setting_key': 'company_name', 'setting_value': 'PT. GELIS Indonesia', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'company_address', 'setting_value': 'Jl. Sudirman No. 123, Jakarta Selatan', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'company_phone', 'setting_value': '021-12345678', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'company_email', 'setting_value': 'info@gelis.com', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'company_website', 'setting_value': 'https://gelis.com', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'timezone', 'setting_value': 'Asia/Jakarta', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'language', 'setting_value': 'id', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'currency', 'setting_value': 'IDR', 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
        {'setting_key': 'is_mock_data', 'setting_value': True, 'updated_by': owner_id, 'updated_at': utc_now().isoformat()},
    ]
    
    await db.settings.insert_many(settings)
    print(f"   ✓ Created {len(settings)} settings")

async def log_activity(user_id, action, description):
    """Log activity"""
    await db.activity_logs.insert_one({
        'id': generate_id(),
        'user_id': user_id,
        'action': action,
        'description': description,
        'ip_address': '127.0.0.1',
        'user_agent': 'Seed Script',
        'created_at': utc_now().isoformat()
    })

# ==================== MAIN ====================

async def main():
    """Main seed function"""
    print("\n" + "="*60)
    print("🌱 GELIS COMPLETE MOCK DATA SEEDER")
    print("="*60)
    
    try:
        # Clear all data
        await clear_all_data()
        
        # Seed in order
        await seed_roles()
        users = await seed_users()
        
        owner_id = next(u['id'] for u in users if u['role_id'] == 1)
        
        businesses = await seed_businesses(owner_id)
        orders = await seed_orders(businesses, users)
        transactions = await seed_transactions(businesses, orders, users)
        await seed_reports(businesses, users, transactions)
        await seed_loyalty_programs(businesses, users)
        await seed_csr_programs(businesses, users)
        await seed_settings(owner_id)
        
        # Log seed activity
        await log_activity(owner_id, 'system.seed', 'Complete mock data seeded')
        
        # Print summary
        print("\n" + "="*60)
        print("✅ SEED COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Roles: 7")
        print(f"   • Users: {len(users)} (1 Owner + {len(users)-1} mock)")
        print(f"   • Businesses: {len(businesses)}")
        print(f"   • Orders: {len(orders)}")
        print(f"   • Transactions: {len(transactions)}")
        print(f"   • Loyalty Programs: 3")
        print(f"   • CSR Programs: 3")
        
        print("\n🔑 Login Credentials:")
        print("   Owner:")
        print("   • Username: owner")
        print("   • Password: owner123")
        print("\n   Other users:")
        print("   • manager/manager123, finance/finance123")
        print("   • loket1-3/loket123, kasir1-3/kasir123")
        print("   • teknisi1-4/teknisi123")
        
        print("\n⚠️  MOCK DATA MODE ACTIVE")
        print("   • Semua data adalah simulasi")
        print("   • Owner dapat menghapus semua mock data di Settings")
        print("   • Setelah hapus, aplikasi siap untuk data real")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == '__main__':
    asyncio.run(main())
