#!/usr/bin/env python3
"""
Mock Data Generator untuk GELIS System
Generate realistic demo data untuk testing dan demo
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta, timezone
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

sys.path.append('/app/backend')
from utils.auth import get_password_hash
from utils.helpers import generate_id, generate_code, utc_now

load_dotenv('/app/backend/.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

# Mock data
BUSINESS_CATEGORIES = ['PPOB', 'PLN', 'Travel', 'PDAM', 'Inventory', 'Custom']

CUSTOMERS = [
    {'name': 'Budi Santoso', 'phone': '081234567890', 'email': 'budi@example.com'},
    {'name': 'Siti Aminah', 'phone': '081234567891', 'email': 'siti@example.com'},
    {'name': 'Ahmad Yani', 'phone': '081234567892', 'email': 'ahmad@example.com'},
    {'name': 'Dewi Lestari', 'phone': '081234567893', 'email': 'dewi@example.com'},
    {'name': 'Rudi Hartono', 'phone': '081234567894', 'email': 'rudi@example.com'},
    {'name': 'Linda Wijaya', 'phone': '081234567895', 'email': 'linda@example.com'},
    {'name': 'Joko Widodo', 'phone': '081234567896', 'email': 'joko@example.com'},
    {'name': 'Sri Mulyani', 'phone': '081234567897', 'email': 'sri@example.com'},
    {'name': 'Bambang Susilo', 'phone': '081234567898', 'email': 'bambang@example.com'},
    {'name': 'Rina Setiawan', 'phone': '081234567899', 'email': 'rina@example.com'},
]

SERVICES = {
    'PPOB': ['Listrik PLN', 'PDAM', 'Telkom', 'Pulsa', 'Internet', 'TV Kabel'],
    'PLN': ['Instalasi Baru', 'Pengurusan NIDI', 'Pengurusan SLO', 'Pemeriksaan Jaringan'],
    'Travel': ['Paket Umroh Reguler', 'Paket Umroh VIP', 'Paket Umroh Plus Turki'],
    'PDAM': ['Pencatatan Meter', 'Instalasi Baru', 'Perbaikan Pipa'],
    'Inventory': ['Pengadaan Alat Kantor', 'Pengadaan Komputer', 'Pengadaan Furniture'],
    'Custom': ['Jasa Konsultasi', 'Jasa Maintenance', 'Jasa Lainnya']
}

TRANSACTION_CATEGORIES = {
    'income': ['Penjualan', 'Jasa', 'Komisi', 'Lain-lain'],
    'expense': ['Gaji', 'Operasional', 'Utilities', 'Marketing', 'Transport', 'ATK']
}

async def create_demo_users(db, business_id):
    """Create demo users dengan berbagai role"""
    users_data = [
        {
            'username': 'manager',
            'email': 'manager@gelis.com',
            'password': get_password_hash('manager123'),
            'full_name': 'Manager Operasional',
            'phone': '081234560001',
            'role_id': 2,
            'is_active': True
        },
        {
            'username': 'finance',
            'email': 'finance@gelis.com',
            'password': get_password_hash('finance123'),
            'full_name': 'Staff Finance',
            'phone': '081234560002',
            'role_id': 3,
            'is_active': True
        },
        {
            'username': 'cs1',
            'email': 'cs1@gelis.com',
            'password': get_password_hash('cs123'),
            'full_name': 'Customer Service 1',
            'phone': '081234560003',
            'role_id': 4,
            'is_active': True
        },
        {
            'username': 'kasir',
            'email': 'kasir@gelis.com',
            'password': get_password_hash('kasir123'),
            'full_name': 'Kasir Utama',
            'phone': '081234560004',
            'role_id': 5,
            'is_active': True
        },
        {
            'username': 'loket',
            'email': 'loket@gelis.com',
            'password': get_password_hash('loket123'),
            'full_name': 'Petugas Loket',
            'phone': '081234560005',
            'role_id': 6,
            'is_active': True
        },
        {
            'username': 'teknisi1',
            'email': 'teknisi1@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Teknisi Lapangan 1',
            'phone': '081234560006',
            'role_id': 7,
            'is_active': True
        },
        {
            'username': 'teknisi2',
            'email': 'teknisi2@gelis.com',
            'password': get_password_hash('teknisi123'),
            'full_name': 'Teknisi Lapangan 2',
            'phone': '081234560007',
            'role_id': 7,
            'is_active': True
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user_data['id'] = generate_id()
        user_data['created_at'] = utc_now().isoformat()
        user_data['updated_at'] = utc_now().isoformat()
        user_data['last_login'] = None
        
        await db.users.insert_one(user_data)
        created_users.append(user_data)
        print(f"  ✅ Created user: {user_data['username']}")
    
    return created_users

async def create_businesses(db, owner_id):
    """Create berbagai bisnis"""
    businesses_data = [
        {
            'name': 'Loket PPOB Pusat',
            'category': 'PPOB',
            'description': 'Layanan pembayaran PPOB (listrik, air, pulsa, dll)',
            'address': 'Jl. Sudirman No. 123, Jakarta',
            'phone': '0211234567',
            'email': 'ppob@gelis.com',
            'settings': {'commission_rate': 0.05}
        },
        {
            'name': 'Instalasi PLN Mandiri',
            'category': 'PLN',
            'description': 'Jasa instalasi listrik PLN, NIDI, dan SLO',
            'address': 'Jl. Gatot Subroto No. 456, Jakarta',
            'phone': '0211234568',
            'email': 'pln@gelis.com',
            'settings': {'technician_fee': 500000}
        },
        {
            'name': 'Travel Umroh Berkah',
            'category': 'Travel',
            'description': 'Penyelenggara perjalanan umroh terpercaya',
            'address': 'Jl. HR Rasuna Said No. 789, Jakarta',
            'phone': '0211234569',
            'email': 'umroh@gelis.com',
            'settings': {'agent_commission': 0.1}
        },
        {
            'name': 'Layanan PDAM',
            'category': 'PDAM',
            'description': 'Pencatatan meter dan instalasi PDAM',
            'address': 'Jl. Thamrin No. 321, Jakarta',
            'phone': '0211234570',
            'email': 'pdam@gelis.com',
            'settings': {'service_fee': 50000}
        },
        {
            'name': 'Toko Serbaguna',
            'category': 'Inventory',
            'description': 'Pengadaan barang dan alat kantor',
            'address': 'Jl. Asia Afrika No. 654, Jakarta',
            'phone': '0211234571',
            'email': 'toko@gelis.com',
            'settings': {'markup_percentage': 0.15}
        }
    ]
    
    created_businesses = []
    for biz_data in businesses_data:
        biz_data['id'] = generate_id()
        biz_data['is_active'] = True
        biz_data['created_by'] = owner_id
        biz_data['created_at'] = utc_now().isoformat()
        biz_data['updated_at'] = utc_now().isoformat()
        
        await db.businesses.insert_one(biz_data)
        created_businesses.append(biz_data)
        print(f"  ✅ Created business: {biz_data['name']}")
    
    return created_businesses

async def create_orders(db, businesses, users, customers):
    """Create sample orders untuk berbagai bisnis"""
    orders = []
    statuses = ['pending', 'processing', 'completed', 'completed', 'completed']  # Bias ke completed
    payment_statuses = ['paid', 'paid', 'paid', 'partial', 'unpaid']
    
    # Generate orders untuk 3 bulan terakhir
    for i in range(50):
        business = random.choice(businesses)
        customer = random.choice(customers)
        creator = random.choice([u for u in users if u['role_id'] in [1, 2, 4, 5, 6]])
        
        service = random.choice(SERVICES[business['category']])
        status = random.choice(statuses)
        payment_status = random.choice(payment_statuses)
        
        # Generate amount based on service type
        if business['category'] == 'Travel':
            total_amount = random.randint(20000000, 35000000)
        elif business['category'] == 'PLN':
            total_amount = random.randint(5000000, 15000000)
        else:
            total_amount = random.randint(50000, 2000000)
        
        paid_amount = total_amount if payment_status == 'paid' else (
            total_amount * 0.5 if payment_status == 'partial' else 0
        )
        
        # Random date dalam 3 bulan terakhir
        days_ago = random.randint(0, 90)
        created_at = utc_now() - timedelta(days=days_ago)
        
        order_data = {
            'id': generate_id(),
            'order_number': generate_code('ORD', 12),
            'business_id': business['id'],
            'customer_name': customer['name'],
            'customer_phone': customer['phone'],
            'customer_email': customer['email'],
            'service_type': service,
            'order_details': {
                'notes': f'Pesanan {service}',
                'quantity': 1
            },
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'status': status,
            'payment_status': payment_status,
            'payment_method': random.choice(['Cash', 'Transfer', 'QRIS', 'Debit Card']),
            'assigned_to': random.choice([u['id'] for u in users if u['role_id'] == 7]) if status != 'pending' else None,
            'completion_date': (created_at + timedelta(days=random.randint(1, 7))).isoformat() if status == 'completed' else None,
            'notes': None,
            'created_by': creator['id'],
            'created_at': created_at.isoformat(),
            'updated_at': created_at.isoformat()
        }
        
        await db.orders.insert_one(order_data)
        orders.append(order_data)
    
    print(f"  ✅ Created {len(orders)} orders")
    return orders

async def create_transactions(db, businesses, users, orders):
    """Create transactions berdasarkan orders dan expense"""
    transactions = []
    
    # Create income transactions dari orders yang paid
    for order in orders:
        if order['payment_status'] in ['paid', 'partial']:
            txn_data = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'order_id': order['id'],
                'business_id': order['business_id'],
                'transaction_type': 'income',
                'category': 'Penjualan',
                'description': f"Pembayaran {order['service_type']} - {order['customer_name']}",
                'amount': order['paid_amount'],
                'payment_method': order['payment_method'],
                'reference_number': f"REF-{random.randint(100000, 999999)}",
                'created_by': order['created_by'],
                'created_at': order['created_at']
            }
            
            await db.transactions.insert_one(txn_data)
            transactions.append(txn_data)
    
    # Create expense transactions
    expense_count = 30
    for i in range(expense_count):
        business = random.choice(businesses)
        user = random.choice([u for u in users if u['role_id'] in [1, 2, 3]])
        
        category = random.choice(TRANSACTION_CATEGORIES['expense'])
        
        # Amount based on category
        if category == 'Gaji':
            amount = random.randint(3000000, 8000000)
        elif category == 'Operasional':
            amount = random.randint(500000, 3000000)
        else:
            amount = random.randint(100000, 1000000)
        
        days_ago = random.randint(0, 90)
        created_at = utc_now() - timedelta(days=days_ago)
        
        txn_data = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'order_id': None,
            'business_id': business['id'],
            'transaction_type': 'expense',
            'category': category,
            'description': f"{category} - {created_at.strftime('%B %Y')}",
            'amount': amount,
            'payment_method': random.choice(['Transfer', 'Cash', 'Debit Card']),
            'reference_number': f"EXP-{random.randint(100000, 999999)}",
            'created_by': user['id'],
            'created_at': created_at.isoformat()
        }
        
        await db.transactions.insert_one(txn_data)
        transactions.append(txn_data)
    
    print(f"  ✅ Created {len(transactions)} transactions")
    return transactions

async def create_customers(db):
    """Create customer records"""
    customers = []
    
    for i, cust in enumerate(CUSTOMERS):
        customer_data = {
            'id': generate_id(),
            'name': cust['name'],
            'email': cust['email'],
            'phone': cust['phone'],
            'address': f"Jl. Customer No. {i+1}, Jakarta",
            'loyalty_points': random.randint(0, 1000),
            'loyalty_tier': random.choice(['Bronze', 'Silver', 'Gold']),
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat()
        }
        
        await db.customers.insert_one(customer_data)
        customers.append(customer_data)
    
    print(f"  ✅ Created {len(customers)} customers")
    return customers

async def create_notifications(db, users):
    """Create sample notifications"""
    notifications = []
    notif_types = ['info', 'success', 'warning']
    
    for i in range(20):
        user = random.choice(users)
        days_ago = random.randint(0, 30)
        created_at = utc_now() - timedelta(days=days_ago)
        
        notif_data = {
            'id': generate_id(),
            'user_id': user['id'],
            'title': random.choice([
                'Pesanan Baru',
                'Pembayaran Diterima',
                'Tugas Ditugaskan',
                'Laporan Siap',
                'Update Sistem'
            ]),
            'message': f"Sample notification message {i+1}",
            'type': random.choice(notif_types),
            'is_read': random.choice([True, False, False]),  # Bias ke unread
            'related_id': None,
            'related_type': None,
            'action_url': None,
            'created_at': created_at.isoformat()
        }
        
        await db.notifications.insert_one(notif_data)
        notifications.append(notif_data)
    
    print(f"  ✅ Created {len(notifications)} notifications")
    return notifications

async def main():
    print("🚀 Starting Mock Data Generation for GELIS System\\n")
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get owner user
    owner = await db.users.find_one({'role_id': 1}, {'_id': 0})
    if not owner:
        print("❌ Owner user not found. Please run init-data first.")
        return
    
    print(f"📊 Using owner: {owner['username']}\\n")
    
    # Step 1: Create demo users
    print("1️⃣ Creating demo users...")
    users = await create_demo_users(db, None)
    all_users = [owner] + users
    
    # Step 2: Create businesses
    print("\\n2️⃣ Creating businesses...")
    businesses = await create_businesses(db, owner['id'])
    
    # Step 3: Create customers
    print("\\n3️⃣ Creating customers...")
    customers = await create_customers(db)
    
    # Step 4: Create orders
    print("\\n4️⃣ Creating orders...")
    orders = await create_orders(db, businesses, all_users, customers)
    
    # Step 5: Create transactions
    print("\\n5️⃣ Creating transactions...")
    transactions = await create_transactions(db, businesses, all_users, orders)
    
    # Step 6: Create notifications
    print("\\n6️⃣ Creating notifications...")
    notifications = await create_notifications(db, all_users)
    
    client.close()
    
    print("\\n" + "="*60)
    print("✅ Mock Data Generation Complete!")
    print("="*60)
    print(f"\\n📈 Summary:")
    print(f"  • Users: {len(all_users)}")
    print(f"  • Businesses: {len(businesses)}")
    print(f"  • Customers: {len(customers)}")
    print(f"  • Orders: {len(orders)}")
    print(f"  • Transactions: {len(transactions)}")
    print(f"  • Notifications: {len(notifications)}")
    print(f"\\n🔐 Demo User Credentials:")
    print(f"  • owner / owner123 (Full access)")
    print(f"  • manager / manager123 (Manager)")
    print(f"  • finance / finance123 (Finance)")
    print(f"  • cs1 / cs123 (Customer Service)")
    print(f"  • kasir / kasir123 (Kasir)")
    print(f"  • loket / loket123 (Loket)")
    print(f"  • teknisi1 / teknisi123 (Teknisi)")
    print(f"\\n🎉 System is ready for demo!")

if __name__ == '__main__':
    asyncio.run(main())
