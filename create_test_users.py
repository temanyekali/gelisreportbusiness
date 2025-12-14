#!/usr/bin/env python3
"""
Create test users for GELIS testing
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from utils.helpers import generate_id, utc_now
from utils.auth import get_password_hash
import os

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'gelis_db')]

async def create_test_users():
    """Create test users for different roles"""
    print("👥 Creating test users...")
    
    # Delete existing users except owner
    await db.users.delete_many({'username': {'$ne': 'owner'}})
    
    users = [
        {
            'id': generate_id(),
            'username': 'manager',
            'email': 'manager@gelis.com',
            'password': get_password_hash('manager123'),
            'full_name': 'Manager GELIS',
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
            'full_name': 'Finance GELIS',
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
            'full_name': 'Kasir 1 GELIS',
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
            'full_name': 'Loket 1 GELIS',
            'phone': '081234567894',
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
            'full_name': 'Teknisi 1 GELIS',
            'phone': '081234567895',
            'role_id': 7,
            'is_active': True,
            'created_at': utc_now().isoformat(),
            'updated_at': utc_now().isoformat(),
            'last_login': None
        }
    ]
    
    await db.users.insert_many(users)
    print(f"   ✅ Created {len(users)} test users")
    
    # Verify users
    total_users = await db.users.count_documents({})
    print(f"   📊 Total users in database: {total_users}")

if __name__ == "__main__":
    asyncio.run(create_test_users())