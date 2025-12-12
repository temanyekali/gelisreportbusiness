"""
Data Synchronization Utilities
Auto-sync between Orders, Transactions, and Reports
"""
from datetime import datetime, date
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from utils.helpers import generate_id, generate_code, utc_now


async def auto_create_transaction_from_order(
    db: AsyncIOMotorDatabase,
    order: dict,
    user_id: str
) -> Optional[dict]:
    """
    Automatically create accounting transaction when order is completed
    """
    if order.get('status') != 'completed':
        return None
    
    # Check if transaction already exists
    existing = await db.accounting.find_one({
        'related_order_id': order['id']
    })
    
    if existing:
        return existing
    
    # Get business info
    business = await db.businesses.find_one({'id': order['business_id']})
    
    # Create revenue transaction
    transaction = {
        'id': generate_id(),
        'transaction_number': generate_code('TRX'),
        'business_id': order['business_id'],
        'transaction_type': 'revenue',
        'category': business.get('category', 'General') if business else 'General',
        'amount': order.get('paid_amount', order.get('total_amount', 0)),
        'description': f"Revenue dari {order.get('service_type', 'Order')} - Order #{order.get('order_number')}",
        'transaction_date': order.get('updated_at', utc_now().isoformat()),
        'payment_method': order.get('payment_method', 'Cash'),
        'bank_name': order.get('bank_name'),
        'reference_number': order.get('order_number'),
        'related_order_id': order['id'],
        'is_mock': order.get('is_mock', False),
        'auto_generated': True,  # Flag untuk indicate auto-generated
        'created_by': user_id,
        'created_at': utc_now().isoformat(),
        'updated_at': utc_now().isoformat()
    }
    
    # Insert transaction
    await db.accounting.insert_one(transaction)
    
    # Update daily report totals
    await update_daily_report_totals(db, transaction)
    
    return transaction


async def update_daily_report_totals(
    db: AsyncIOMotorDatabase,
    transaction: dict
):
    """
    Update daily report totals when transaction is added
    """
    # Get transaction date (date only, not datetime)
    trans_date = transaction['transaction_date'][:10]  # YYYY-MM-DD
    business_id = transaction['business_id']
    
    # Calculate totals for the day
    pipeline = [
        {
            '$match': {
                'business_id': business_id,
                'transaction_date': {'$regex': f'^{trans_date}'}
            }
        },
        {
            '$group': {
                '_id': '$transaction_type',
                'total': {'$sum': '$amount'}
            }
        }
    ]
    
    totals = {}
    async for result in db.accounting.aggregate(pipeline):
        totals[result['_id']] = result['total']
    
    total_revenue = totals.get('revenue', 0)
    total_expenses = totals.get('expense', 0)
    
    # Update or create loket report
    await db.loket_reports.update_one(
        {
            'business_id': business_id,
            'report_date': trans_date
        },
        {
            '$set': {
                'total_revenue': total_revenue,
                'total_transactions': await db.accounting.count_documents({
                    'business_id': business_id,
                    'transaction_type': 'revenue',
                    'transaction_date': {'$regex': f'^{trans_date}'}
                }),
                'updated_at': utc_now().isoformat()
            }
        },
        upsert=False
    )
    
    # Update kasir report
    await db.kasir_reports.update_one(
        {
            'business_id': business_id,
            'report_date': trans_date
        },
        {
            '$set': {
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': total_revenue - total_expenses,
                'updated_at': utc_now().isoformat()
            }
        },
        upsert=False
    )


async def sync_order_to_accounting(
    db: AsyncIOMotorDatabase,
    order_id: str,
    user_id: str
) -> dict:
    """
    Sync specific order to accounting (manual trigger)
    """
    order = await db.orders.find_one({'id': order_id})
    if not order:
        return {'error': 'Order not found'}
    
    transaction = await auto_create_transaction_from_order(db, order, user_id)
    
    return {
        'success': True,
        'order_id': order_id,
        'transaction_id': transaction['id'] if transaction else None,
        'synced': transaction is not None
    }


async def recalculate_all_reports(
    db: AsyncIOMotorDatabase,
    date_str: Optional[str] = None
):
    """
    Recalculate all reports for a specific date or all dates
    """
    # Get all unique dates and businesses from transactions
    pipeline = [
        {
            '$project': {
                'date': {'$substr': ['$transaction_date', 0, 10]},
                'business_id': 1,
                'transaction_type': 1,
                'amount': 1
            }
        }
    ]
    
    if date_str:
        pipeline.insert(0, {
            '$match': {
                'transaction_date': {'$regex': f'^{date_str}'}
            }
        })
    
    pipeline.extend([
        {
            '$group': {
                '_id': {
                    'date': '$date',
                    'business_id': '$business_id',
                    'type': '$transaction_type'
                },
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        }
    ])
    
    # Collect data by date and business
    report_data = {}
    async for result in db.accounting.aggregate(pipeline):
        key = (result['_id']['date'], result['_id']['business_id'])
        if key not in report_data:
            report_data[key] = {
                'date': result['_id']['date'],
                'business_id': result['_id']['business_id'],
                'revenue': 0,
                'expenses': 0,
                'transaction_count': 0
            }
        
        if result['_id']['type'] == 'revenue':
            report_data[key]['revenue'] = result['total']
            report_data[key]['transaction_count'] = result['count']
        else:
            report_data[key]['expenses'] = result['total']
    
    # Update reports
    updated_count = 0
    for (report_date, business_id), data in report_data.items():
        # Update loket report
        await db.loket_reports.update_one(
            {
                'business_id': business_id,
                'report_date': report_date
            },
            {
                '$set': {
                    'total_revenue': data['revenue'],
                    'total_transactions': data['transaction_count'],
                    'updated_at': utc_now().isoformat()
                }
            },
            upsert=False
        )
        
        # Update kasir report
        await db.kasir_reports.update_one(
            {
                'business_id': business_id,
                'report_date': report_date
            },
            {
                '$set': {
                    'total_revenue': data['revenue'],
                    'total_expenses': data['expenses'],
                    'net_income': data['revenue'] - data['expenses'],
                    'updated_at': utc_now().isoformat()
                }
            },
            upsert=False
        )
        
        updated_count += 1
    
    return {
        'success': True,
        'updated_reports': updated_count,
        'date': date_str or 'all'
    }


async def get_sync_status(
    db: AsyncIOMotorDatabase,
    business_id: Optional[str] = None
) -> dict:
    """
    Get synchronization status between orders, transactions, and reports
    """
    query = {}
    if business_id:
        query['business_id'] = business_id
    
    # Count completed orders
    completed_orders = await db.orders.count_documents({
        **query,
        'status': 'completed'
    })
    
    # Count transactions with related orders
    transactions_with_orders = await db.accounting.count_documents({
        **query,
        'related_order_id': {'$exists': True, '$ne': None}
    })
    
    # Count reports
    loket_reports_count = await db.loket_reports.count_documents(query)
    kasir_reports_count = await db.kasir_reports.count_documents(query)
    
    # Calculate sync percentage
    sync_percentage = 0
    if completed_orders > 0:
        sync_percentage = (transactions_with_orders / completed_orders) * 100
    
    return {
        'completed_orders': completed_orders,
        'transactions_synced': transactions_with_orders,
        'loket_reports': loket_reports_count,
        'kasir_reports': kasir_reports_count,
        'sync_percentage': round(sync_percentage, 2),
        'needs_sync': completed_orders - transactions_with_orders,
        'business_id': business_id or 'all'
    }


async def auto_sync_missing_transactions(
    db: AsyncIOMotorDatabase,
    user_id: str
) -> dict:
    """
    Auto-sync all completed orders that don't have transactions yet
    """
    # Find completed orders without transactions
    completed_orders = []
    async for order in db.orders.find({'status': 'completed'}):
        # Check if transaction exists
        trans = await db.accounting.find_one({'related_order_id': order['id']})
        if not trans:
            completed_orders.append(order)
    
    # Create transactions for missing orders
    created_count = 0
    for order in completed_orders:
        transaction = await auto_create_transaction_from_order(db, order, user_id)
        if transaction:
            created_count += 1
    
    return {
        'success': True,
        'orders_checked': len(completed_orders),
        'transactions_created': created_count
    }
