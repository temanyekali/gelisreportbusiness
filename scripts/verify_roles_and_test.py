"""
Script untuk verifikasi role dan permission matrix
Run: python3 /app/scripts/verify_roles_and_test.py
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Role Matrix (sesuai sistem)
ROLE_MATRIX = {
    1: 'Owner',
    2: 'Manager',
    3: 'Finance',
    4: 'Marketing',
    5: 'Kasir',
    6: 'Loket',
    7: 'Teknisi'
}

# Permission Matrix (dari Layout.js)
PERMISSION_MATRIX = {
    'Dashboard': [1, 2, 3, 4, 5, 6, 7],  # Semua role
    'Bisnis': [1, 2],
    'Pesanan': [1, 2, 5, 6],
    'Pekerjaan Teknisi': [1, 2, 5, 7],
    'Akunting': [1, 2, 3],
    'Pengguna': [1, 2],
    'Laporan Harian': [1, 2, 3, 5, 6],
    'Ringkasan Eksekutif': [1, 2, 3],
    'Program Loyalitas': [1, 2],
    'Program CSR': [1, 2],
    'Log Aktivitas': [1, 2],
    'Pengaturan': [1]
}

async def verify_users_exist():
    """Verify users dengan berbagai role exist"""
    print("\n" + "="*70)
    print("👥 VERIFYING USERS")
    print("="*70)
    
    users = await db.users.find({}, {'_id': 0, 'username': 1, 'role_id': 1, 'name': 1}).to_list(100)
    
    # Group by role
    users_by_role = {}
    for user in users:
        role_id = user.get('role_id')
        if role_id not in users_by_role:
            users_by_role[role_id] = []
        users_by_role[role_id].append(user)
    
    print(f"\n📊 Total Users: {len(users)}")
    print("\nUsers by Role:")
    
    for role_id in sorted(ROLE_MATRIX.keys()):
        role_name = ROLE_MATRIX[role_id]
        role_users = users_by_role.get(role_id, [])
        
        print(f"\n  {role_id}. {role_name}: {len(role_users)} users")
        for user in role_users:
            print(f"     - {user.get('username')} ({user.get('name', 'N/A')})")
    
    return users_by_role

async def show_permission_matrix():
    """Display permission matrix"""
    print("\n" + "="*70)
    print("🔐 PERMISSION MATRIX")
    print("="*70)
    
    print("\n{:<25} {:<50}".format("Menu", "Allowed Roles"))
    print("-" * 75)
    
    for menu, roles in PERMISSION_MATRIX.items():
        role_names = [ROLE_MATRIX[r] for r in roles if r in ROLE_MATRIX]
        print("{:<25} {}".format(menu, ", ".join(role_names)))

async def test_teknisi_access():
    """Test teknisi access (hanya Pekerjaan Teknisi)"""
    print("\n" + "="*70)
    print("🧪 TEST: TEKNISI ACCESS (Role ID: 7)")
    print("="*70)
    
    teknisi_role_id = 7
    
    print(f"\nTeknisi ({ROLE_MATRIX[teknisi_role_id]}) DAPAT akses:")
    for menu, roles in PERMISSION_MATRIX.items():
        if teknisi_role_id in roles:
            print(f"  ✅ {menu}")
    
    print(f"\nTeknisi TIDAK DAPAT akses:")
    for menu, roles in PERMISSION_MATRIX.items():
        if teknisi_role_id not in roles:
            print(f"  ❌ {menu}")

async def check_activity_logs():
    """Check if activity logging is working"""
    print("\n" + "="*70)
    print("📝 CHECKING ACTIVITY LOGS")
    print("="*70)
    
    # Get recent activity logs
    logs = await db.activity_logs.find({}, {'_id': 0}).sort('timestamp', -1).limit(10).to_list(10)
    
    print(f"\n📊 Total Activity Logs: {await db.activity_logs.count_documents({})}")
    print(f"\nRecent 10 Activities:")
    
    if logs:
        for idx, log in enumerate(logs, 1):
            timestamp = log.get('timestamp', 'N/A')
            if isinstance(timestamp, str):
                timestamp = timestamp[:19]  # YYYY-MM-DD HH:MM:SS
            
            print(f"\n  {idx}. [{timestamp}]")
            print(f"     User: {log.get('user_id', 'N/A')}")
            print(f"     Action: {log.get('action_type', 'N/A')}")
            print(f"     Description: {log.get('description', 'N/A')[:60]}")
    else:
        print("\n  ⚠️ No activity logs found!")
        print("  Activity logging may not be working properly.")

async def generate_test_users():
    """Ensure test users exist for each role"""
    print("\n" + "="*70)
    print("🔧 ENSURING TEST USERS EXIST")
    print("="*70)
    
    # Import di awal function
    import sys
    import uuid
    sys.path.insert(0, '/app/backend')
    from utils.auth import get_password_hash
    
    test_users = [
        {'username': 'owner', 'password': 'owner123', 'name': 'Owner User', 'role_id': 1, 'email': 'owner@gelis.com'},
        {'username': 'manager', 'password': 'manager123', 'name': 'Manager User', 'role_id': 2, 'email': 'manager@gelis.com'},
        {'username': 'finance', 'password': 'finance123', 'name': 'Finance User', 'role_id': 3, 'email': 'finance@gelis.com'},
        {'username': 'kasir1', 'password': 'kasir123', 'name': 'Kasir User', 'role_id': 5, 'email': 'kasir1@gelis.com'},
        {'username': 'loket1', 'password': 'loket123', 'name': 'Loket User', 'role_id': 6, 'email': 'loket1@gelis.com'},
        {'username': 'indra', 'password': 'teknisi123', 'name': 'Indra (Teknisi)', 'role_id': 7, 'email': 'indra@gelis.com'},
    ]
    
    for test_user in test_users:
        existing = await db.users.find_one({'username': test_user['username']}, {'_id': 0})
        
        if not existing:
            user_data = {
                'id': str(uuid.uuid4()),
                'username': test_user['username'],
                'name': test_user['name'],
                'email': test_user['email'],
                'password': get_password_hash(test_user['password']),
                'role_id': test_user['role_id'],
                'is_active': True,
                'created_at': '2025-12-14T10:00:00'
            }
            await db.users.insert_one(user_data)
            print(f"  ✅ Created: {test_user['username']} ({ROLE_MATRIX[test_user['role_id']]})")
        else:
            print(f"  ✓ Exists: {test_user['username']} ({ROLE_MATRIX[test_user['role_id']]})")

async def main():
    print("="*70)
    print("🔐 ROLE & PERMISSION VERIFICATION TOOL")
    print("="*70)
    
    # Ensure test users exist
    await generate_test_users()
    
    # Verify users
    users_by_role = await verify_users_exist()
    
    # Show permission matrix
    await show_permission_matrix()
    
    # Test specific role (Teknisi)
    await test_teknisi_access()
    
    # Check activity logs
    await check_activity_logs()
    
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETED")
    print("="*70)
    
    print("\n💡 TESTING INSTRUCTIONS:")
    print("   1. Login sebagai 'indra' dengan password 'teknisi123'")
    print("   2. Verifikasi hanya menu 'Dashboard' dan 'Pekerjaan Teknisi' yang muncul")
    print("   3. Coba akses URL lain (misal: /users) → harus redirect/403")
    print("   4. Check Log Aktivitas untuk melihat semua activity recorded")
    
    print("\n📝 TEST CREDENTIALS:")
    print("   Owner:    owner / owner123")
    print("   Manager:  manager / manager123")
    print("   Finance:  finance / finance123")
    print("   Kasir:    kasir1 / kasir123")
    print("   Loket:    loket1 / loket123")
    print("   Teknisi:  indra / teknisi123")
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
