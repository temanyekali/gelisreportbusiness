"""
Script untuk verifikasi konsistensi data antara:
- Orders (Pemesanan)
- Laporan Harian (Loket & Kasir)
- Akunting (Transactions)

Run: python3 /app/scripts/verify_data_consistency.py
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def verify_ppob_consistency():
    """Verify PPOB: Shift reports ↔ Accounting transactions"""
    print("\n" + "="*70)
    print("🔍 VERIFYING PPOB DATA CONSISTENCY")
    print("="*70)
    
    # Get PPOB business
    ppob = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if not ppob:
        print("❌ PPOB business not found!")
        return
    
    # 1. Check shift reports
    shift_reports = await db.ppob_loket_shifts.find({}, {'_id': 0}).to_list(1000)
    print(f"\n📊 PPOB Shift Reports: {len(shift_reports)}")
    
    # 2. Check transactions from shifts
    txn_from_shifts = await db.transactions.find({
        'business_id': ppob['id'],
        'reference_number': {'$regex': '^PPOB-SHIFT-'}
    }, {'_id': 0}).to_list(1000)
    print(f"💰 Transactions from Shifts: {len(txn_from_shifts)}")
    
    # 3. Check consistency
    if len(shift_reports) == len(txn_from_shifts):
        print("✅ CONSISTENCY: Each shift report has corresponding transaction")
    else:
        print(f"❌ INCONSISTENCY: {len(shift_reports)} shifts but {len(txn_from_shifts)} transactions!")
        print("   Some shifts may not have accounting entries")
    
    # 4. Verify amounts
    total_shift_penjualan = sum(r.get('total_penjualan', 0) for r in shift_reports)
    total_txn_amount = sum(t.get('amount', 0) for t in txn_from_shifts)
    
    print(f"\n💵 Total from Shifts: Rp {total_shift_penjualan:,.0f}")
    print(f"💵 Total from Transactions: Rp {total_txn_amount:,.0f}")
    
    if abs(total_shift_penjualan - total_txn_amount) < 1:
        print("✅ AMOUNTS MATCH: Shift penjualan = Transaction amounts")
    else:
        diff = total_shift_penjualan - total_txn_amount
        print(f"❌ AMOUNT MISMATCH: Difference of Rp {diff:,.0f}")
    
    # 5. Check for PPOB orders (should be ZERO)
    ppob_orders = await db.orders.count_documents({'business_id': ppob['id']})
    print(f"\n📦 PPOB Orders: {ppob_orders}")
    if ppob_orders == 0:
        print("✅ CORRECT: No PPOB orders (using shift reports)")
    else:
        print(f"❌ ERROR: Found {ppob_orders} PPOB orders! These should not exist!")
    
    return {
        'shifts': len(shift_reports),
        'transactions': len(txn_from_shifts),
        'shift_total': total_shift_penjualan,
        'txn_total': total_txn_amount,
        'orders': ppob_orders
    }

async def verify_other_business_consistency():
    """Verify Other Businesses: Orders ↔ Accounting transactions"""
    print("\n" + "="*70)
    print("🔍 VERIFYING OTHER BUSINESSES DATA CONSISTENCY")
    print("="*70)
    
    # Get non-PPOB businesses
    businesses = await db.businesses.find({'category': {'$ne': 'PPOB'}}, {'_id': 0}).to_list(100)
    print(f"\n📊 Non-PPOB Businesses: {len(businesses)}")
    
    results = {}
    
    for biz in businesses:
        # Count orders
        orders = await db.orders.count_documents({'business_id': biz['id']})
        
        # Count transactions (non-shift)
        transactions = await db.transactions.count_documents({
            'business_id': biz['id']
        })
        
        # Get totals
        order_total = await db.orders.aggregate([
            {'$match': {'business_id': biz['id'], 'payment_status': 'paid'}},
            {'$group': {'_id': None, 'total': {'$sum': '$paid_amount'}}}
        ]).to_list(1)
        order_total_amount = order_total[0]['total'] if order_total else 0
        
        txn_income = await db.transactions.aggregate([
            {'$match': {'business_id': biz['id'], 'transaction_type': 'income'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]).to_list(1)
        txn_income_amount = txn_income[0]['total'] if txn_income else 0
        
        results[biz['name']] = {
            'orders': orders,
            'transactions': transactions,
            'order_total': order_total_amount,
            'txn_income': txn_income_amount
        }
        
        print(f"\n📌 {biz['name']}:")
        print(f"   Orders: {orders}")
        print(f"   Transactions: {transactions}")
        print(f"   Order Total (paid): Rp {order_total_amount:,.0f}")
        print(f"   Transaction Income: Rp {txn_income_amount:,.0f}")
        
        # Note: Orders and transactions may not match 1:1 because:
        # - Transactions can include expenses
        # - Not all orders may have accounting entries yet
    
    return results

async def verify_date_ranges():
    """Verify date ranges across all data"""
    print("\n" + "="*70)
    print("🔍 VERIFYING DATE RANGES")
    print("="*70)
    
    # PPOB Shifts date range
    shifts = await db.ppob_loket_shifts.find({}, {'_id': 0, 'tanggal': 1}).sort('tanggal', 1).to_list(1000)
    if shifts:
        print(f"\n📅 PPOB Shift Reports:")
        print(f"   First: {shifts[0]['tanggal']}")
        print(f"   Last: {shifts[-1]['tanggal']}")
        print(f"   Total: {len(shifts)} reports")
    
    # Transactions date range
    txns = await db.transactions.find({}, {'_id': 0, 'created_at': 1}).sort('created_at', 1).to_list(1000)
    if txns:
        first_date = txns[0]['created_at'][:10] if isinstance(txns[0]['created_at'], str) else str(txns[0]['created_at'])[:10]
        last_date = txns[-1]['created_at'][:10] if isinstance(txns[-1]['created_at'], str) else str(txns[-1]['created_at'])[:10]
        print(f"\n💰 Transactions:")
        print(f"   First: {first_date}")
        print(f"   Last: {last_date}")
        print(f"   Total: {len(txns)} transactions")
    
    # Orders date range
    orders = await db.orders.find({}, {'_id': 0, 'created_at': 1}).sort('created_at', 1).to_list(1000)
    if orders:
        first_date = orders[0]['created_at'][:10] if isinstance(orders[0]['created_at'], str) else str(orders[0]['created_at'])[:10]
        last_date = orders[-1]['created_at'][:10] if isinstance(orders[-1]['created_at'], str) else str(orders[-1]['created_at'])[:10]
        print(f"\n📦 Orders:")
        print(f"   First: {first_date}")
        print(f"   Last: {last_date}")
        print(f"   Total: {len(orders)} orders")

async def generate_summary_report():
    """Generate summary report"""
    print("\n" + "="*70)
    print("📊 SUMMARY REPORT")
    print("="*70)
    
    # Total counts
    total_shifts = await db.ppob_loket_shifts.count_documents({})
    total_orders = await db.orders.count_documents({})
    total_transactions = await db.transactions.count_documents({})
    
    # Financial totals
    total_income_pipeline = [
        {'$match': {'transaction_type': 'income'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    income_result = await db.transactions.aggregate(total_income_pipeline).to_list(1)
    total_income = income_result[0]['total'] if income_result else 0
    
    total_expense_pipeline = [
        {'$match': {'transaction_type': 'expense'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    expense_result = await db.transactions.aggregate(total_expense_pipeline).to_list(1)
    total_expense = expense_result[0]['total'] if expense_result else 0
    
    print(f"\n📊 DATA COUNTS:")
    print(f"   PPOB Shift Reports: {total_shifts}")
    print(f"   Orders (Non-PPOB): {total_orders}")
    print(f"   Total Transactions: {total_transactions}")
    
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   Total Income: Rp {total_income:,.0f}")
    print(f"   Total Expense: Rp {total_expense:,.0f}")
    print(f"   Net Balance: Rp {(total_income - total_expense):,.0f}")
    
    # Health check
    print(f"\n✅ DATA HEALTH CHECK:")
    ppob = await db.businesses.find_one({'category': 'PPOB'}, {'_id': 0})
    if ppob:
        ppob_orders = await db.orders.count_documents({'business_id': ppob['id']})
        ppob_txns = await db.transactions.count_documents({
            'business_id': ppob['id'],
            'reference_number': {'$regex': '^PPOB-SHIFT-'}
        })
        
        print(f"   PPOB Orders: {ppob_orders} (should be 0) {'✅' if ppob_orders == 0 else '❌'}")
        print(f"   PPOB Shift→Txn ratio: {total_shifts}:{ppob_txns} {'✅' if total_shifts == ppob_txns else '❌'}")

async def main():
    print("="*70)
    print("🚀 DATA CONSISTENCY VERIFICATION TOOL")
    print("="*70)
    print("\nThis tool verifies data consistency across:")
    print("  1. Orders (Pemesanan)")
    print("  2. Laporan Harian (Loket & Kasir)")
    print("  3. Akunting (Transactions)")
    
    # Run verifications
    ppob_results = await verify_ppob_consistency()
    other_results = await verify_other_business_consistency()
    await verify_date_ranges()
    await generate_summary_report()
    
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETED!")
    print("="*70)
    
    client.close()

if __name__ == '__main__':
    asyncio.run(main())
