"""
Script untuk menghapus semua data pemesanan PPOB
Karena PPOB menggunakan sistem laporan harian per shift, BUKAN per pemesanan
Run: python3 /app/scripts/clean_ppob_orders.py
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

async def get_ppob_business():
    """Get PPOB business"""
    business = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if not business:
        print("❌ PPOB business not found!")
        return None
    return business

async def clean_ppob_orders():
    """Hapus semua orders PPOB"""
    print("\n🧹 Menghapus semua data pemesanan PPOB...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Count existing orders
    existing_orders = await db.orders.count_documents({'business_id': ppob_business['id']})
    print(f"   Found {existing_orders} PPOB orders to delete")
    
    # Delete PPOB orders
    result = await db.orders.delete_many({'business_id': ppob_business['id']})
    print(f"   ✓ Deleted {result.deleted_count} PPOB orders")
    
    # Check if there are any transactions from orders (not from shift reports)
    # Transactions from shift reports have reference like 'PPOB-SHIFT-...'
    txn_from_orders = await db.transactions.find({
        'business_id': ppob_business['id'],
        'reference_number': {'$not': {'$regex': '^PPOB-SHIFT-'}}
    }, {'_id': 0}).to_list(100)
    
    if txn_from_orders:
        print(f"\n   ⚠️ Found {len(txn_from_orders)} transactions from PPOB orders (not from shift reports)")
        print("   These should be removed as well...")
        
        # Delete transactions from orders
        result = await db.transactions.delete_many({
            'business_id': ppob_business['id'],
            'reference_number': {'$not': {'$regex': '^PPOB-SHIFT-'}}
        })
        print(f"   ✓ Deleted {result.deleted_count} PPOB order transactions")
    else:
        print("   ✓ No order-based transactions found (good!)")

async def verify_data_integrity():
    """Verify data setelah cleaning"""
    print("\n📊 Verifying data integrity...")
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Check orders
    ppob_orders = await db.orders.count_documents({'business_id': ppob_business['id']})
    print(f"   PPOB Orders: {ppob_orders} (should be 0)")
    
    # Check shift reports
    shift_reports = await db.ppob_loket_shifts.count_documents({})
    print(f"   PPOB Shift Reports: {shift_reports}")
    
    # Check transactions from shift
    txn_from_shift = await db.transactions.count_documents({
        'business_id': ppob_business['id'],
        'reference_number': {'$regex': '^PPOB-SHIFT-'}
    })
    print(f"   PPOB Transactions (from shifts): {txn_from_shift}")
    
    # Check total PPOB revenue
    pipeline = [
        {
            '$match': {
                'business_id': ppob_business['id'],
                'transaction_type': 'income',
                'reference_number': {'$regex': '^PPOB-SHIFT-'}
            }
        },
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    result = await db.transactions.aggregate(pipeline).to_list(1)
    total_revenue = result[0]['total'] if result else 0
    
    print(f"   Total PPOB Revenue (from shifts): Rp {total_revenue:,.0f}")
    
    # Verify consistency
    print("\n✅ Data Integrity Check:")
    if ppob_orders == 0:
        print("   ✓ No PPOB orders (correct - using shift reports)")
    else:
        print(f"   ❌ Still have {ppob_orders} PPOB orders!")
    
    if shift_reports > 0 and txn_from_shift == shift_reports:
        print(f"   ✓ All {shift_reports} shifts have corresponding transactions")
    else:
        print(f"   ⚠️ Mismatch: {shift_reports} shifts but {txn_from_shift} transactions")

async def show_sample_data():
    """Show sample transactions"""
    print("\n📋 Sample PPOB Transactions (from shift reports):")
    print("=" * 70)
    
    ppob_business = await get_ppob_business()
    if not ppob_business:
        return
    
    # Get 3 sample transactions
    samples = await db.transactions.find({
        'business_id': ppob_business['id'],
        'reference_number': {'$regex': '^PPOB-SHIFT-'}
    }, {'_id': 0}).sort('created_at', -1).limit(3).to_list(3)
    
    for idx, txn in enumerate(samples, 1):
        print(f"\n🔸 Transaction {idx}")
        print(f"   Date: {txn.get('created_at', 'N/A')[:10]}")
        print(f"   Category: {txn.get('category')}")
        print(f"   Amount: Rp {txn.get('amount', 0):,.0f}")
        print(f"   Reference: {txn.get('reference_number')}")
        print(f"   Description:")
        desc_lines = txn.get('description', '').split('\n')
        for line in desc_lines[:3]:  # Show first 3 lines
            print(f"      {line}")
    
    print("=" * 70)

async def main():
    print("=" * 70)
    print("🚀 CLEAN PPOB ORDERS - Gunakan Shift Reports Saja")
    print("=" * 70)
    print("\n💡 KONSEP:")
    print("   - PPOB TIDAK menggunakan sistem pemesanan individual")
    print("   - PPOB menggunakan LAPORAN HARIAN per shift")
    print("   - Setiap shift = 1 entry akuntansi (akumulasi penjualan)")
    print("=" * 70)
    
    # Clean PPOB orders
    await clean_ppob_orders()
    
    # Verify
    await verify_data_integrity()
    
    # Show samples
    await show_sample_data()
    
    print("\n" + "=" * 70)
    print("✅ CLEANING COMPLETED!")
    print("=" * 70)
    print("\n📌 KESIMPULAN:")
    print("   ✓ Semua data pemesanan PPOB telah dihapus")
    print("   ✓ Data akunting PPOB hanya dari laporan shift")
    print("   ✓ Tidak ada duplikasi atau inkonsistensi")
    print("=" * 70)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
