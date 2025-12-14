from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

# Import models
from models import *

# Import utils
from utils.auth import (
    get_password_hash, verify_password, create_access_token, 
    get_current_user, decode_token
)
from utils.permissions import check_permission, require_permission, ROLE_OWNER
from utils.helpers import generate_id, generate_code, utc_now

# Activity logging helper
async def log_activity(
    user_id: str,
    action: str,
    description: str,
    ip_address: str = '0.0.0.0',
    related_type: str = None,
    related_id: str = None,
    metadata: dict = None
):
    """Log user activity for audit trail"""
    activity_log = {
        'id': generate_id(),
        'user_id': user_id,
        'action': action,
        'description': description,
        'ip_address': ip_address,
        'related_type': related_type,
        'related_id': related_id,
        'metadata': metadata or {},
        'created_at': utc_now().isoformat()
    }
    await db.activity_logs.insert_one(activity_log)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection (Kubernetes will inject MONGO_URL and DB_NAME, fallback for local dev)
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'gelis_db')]

# Create the main app
app = FastAPI(title='GELIS - Sistem Monitoring Operasional Multi-Bisnis')
api_router = APIRouter(prefix='/api')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= AUTH ROUTES =============
@api_router.post('/auth/register', response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({
        '$or': [
            {'username': user_data.username},
            {'email': user_data.email}
        ]
    }, {'_id': 0})
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username atau email sudah terdaftar'
        )
    
    # Create new user
    user_dict = user_data.model_dump(exclude={'password'})
    user_dict['id'] = generate_id()
    user_dict['password'] = get_password_hash(user_data.password)
    user_dict['created_at'] = utc_now()
    user_dict['updated_at'] = utc_now()
    user_dict['last_login'] = None
    
    # Serialize datetimes
    doc = user_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.users.insert_one(doc)
    
    # Get role name
    role = await db.roles.find_one({'id': user_dict['role_id']}, {'_id': 0})
    user_dict['role_name'] = role['name'] if role else None
    
    return UserResponse(**user_dict)

@api_router.post('/auth/login', response_model=Token)
async def login(login_data: UserLogin, request: Request):
    # Find user
    user = await db.users.find_one({
        '$or': [
            {'username': login_data.identifier},
            {'email': login_data.identifier}
        ]
    }, {'_id': 0})
    
    if not user or not verify_password(login_data.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Username/email atau password salah'
        )
    
    if not user.get('is_active'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Akun Anda tidak aktif'
        )
    
    # Update last login
    await db.users.update_one(
        {'id': user['id']},
        {'$set': {'last_login': utc_now().isoformat()}}
    )
    
    # Log login activity
    await log_activity(
        user_id=user['id'],
        action='login',
        description=f"User {user['username']} logged in successfully",
        ip_address=request.client.host,
        related_type='user',
        related_id=user['id'],
        metadata={'username': user['username'], 'role_id': user['role_id'], 'user_agent': request.headers.get('user-agent')}
    )
    
    # Create access token
    access_token = create_access_token(data={
        'sub': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role_id': user['role_id']
    })
    
    # Get role name
    role = await db.roles.find_one({'id': user['role_id']}, {'_id': 0})
    user['role_name'] = role['name'] if role else None
    
    # Parse datetime fields
    if isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    if isinstance(user['updated_at'], str):
        user['updated_at'] = datetime.fromisoformat(user['updated_at'])
    if user.get('last_login') and isinstance(user['last_login'], str):
        user['last_login'] = datetime.fromisoformat(user['last_login'])
    
    return Token(
        access_token=access_token,
        user=UserResponse(**user)
    )

@api_router.get('/auth/me', response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=404, detail='User tidak ditemukan')
    
    # Get role name
    role = await db.roles.find_one({'id': user['role_id']}, {'_id': 0})
    user['role_name'] = role['name'] if role else None
    
    # Parse datetime fields
    if isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    if isinstance(user['updated_at'], str):
        user['updated_at'] = datetime.fromisoformat(user['updated_at'])
    if user.get('last_login') and isinstance(user['last_login'], str):
        user['last_login'] = datetime.fromisoformat(user['last_login'])
    
    return UserResponse(**user)

# ============= DASHBOARD ROUTES =============
@api_router.get('/dashboard/stats', response_model=DashboardStats)
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get counts
    total_businesses = await db.businesses.count_documents({'is_active': True})
    total_orders = await db.orders.count_documents({})
    active_orders = await db.orders.count_documents({'status': {'$nin': ['completed', 'cancelled']}})
    pending_orders = await db.orders.count_documents({'status': 'pending'})
    
    # Get today's completed orders
    completed_orders_today = await db.orders.count_documents({
        'status': 'completed',
        'completion_date': {'$gte': today_start.isoformat()}
    })
    
    # Calculate revenue and expenses
    revenue_pipeline = [
        {'$match': {'transaction_type': 'income'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    revenue_result = await db.transactions.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]['total'] if revenue_result else 0
    
    expense_pipeline = [
        {'$match': {'transaction_type': 'expense'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    expense_result = await db.transactions.aggregate(expense_pipeline).to_list(1)
    total_expenses = expense_result[0]['total'] if expense_result else 0
    
    # Today's revenue
    revenue_today_pipeline = [
        {'$match': {'transaction_type': 'income', 'created_at': {'$gte': today_start.isoformat()}}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    revenue_today_result = await db.transactions.aggregate(revenue_today_pipeline).to_list(1)
    revenue_today = revenue_today_result[0]['total'] if revenue_today_result else 0
    
    # Today's expenses
    expenses_today_pipeline = [
        {'$match': {'transaction_type': 'expense', 'created_at': {'$gte': today_start.isoformat()}}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ]
    expenses_today_result = await db.transactions.aggregate(expenses_today_pipeline).to_list(1)
    expenses_today = expenses_today_result[0]['total'] if expenses_today_result else 0
    
    return DashboardStats(
        total_businesses=total_businesses,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_expenses=total_expenses,
        active_orders=active_orders,
        pending_orders=pending_orders,
        completed_orders_today=completed_orders_today,
        revenue_today=revenue_today,
        expenses_today=expenses_today,
        net_today=revenue_today - expenses_today
    )

# ============= BUSINESS ROUTES =============
@api_router.get('/businesses', response_model=List[Business])
async def get_businesses(current_user: dict = Depends(get_current_user)):
    # Check permission - Only Owner & Manager can view businesses
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Bisnis')
    
    businesses = await db.businesses.find({}, {'_id': 0}).to_list(1000)
    for biz in businesses:
        if isinstance(biz.get('created_at'), str):
            biz['created_at'] = datetime.fromisoformat(biz['created_at'])
        if isinstance(biz.get('updated_at'), str):
            biz['updated_at'] = datetime.fromisoformat(biz['updated_at'])
    return businesses

@api_router.post('/businesses', response_model=Business)
async def create_business(business_data: BusinessCreate, current_user: dict = Depends(get_current_user)):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    biz_dict = business_data.model_dump()
    biz_dict['id'] = generate_id()
    biz_dict['created_by'] = current_user['sub']
    biz_dict['created_at'] = utc_now()
    biz_dict['updated_at'] = utc_now()
    
    # Serialize datetimes
    doc = biz_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.businesses.insert_one(doc)
    
    return Business(**biz_dict)

@api_router.get('/businesses/{business_id}', response_model=Business)
async def get_business(business_id: str, current_user: dict = Depends(get_current_user)):
    business = await db.businesses.find_one({'id': business_id}, {'_id': 0})
    if not business:
        raise HTTPException(status_code=404, detail='Bisnis tidak ditemukan')
    
    if isinstance(business.get('created_at'), str):
        business['created_at'] = datetime.fromisoformat(business['created_at'])
    if isinstance(business.get('updated_at'), str):
        business['updated_at'] = datetime.fromisoformat(business['updated_at'])
    
    return Business(**business)

# ============= ORDER ROUTES =============
@api_router.get('/orders', response_model=List[Order])
async def get_orders(
    business_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Owner, Manager, Kasir, Loket only
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 5, 6]:  # Owner, Manager, Kasir, Loket
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Pesanan')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if status_filter:
        query['status'] = status_filter
    
    # Pagination for faster loading (default: 100 latest orders)
    orders = await db.orders.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    for order in orders:
        for field in ['created_at', 'updated_at', 'completion_date']:
            if order.get(field) and isinstance(order[field], str):
                order[field] = datetime.fromisoformat(order[field])
    return orders

@api_router.post('/orders', response_model=Order)
async def create_order(order_data: OrderCreate, current_user: dict = Depends(get_current_user)):
    order_dict = order_data.model_dump()
    order_dict['id'] = generate_id()
    order_dict['order_number'] = generate_code('ORD', 12)
    order_dict['status'] = OrderStatus.PENDING
    
    # Auto-set payment status based on paid_amount
    if order_dict.get('paid_amount', 0) >= order_dict.get('total_amount', 0):
        order_dict['payment_status'] = PaymentStatus.PAID
    elif order_dict.get('paid_amount', 0) > 0:
        order_dict['payment_status'] = PaymentStatus.PARTIAL
    else:
        order_dict['payment_status'] = PaymentStatus.UNPAID
    
    order_dict['created_by'] = current_user['sub']
    order_dict['created_at'] = utc_now()
    order_dict['updated_at'] = utc_now()
    
    # Serialize datetimes
    doc = order_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.orders.insert_one(doc)
    
    # AUTO-CREATE TRANSACTION if payment received on creation
    if order_dict.get('paid_amount', 0) > 0:
        transaction = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'business_id': order_dict['business_id'],
            'transaction_type': 'income',
            'category': 'Order Payment',
            'description': f"Pembayaran order {order_dict['order_number']} - {order_dict['customer_name']}",
            'amount': order_dict['paid_amount'],
            'payment_method': order_dict.get('payment_method', 'cash'),
            'reference_number': order_dict['order_number'],
            'order_id': order_dict['id'],
            'created_by': current_user['sub'],
            'created_at': utc_now().isoformat()
        }
        await db.transactions.insert_one(transaction)
        
        # Log activity
        await log_activity(
            user_id=current_user['sub'],
            action='order_created_with_payment',
            description=f"Order {order_dict['order_number']} dibuat dengan pembayaran {order_dict['paid_amount']} - Auto transaction created",
            related_type='order',
            related_id=order_dict['id'],
            metadata={'order_number': order_dict['order_number'], 'amount': order_dict['paid_amount']}
        )
    
    # Create notification for manager
    notif = {
        'id': generate_id(),
        'user_id': 'broadcast_manager',  # Special ID for broadcast
        'title': 'Pesanan Baru',
        'message': f"Pesanan baru {order_dict['order_number']} dari {order_dict['customer_name']}",
        'type': 'info',
        'related_id': order_dict['id'],
        'related_type': 'order',
        'is_read': False,
        'created_at': utc_now().isoformat()
    }
    await db.notifications.insert_one(notif)
    
    return Order(**order_dict)

@api_router.put('/orders/{order_id}')
async def update_order(
    order_id: str,
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    paid_amount: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    # Get existing order
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    update_data = {'updated_at': utc_now().isoformat()}
    
    if status:
        update_data['status'] = status
        if status == 'completed':
            update_data['completion_date'] = utc_now().isoformat()
    
    if payment_status:
        update_data['payment_status'] = payment_status
    
    if assigned_to:
        update_data['assigned_to'] = assigned_to
        # Create notification for assigned user
        notif = {
            'id': generate_id(),
            'user_id': assigned_to,
            'title': 'Pesanan Ditugaskan',
            'message': f"Anda ditugaskan untuk pesanan {order['order_number']}",
            'type': 'info',
            'related_id': order_id,
            'related_type': 'order',
            'is_read': False,
            'created_at': utc_now().isoformat()
        }
        await db.notifications.insert_one(notif)
    
    # AUTO-CREATE TRANSACTION when payment received
    if paid_amount is not None and paid_amount > 0:
        old_paid = order.get('paid_amount', 0)
        new_payment = paid_amount - old_paid
        
        if new_payment > 0:
            # Create income transaction automatically
            transaction = {
                'id': generate_id(),
                'transaction_code': generate_code('TXN', 12),
                'business_id': order['business_id'],
                'transaction_type': 'income',
                'category': 'Order Payment',
                'description': f"Pembayaran order {order['order_number']} - {order['customer_name']}",
                'amount': new_payment,
                'payment_method': order.get('payment_method', 'cash'),
                'reference_number': order['order_number'],
                'order_id': order_id,
                'created_by': current_user['sub'],
                'created_at': utc_now().isoformat()
            }
            await db.transactions.insert_one(transaction)
            
            # Log activity
            activity_log = {
                'id': generate_id(),
                'user_id': current_user['sub'],
                'action': 'payment_received',
                'description': f"Pembayaran {new_payment} untuk order {order['order_number']} - Auto transaction created",
                'ip_address': '0.0.0.0',
                'created_at': utc_now().isoformat()
            }
            await db.activity_logs.insert_one(activity_log)
        
        update_data['paid_amount'] = paid_amount
    
    result = await db.orders.update_one({'id': order_id}, {'$set': update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    return {'message': 'Order berhasil diupdate', 'auto_transaction_created': paid_amount is not None and (paid_amount - order.get('paid_amount', 0)) > 0}

# ============= TRANSACTION ROUTES =============
@api_router.get('/transactions', response_model=List[Transaction])
async def get_transactions(
    business_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Only Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 8]:  # Owner, Manager, Finance, IT Developer
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Akunting')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if transaction_type:
        query['transaction_type'] = transaction_type
    if start_date and end_date:
        query['created_at'] = {'$gte': start_date, '$lte': end_date}
    
    # Pagination for faster loading (default: 100 latest transactions)
    transactions = await db.transactions.find(query, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit).to_list(limit)
    for txn in transactions:
        if txn.get('created_at') and isinstance(txn['created_at'], str):
            txn['created_at'] = datetime.fromisoformat(txn['created_at'])
    
    return transactions

@api_router.post('/transactions', response_model=Transaction)
async def create_transaction(txn_data: TransactionCreate, current_user: dict = Depends(get_current_user)):
    txn_dict = txn_data.model_dump()
    txn_dict['id'] = generate_id()
    txn_dict['transaction_code'] = generate_code('TXN', 12)
    txn_dict['created_by'] = current_user['sub']
    txn_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = txn_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.transactions.insert_one(doc)
    
    return Transaction(**txn_dict)

@api_router.put('/transactions/{transaction_id}', response_model=Transaction)
async def update_transaction(
    transaction_id: str,
    txn_data: TransactionCreate,
    current_user: dict = Depends(get_current_user)
):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5]:  # Owner, Manager, Finance, Kasir
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    existing = await db.transactions.find_one({'id': transaction_id}, {'_id': 0})
    if not existing:
        raise HTTPException(status_code=404, detail='Transaksi tidak ditemukan')
    
    txn_dict = txn_data.model_dump()
    doc = txn_dict.copy()
    
    await db.transactions.update_one({'id': transaction_id}, {'$set': doc})
    
    existing.update(txn_dict)
    if isinstance(existing.get('created_at'), str):
        existing['created_at'] = datetime.fromisoformat(existing['created_at'])
    
    return Transaction(**existing)

@api_router.delete('/transactions/{transaction_id}')
async def delete_transaction(transaction_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - ONLY Owner can delete
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != 1:  # Only Owner
        raise HTTPException(status_code=403, detail='Hanya Owner yang dapat menghapus transaksi')
    
    # Get transaction details for logging
    transaction = await db.transactions.find_one({'id': transaction_id}, {'_id': 0})
    if not transaction:
        raise HTTPException(status_code=404, detail='Transaksi tidak ditemukan')
    
    result = await db.transactions.delete_one({'id': transaction_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Transaksi tidak ditemukan')
    
    # Log activity
    activity_log = {
        'id': generate_id(),
        'user_id': current_user['sub'],
        'action': 'delete_transaction',
        'description': f"Menghapus transaksi {transaction['transaction_code']} - {transaction['description']} (Rp {transaction['amount']})",
        'ip_address': '0.0.0.0',
        'created_at': utc_now().isoformat()
    }
    await db.activity_logs.insert_one(activity_log)
    
    return {'message': 'Transaksi berhasil dihapus'}


# ============= FINANCIAL DASHBOARD SUMMARY =============
@api_router.get('/financial/dashboard')
async def get_financial_dashboard(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Real-time financial dashboard - Membaca langsung dari transactions
    Menampilkan: Total Pemasukan, Pengeluaran, Laba, dan breakdown per kategori
    """
    # Check permission - Only Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke Financial Dashboard')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if start_date and end_date:
        query['created_at'] = {'$gte': start_date, '$lte': end_date}
    
    # Get all transactions (optimized: projection for only needed fields, max 5000 records)
    transactions = await db.transactions.find(
        query, 
        {'_id': 0, 'amount': 1, 'transaction_type': 1, 'category': 1, 'created_at': 1}
    ).limit(5000).to_list(5000)
    
    # Calculate totals
    total_income = sum(t['amount'] for t in transactions if t.get('transaction_type') == 'income')
    total_expense = sum(t['amount'] for t in transactions if t.get('transaction_type') == 'expense')
    net_profit = total_income - total_expense
    
    # Breakdown by category
    income_by_category = {}
    expense_by_category = {}
    
    for txn in transactions:
        category = txn.get('category', 'Lainnya')
        amount = txn.get('amount', 0)
        
        if txn.get('transaction_type') == 'income':
            income_by_category[category] = income_by_category.get(category, 0) + amount
        elif txn.get('transaction_type') == 'expense':
            expense_by_category[category] = expense_by_category.get(category, 0) + amount
    
    # Get orders summary for comparison (optimized: only fetch needed fields)
    order_query = {}
    if business_id:
        order_query['business_id'] = business_id
    if start_date and end_date:
        order_query['created_at'] = {'$gte': start_date, '$lte': end_date}
    
    orders = await db.orders.find(
        order_query, 
        {'_id': 0, 'total_amount': 1, 'payment_status': 1}
    ).limit(5000).to_list(5000)
    total_orders = len(orders)
    total_order_amount = sum(o.get('total_amount', 0) for o in orders)
    paid_orders = len([o for o in orders if o.get('payment_status') == 'paid'])
    pending_orders = len([o for o in orders if o.get('payment_status') in ['unpaid', 'partial']])
    
    return {
        'period': {
            'start_date': start_date or 'All time',
            'end_date': end_date or 'Now'
        },
        'financial_summary': {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'net_profit': round(net_profit, 2),
            'profit_margin': round((net_profit / total_income * 100), 2) if total_income > 0 else 0
        },
        'income_breakdown': income_by_category,
        'expense_breakdown': expense_by_category,
        'orders_summary': {
            'total_orders': total_orders,
            'total_order_amount': round(total_order_amount, 2),
            'paid_orders': paid_orders,
            'pending_orders': pending_orders,
            'payment_collection_rate': round((paid_orders / total_orders * 100), 2) if total_orders > 0 else 0
        },
        'transaction_count': {
            'total': len(transactions),
            'income_transactions': len([t for t in transactions if t.get('transaction_type') == 'income']),
            'expense_transactions': len([t for t in transactions if t.get('transaction_type') == 'expense'])
        }
    }

# ============= ACCOUNTING SUMMARY ROUTES =============
@api_router.get('/accounting/summary')
async def get_accounting_summary(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get accounting summary with debit/kredit totals"""
    # Check permission - Only Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Akunting')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if start_date and end_date:
        query['created_at'] = {'$gte': start_date, '$lte': end_date}
    
    # Get all transactions (optimized: projection for only needed fields, max 5000 records)
    transactions = await db.transactions.find(
        query, 
        {'_id': 0, 'amount': 1, 'transaction_type': 1, 'category': 1, 'created_at': 1}
    ).limit(5000).to_list(5000)
    
    # Calculate totals
    total_income = sum(t['amount'] for t in transactions if t['transaction_type'] == 'income')
    total_expense = sum(t['amount'] for t in transactions if t['transaction_type'] == 'expense')
    total_transfer = sum(t['amount'] for t in transactions if t['transaction_type'] == 'transfer')
    
    # Group by category
    categories = {}
    for txn in transactions:
        cat = txn.get('category', 'Other')
        if cat not in categories:
            categories[cat] = {'income': 0, 'expense': 0, 'count': 0}
        
        if txn['transaction_type'] == 'income':
            categories[cat]['income'] += txn['amount']
        elif txn['transaction_type'] == 'expense':
            categories[cat]['expense'] += txn['amount']
        categories[cat]['count'] += 1
    
    # Group by payment method
    payment_methods = {}
    for txn in transactions:
        method = txn.get('payment_method', 'Unknown')
        if method not in payment_methods:
            payment_methods[method] = {'total': 0, 'count': 0}
        payment_methods[method]['total'] += txn['amount']
        payment_methods[method]['count'] += 1
    
    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'total_transfer': total_transfer,
        'balance': total_income - total_expense,
        'transaction_count': len(transactions),
        'categories': categories,
        'payment_methods': payment_methods
    }

@api_router.get('/accounting/period-report')
async def get_period_report(
    period: str = 'daily',  # daily, weekly, monthly, yearly
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get period-based accounting report"""
    query = {}
    if business_id:
        query['business_id'] = business_id
    
    # Set default date range if not provided
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
    if not end_date:
        end_date = datetime.now().isoformat()
    
    query['created_at'] = {'$gte': start_date, '$lte': end_date}
    
    transactions = await db.transactions.find(query, {'_id': 0}).to_list(10000)
    
    # Group by period
    period_data = {}
    for txn in transactions:
        txn_date = datetime.fromisoformat(txn['created_at']) if isinstance(txn['created_at'], str) else txn['created_at']
        
        if period == 'daily':
            key = txn_date.strftime('%Y-%m-%d')
        elif period == 'weekly':
            key = f"{txn_date.year}-W{txn_date.isocalendar()[1]}"
        elif period == 'monthly':
            key = txn_date.strftime('%Y-%m')
        elif period == 'yearly':
            key = str(txn_date.year)
        else:
            key = txn_date.strftime('%Y-%m-%d')
        
        if key not in period_data:
            period_data[key] = {'income': 0, 'expense': 0, 'transfer': 0, 'count': 0}
        
        if txn['transaction_type'] == 'income':
            period_data[key]['income'] += txn['amount']
        elif txn['transaction_type'] == 'expense':
            period_data[key]['expense'] += txn['amount']
        elif txn['transaction_type'] == 'transfer':
            period_data[key]['transfer'] += txn['amount']
        period_data[key]['count'] += 1
    
    # Convert to list and sort
    report = []
    for period_key, data in sorted(period_data.items()):
        report.append({
            'period': period_key,
            'income': data['income'],
            'expense': data['expense'],
            'transfer': data['transfer'],
            'balance': data['income'] - data['expense'],
            'transaction_count': data['count']
        })
    
    return {
        'period_type': period,
        'start_date': start_date,
        'end_date': end_date,
        'data': report
    }

# ============= USER MANAGEMENT ROUTES =============
@api_router.get('/users', response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    # Check permission - Owner (1) and IT Developer (8) can view all users
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if not user or user.get('role_id') not in [1, 8]:  # Owner and IT Developer
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    users = await db.users.find({}, {'_id': 0, 'password': 0}).to_list(1000)
    
    # Get roles
    roles = await db.roles.find({}, {'_id': 0}).to_list(100)
    role_map = {r['id']: r['name'] for r in roles}
    
    for u in users:
        u['role_name'] = role_map.get(u['role_id'])
        for field in ['created_at', 'updated_at', 'last_login']:
            if u.get(field) and isinstance(u[field], str):
                u[field] = datetime.fromisoformat(u[field])
    
    return users

@api_router.put('/users/{user_id}', response_model=UserResponse)
async def update_user(user_id: str, user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    # Check permission - Owner or Manager (limited)
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail='User tidak ditemukan')
    
    # Manager can only edit non-owner users
    if user['role_id'] == 2 and target_user['role_id'] == 1:
        raise HTTPException(status_code=403, detail='Manager tidak bisa mengedit Owner')
    
    update_data = user_data.model_dump(exclude={'password'})
    update_data['updated_at'] = utc_now().isoformat()
    
    # Update password if provided
    if user_data.password:
        update_data['password'] = get_password_hash(user_data.password)
    
    await db.users.update_one({'id': user_id}, {'$set': update_data})
    
    # Get updated user
    updated_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    role = await db.roles.find_one({'id': updated_user['role_id']}, {'_id': 0})
    updated_user['role_name'] = role['name'] if role else None
    
    # Parse datetime
    for field in ['created_at', 'updated_at', 'last_login']:
        if updated_user.get(field) and isinstance(updated_user[field], str):
            updated_user[field] = datetime.fromisoformat(updated_user[field])
    
    return UserResponse(**updated_user)

@api_router.delete('/users/{user_id}')
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - Only Owner
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != 1:  # Only Owner
        raise HTTPException(status_code=403, detail='Hanya Owner yang dapat menghapus user')
    
    # Cannot delete self
    if user_id == current_user['sub']:
        raise HTTPException(status_code=400, detail='Tidak bisa menghapus akun sendiri')
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail='User tidak ditemukan')
    
    result = await db.users.delete_one({'id': user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='User tidak ditemukan')
    
    return {'message': 'User berhasil dihapus'}

@api_router.put('/users/{user_id}/toggle-active')
async def toggle_user_active(user_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != ROLE_OWNER:
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    target_user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not target_user:
        raise HTTPException(status_code=404, detail='User tidak ditemukan')
    
    new_status = not target_user.get('is_active', True)
    await db.users.update_one({'id': user_id}, {'$set': {'is_active': new_status}})
    
    return {'message': f"User {'diaktifkan' if new_status else 'dinonaktifkan'}"}

# ============= NOTIFICATION ROUTES =============
@api_router.get('/notifications', response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    notifications = await db.notifications.find(
        {'$or': [{'user_id': current_user['sub']}, {'user_id': 'broadcast_manager'}]},
        {'_id': 0}
    ).sort('created_at', -1).limit(100).to_list(100)
    
    for notif in notifications:
        if isinstance(notif.get('created_at'), str):
            notif['created_at'] = datetime.fromisoformat(notif['created_at'])
    
    return notifications

@api_router.put('/notifications/{notif_id}/read')
async def mark_notification_read(notif_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.notifications.update_one(
        {'id': notif_id, 'user_id': current_user['sub']},
        {'$set': {'is_read': True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Notifikasi tidak ditemukan')
    
    return {'message': 'Notifikasi ditandai sudah dibaca'}

# ============= ACTIVITY LOG ROUTES =============
@api_router.get('/activity-logs', response_model=List[ActivityLog])
async def get_activity_logs(
    user_id: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    query = {}
    if user_id:
        query['user_id'] = user_id
    
    logs = await db.activity_logs.find(query, {'_id': 0}).sort('created_at', -1).limit(limit).to_list(limit)
    
    for log in logs:
        if isinstance(log.get('created_at'), str):
            log['created_at'] = datetime.fromisoformat(log['created_at'])
    
    return logs

# ============= SETTINGS ROUTES =============
@api_router.get('/settings/{key}')
async def get_setting(key: str, current_user: dict = Depends(get_current_user)):
    setting = await db.settings.find_one({'setting_key': key}, {'_id': 0})
    if not setting:
        return {'setting_key': key, 'setting_value': {}}
    
    return setting

@api_router.put('/settings/{key}')
async def update_setting(key: str, value: dict, current_user: dict = Depends(get_current_user)):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != ROLE_OWNER:
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    await db.settings.update_one(
        {'setting_key': key},
        {
            '$set': {
                'setting_value': value,
                'updated_by': current_user['sub'],
                'updated_at': utc_now().isoformat()
            }
        },
        upsert=True
    )
    
    return {'message': 'Setting berhasil diupdate'}

# ============= DAILY REPORT ROUTES =============
@api_router.get('/reports/loket-daily', response_model=List[LoketDailyReport])
async def get_loket_daily_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Owner, Manager, Finance, Kasir, Loket
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5, 6]:  # Owner, Manager, Finance, Kasir, Loket
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Laporan')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if start_date and end_date:
        query['report_date'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    reports = await db.loket_daily_reports.find(query, {'_id': 0}).sort('report_date', -1).to_list(1000)
    
    for report in reports:
        if isinstance(report.get('report_date'), str):
            report['report_date'] = datetime.fromisoformat(report['report_date'])
        if isinstance(report.get('created_at'), str):
            report['created_at'] = datetime.fromisoformat(report['created_at'])
    
    return reports

@api_router.post('/reports/loket-daily', response_model=LoketDailyReport)
async def create_loket_daily_report(report_data: LoketDailyReportCreate, current_user: dict = Depends(get_current_user)):
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['created_by'] = current_user['sub']
    report_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['report_date'] = doc['report_date'].isoformat() if isinstance(doc['report_date'], datetime) else doc['report_date']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.loket_daily_reports.insert_one(doc)
    
    # AUTO-CREATE TRANSACTION for total setoran
    if report_dict.get('total_setoran_shift', 0) > 0:
        transaction = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'business_id': report_dict['business_id'],
            'transaction_type': 'income',
            'category': 'Setoran Loket',
            'description': f"Setoran harian loket shift {report_dict['shift']} - {report_dict['nama_petugas']}",
            'amount': report_dict['total_setoran_shift'],
            'payment_method': 'cash',
            'reference_number': f"LOKET-{doc['report_date']}-SHIFT{report_dict['shift']}",
            'order_id': None,
            'created_by': current_user['sub'],
            'created_at': utc_now().isoformat()
        }
        await db.transactions.insert_one(transaction)
    
    return LoketDailyReport(**report_dict)

@api_router.get('/reports/kasir-daily', response_model=List[KasirDailyReport])
async def get_kasir_daily_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Owner, Manager, Finance, Kasir, Loket
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5, 6]:  # Owner, Manager, Finance, Kasir, Loket
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Laporan')
    
    query = {}
    if business_id:
        query['business_id'] = business_id
    if start_date and end_date:
        query['report_date'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    reports = await db.kasir_daily_reports.find(query, {'_id': 0}).sort('report_date', -1).to_list(1000)
    
    for report in reports:
        if isinstance(report.get('report_date'), str):
            report['report_date'] = datetime.fromisoformat(report['report_date'])
        if isinstance(report.get('created_at'), str):
            report['created_at'] = datetime.fromisoformat(report['created_at'])
    
    return reports

@api_router.post('/reports/kasir-daily', response_model=KasirDailyReport)
async def create_kasir_daily_report(report_data: KasirDailyReportCreate, current_user: dict = Depends(get_current_user)):
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['created_by'] = current_user['sub']
    report_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['report_date'] = doc['report_date'].isoformat() if isinstance(doc['report_date'], datetime) else doc['report_date']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.kasir_daily_reports.insert_one(doc)
    
    # AUTO-CREATE TRANSACTIONS for kasir report
    transactions_created = []
    
    # Income: Total setoran (pagi + siang + sore)
    total_setoran = (report_dict.get('setoran_pagi', 0) + 
                     report_dict.get('setoran_siang', 0) + 
                     report_dict.get('setoran_sore', 0))
    
    if total_setoran > 0:
        txn = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'business_id': report_dict['business_id'],
            'transaction_type': 'income',
            'category': 'Setoran Kasir',
            'description': f"Total setoran harian kasir (Pagi: {report_dict.get('setoran_pagi', 0)}, Siang: {report_dict.get('setoran_siang', 0)}, Sore: {report_dict.get('setoran_sore', 0)})",
            'amount': total_setoran,
            'payment_method': 'cash',
            'reference_number': f"KASIR-{doc['report_date']}",
            'order_id': None,
            'created_by': current_user['sub'],
            'created_at': utc_now().isoformat()
        }
        await db.transactions.insert_one(txn)
        transactions_created.append('setoran')
    
    # Expense: Belanja loket
    if report_dict.get('belanja_loket', 0) > 0:
        txn = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'business_id': report_dict['business_id'],
            'transaction_type': 'expense',
            'category': 'Belanja Operasional',
            'description': 'Belanja loket harian',
            'amount': report_dict['belanja_loket'],
            'payment_method': 'cash',
            'reference_number': f"KASIR-{doc['report_date']}-BELANJA",
            'order_id': None,
            'created_by': current_user['sub'],
            'created_at': utc_now().isoformat()
        }
        await db.transactions.insert_one(txn)
        transactions_created.append('belanja')
    
    # Income: Admin fee
    if report_dict.get('total_admin', 0) > 0:
        txn = {
            'id': generate_id(),
            'transaction_code': generate_code('TXN', 12),
            'business_id': report_dict['business_id'],
            'transaction_type': 'income',
            'category': 'Admin Fee',
            'description': 'Penerimaan admin harian',
            'amount': report_dict['total_admin'],
            'payment_method': 'cash',
            'reference_number': f"KASIR-{doc['report_date']}-ADMIN",
            'order_id': None,
            'created_by': current_user['sub'],
            'created_at': utc_now().isoformat()
        }
        await db.transactions.insert_one(txn)
        transactions_created.append('admin')
    
    return KasirDailyReport(**report_dict)

@api_router.put('/reports/loket-daily/{report_id}', response_model=LoketDailyReport)
async def update_loket_daily_report(
    report_id: str,
    report_data: LoketDailyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Owner or Manager can edit
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin untuk mengedit laporan')
    
    # Get existing report
    existing = await db.loket_daily_reports.find_one({'id': report_id}, {'_id': 0})
    if not existing:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    report_dict = report_data.model_dump()
    report_dict['updated_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['report_date'] = doc['report_date'].isoformat() if isinstance(doc['report_date'], datetime) else doc['report_date']
    if 'updated_at' in doc and isinstance(doc['updated_at'], datetime):
        doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.loket_daily_reports.update_one({'id': report_id}, {'$set': doc})
    
    # Merge for response
    existing.update(report_dict)
    if isinstance(existing.get('report_date'), str):
        existing['report_date'] = datetime.fromisoformat(existing['report_date'])
    if isinstance(existing.get('created_at'), str):
        existing['created_at'] = datetime.fromisoformat(existing['created_at'])
    
    return LoketDailyReport(**existing)

@api_router.put('/reports/kasir-daily/{report_id}', response_model=KasirDailyReport)
async def update_kasir_daily_report(
    report_id: str,
    report_data: KasirDailyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    # Check permission - Owner or Manager can edit
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin untuk mengedit laporan')
    
    # Get existing report
    existing = await db.kasir_daily_reports.find_one({'id': report_id}, {'_id': 0})
    if not existing:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    report_dict = report_data.model_dump()
    report_dict['updated_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['report_date'] = doc['report_date'].isoformat() if isinstance(doc['report_date'], datetime) else doc['report_date']
    if 'updated_at' in doc and isinstance(doc['updated_at'], datetime):
        doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.kasir_daily_reports.update_one({'id': report_id}, {'$set': doc})
    
    # Merge for response
    existing.update(report_dict)
    if isinstance(existing.get('report_date'), str):
        existing['report_date'] = datetime.fromisoformat(existing['report_date'])
    if isinstance(existing.get('created_at'), str):
        existing['created_at'] = datetime.fromisoformat(existing['created_at'])
    
    return KasirDailyReport(**existing)


# ============= RECONCILIATION & VERIFICATION ROUTES =============
@api_router.get('/reports/reconciliation/kasir')
async def reconcile_kasir_report(
    report_date: str,
    business_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Rekonsiliasi Laporan Kasir dengan Transaksi Aktual
    Mendeteksi ketidaksesuaian data untuk verifikasi lebih lanjut
    """
    # Check permission - Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses rekonsiliasi')
    
    # Get kasir report for the date
    query = {'report_date': {'$gte': report_date, '$lt': report_date + 'T23:59:59'}}
    if business_id:
        query['business_id'] = business_id
    
    kasir_reports = await db.kasir_daily_reports.find(query, {'_id': 0}).to_list(100)
    
    if not kasir_reports:
        raise HTTPException(status_code=404, detail=f'Tidak ada laporan kasir untuk tanggal {report_date}')
    
    # Get actual transactions for the date (optimized: only needed fields)
    txn_query = {
        'created_at': {'$gte': report_date, '$lt': report_date + 'T23:59:59'},
        'category': {'$in': ['Order Payment', 'Setoran Kasir', 'Admin Fee', 'Belanja Loket']}
    }
    if business_id:
        txn_query['business_id'] = business_id
    
    transactions = await db.transactions.find(
        txn_query, 
        {'_id': 0, 'amount': 1, 'transaction_type': 1, 'category': 1}
    ).limit(2000).to_list(2000)
    
    # Calculate actual totals from transactions
    actual_income = sum(t['amount'] for t in transactions if t['transaction_type'] == 'income')
    actual_setoran_kasir = sum(t['amount'] for t in transactions if t.get('category') == 'Setoran Kasir')
    actual_admin = sum(t['amount'] for t in transactions if t.get('category') == 'Admin Fee')
    actual_belanja = sum(t['amount'] for t in transactions if t.get('category') == 'Belanja Loket')
    
    results = []
    
    for report in kasir_reports:
        # Calculate reported totals
        reported_setoran = (report.get('setoran_pagi', 0) + 
                           report.get('setoran_siang', 0) + 
                           report.get('setoran_sore', 0))
        reported_admin = report.get('total_admin', 0)
        reported_belanja = report.get('belanja_loket', 0)
        reported_total = reported_setoran + reported_admin - reported_belanja
        
        # Calculate discrepancies
        setoran_diff = reported_setoran - actual_setoran_kasir
        admin_diff = reported_admin - actual_admin
        belanja_diff = reported_belanja - actual_belanja
        
        # Determine status
        has_discrepancy = abs(setoran_diff) > 1000 or abs(admin_diff) > 100 or abs(belanja_diff) > 100
        
        discrepancy_details = []
        if abs(setoran_diff) > 1000:
            discrepancy_details.append({
                'category': 'Setoran Kasir',
                'reported': reported_setoran,
                'actual': actual_setoran_kasir,
                'difference': setoran_diff,
                'percentage': round((setoran_diff / reported_setoran * 100), 2) if reported_setoran > 0 else 0
            })
        
        if abs(admin_diff) > 100:
            discrepancy_details.append({
                'category': 'Admin Fee',
                'reported': reported_admin,
                'actual': actual_admin,
                'difference': admin_diff,
                'percentage': round((admin_diff / reported_admin * 100), 2) if reported_admin > 0 else 0
            })
        
        if abs(belanja_diff) > 100:
            discrepancy_details.append({
                'category': 'Belanja Loket',
                'reported': reported_belanja,
                'actual': actual_belanja,
                'difference': belanja_diff,
                'percentage': round((belanja_diff / reported_belanja * 100), 2) if reported_belanja > 0 else 0
            })
        
        result = {
            'report_id': report['id'],
            'report_date': report['report_date'],
            'business_id': report['business_id'],
            'status': 'DISCREPANCY' if has_discrepancy else 'MATCHED',
            'reported_total': round(reported_total, 2),
            'actual_total': round(actual_income - actual_belanja, 2),
            'total_difference': round(reported_total - (actual_income - actual_belanja), 2),
            'breakdown': {
                'setoran_kasir': {
                    'reported': reported_setoran,
                    'actual': actual_setoran_kasir,
                    'difference': setoran_diff
                },
                'admin_fee': {
                    'reported': reported_admin,
                    'actual': actual_admin,
                    'difference': admin_diff
                },
                'belanja_loket': {
                    'reported': reported_belanja,
                    'actual': actual_belanja,
                    'difference': belanja_diff
                }
            },
            'discrepancies': discrepancy_details,
            'requires_investigation': has_discrepancy,
            'created_by': report.get('created_by'),
            'notes': report.get('notes')
        }
        
        results.append(result)
    
    return {
        'reconciliation_date': report_date,
        'total_reports': len(results),
        'matched_reports': len([r for r in results if r['status'] == 'MATCHED']),
        'discrepancy_reports': len([r for r in results if r['status'] == 'DISCREPANCY']),
        'reports': results
    }

@api_router.get('/reports/reconciliation/loket')
async def reconcile_loket_report(
    report_date: str,
    business_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Rekonsiliasi Laporan Loket dengan Transaksi Aktual
    Verifikasi pelunasan per bank dengan data transaksi
    """
    # Check permission - Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses rekonsiliasi')
    
    # Get loket reports for the date
    query = {'report_date': {'$gte': report_date, '$lt': report_date + 'T23:59:59'}}
    if business_id:
        query['business_id'] = business_id
    
    loket_reports = await db.loket_daily_reports.find(query, {'_id': 0}).to_list(100)
    
    if not loket_reports:
        raise HTTPException(status_code=404, detail=f'Tidak ada laporan loket untuk tanggal {report_date}')
    
    # Get actual transactions for the date (optimized: only needed fields)
    txn_query = {
        'created_at': {'$gte': report_date, '$lt': report_date + 'T23:59:59'},
        'category': {'$in': ['Order Payment', 'Setoran Loket']}
    }
    if business_id:
        txn_query['business_id'] = business_id
    
    transactions = await db.transactions.find(
        txn_query, 
        {'_id': 0, 'amount': 1, 'category': 1}
    ).limit(2000).to_list(2000)
    
    # Calculate actual total
    actual_total_setoran = sum(t['amount'] for t in transactions if t.get('category') == 'Setoran Loket')
    
    results = []
    
    for report in loket_reports:
        reported_total = report.get('total_setoran_shift', 0)
        
        # Check bank balances consistency
        bank_balance_checks = []
        total_bank_setoran = 0
        
        for bank in report.get('bank_balances', []):
            expected_saldo_akhir = (bank['saldo_awal'] + 
                                   bank['saldo_inject'] - 
                                   bank['data_lunas'] - 
                                   bank['setor_kasir'] - 
                                   bank['transfer_amount'])
            
            saldo_match = abs(expected_saldo_akhir - bank['saldo_akhir']) < 100
            total_bank_setoran += bank['sisa_setoran']
            
            bank_balance_checks.append({
                'bank_name': bank['bank_name'],
                'reported_saldo_akhir': bank['saldo_akhir'],
                'calculated_saldo_akhir': expected_saldo_akhir,
                'is_balanced': saldo_match,
                'difference': bank['saldo_akhir'] - expected_saldo_akhir,
                'sisa_setoran': bank['sisa_setoran']
            })
        
        # Compare report total with actual transactions
        difference = reported_total - actual_total_setoran
        has_discrepancy = abs(difference) > 1000 or any(not b['is_balanced'] for b in bank_balance_checks)
        
        result = {
            'report_id': report['id'],
            'report_date': report['report_date'],
            'business_id': report['business_id'],
            'shift': report.get('shift'),
            'nama_petugas': report.get('nama_petugas'),
            'status': 'DISCREPANCY' if has_discrepancy else 'MATCHED',
            'reported_total_setoran': reported_total,
            'actual_total_setoran': actual_total_setoran,
            'difference': difference,
            'bank_balances': bank_balance_checks,
            'all_banks_balanced': all(b['is_balanced'] for b in bank_balance_checks),
            'requires_investigation': has_discrepancy,
            'notes': report.get('notes')
        }
        
        results.append(result)
    
    return {
        'reconciliation_date': report_date,
        'total_reports': len(results),
        'matched_reports': len([r for r in results if r['status'] == 'MATCHED']),
        'discrepancy_reports': len([r for r in results if r['status'] == 'DISCREPANCY']),
        'reports': results
    }

@api_router.get('/reports/verification/summary')
async def get_verification_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Summary verifikasi semua laporan dalam periode tertentu
    Menampilkan overview discrepancies yang perlu investigasi
    """
    # Check permission - Owner, Manager, Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses verifikasi')
    
    # Default to last 7 days if not specified
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get all kasir reports in period
    kasir_query = {
        'report_date': {'$gte': start_date, '$lt': end_date + 'T23:59:59'}
    }
    kasir_reports = await db.kasir_daily_reports.find(kasir_query, {'_id': 0}).to_list(1000)
    
    # Get all loket reports in period
    loket_reports = await db.loket_daily_reports.find(kasir_query, {'_id': 0}).to_list(1000)
    
    # Get all transactions in period (optimized: only needed fields for summary)
    txn_query = {
        'created_at': {'$gte': start_date, '$lt': end_date + 'T23:59:59'}
    }
    transactions = await db.transactions.find(
        txn_query, 
        {'_id': 0, 'amount': 1, 'transaction_type': 1}
    ).limit(3000).to_list(3000)
    
    # Analyze discrepancies
    kasir_total_reported = sum(r.get('setoran_pagi', 0) + r.get('setoran_siang', 0) + r.get('setoran_sore', 0) for r in kasir_reports)
    loket_total_reported = sum(r.get('total_setoran_shift', 0) for r in loket_reports)
    
    actual_total = sum(t['amount'] for t in transactions if t['transaction_type'] == 'income')
    
    return {
        'period': {
            'start_date': start_date,
            'end_date': end_date
        },
        'summary': {
            'total_kasir_reports': len(kasir_reports),
            'total_loket_reports': len(loket_reports),
            'kasir_total_reported': round(kasir_total_reported, 2),
            'loket_total_reported': round(loket_total_reported, 2),
            'actual_total_transactions': round(actual_total, 2),
            'overall_difference': round((kasir_total_reported + loket_total_reported) - actual_total, 2)
        },
        'verification_status': {
            'requires_investigation': abs((kasir_total_reported + loket_total_reported) - actual_total) > 10000,
            'tolerance_threshold': 10000,
            'accuracy_rate': round((1 - abs((kasir_total_reported + loket_total_reported) - actual_total) / actual_total) * 100, 2) if actual_total > 0 else 100
        },
        'recommendations': [
            'Lakukan rekonsiliasi harian untuk setiap tanggal' if abs((kasir_total_reported + loket_total_reported) - actual_total) > 10000 else 'Data akurat, tidak ada investigasi diperlukan',
            'Periksa laporan kasir dengan discrepancy > 1%' if actual_total > 0 and abs(kasir_total_reported - actual_total) / actual_total > 0.01 else 'Laporan kasir sesuai',
            'Verifikasi saldo bank di laporan loket' if len(loket_reports) > 0 else 'Tidak ada laporan loket'
        ]
    }


@api_router.delete('/reports/loket-daily/{report_id}')
async def delete_loket_daily_report(report_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - only Owner can delete
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != 1:  # Only Owner
        raise HTTPException(status_code=403, detail='Hanya Owner yang dapat menghapus laporan')
    
    result = await db.loket_daily_reports.delete_one({'id': report_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    return {'message': 'Laporan berhasil dihapus'}

@api_router.delete('/reports/kasir-daily/{report_id}')
async def delete_kasir_daily_report(report_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - only Owner can delete
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != 1:  # Only Owner
        raise HTTPException(status_code=403, detail='Hanya Owner yang dapat menghapus laporan')
    
    result = await db.kasir_daily_reports.delete_one({'id': report_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    return {'message': 'Laporan berhasil dihapus'}

# ============= TEKNISI ROUTES =============
@api_router.get('/teknisi/orders', response_model=List[Order])
async def get_teknisi_orders(current_user: dict = Depends(get_current_user)):
    # Get orders assigned to current teknisi - ONLY orders that require technician
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    # Check permission - Owner, Manager, Kasir, Teknisi
    if user['role_id'] not in [1, 2, 5, 7]:  # Owner, Manager, Kasir, Teknisi
        raise HTTPException(status_code=403, detail='Tidak memiliki akses ke menu Pekerjaan Teknisi')
    
    # Base query: only orders that require technician
    query = {'requires_technician': True}
    
    # If teknisi, only show assigned orders. If manager/owner/kasir, show all
    if user['role_id'] == 7:  # Teknisi
        query['assigned_to'] = current_user['sub']
    
    orders = await db.orders.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
    for order in orders:
        for field in ['created_at', 'updated_at', 'completion_date']:
            if order.get(field) and isinstance(order[field], str):
                order[field] = datetime.fromisoformat(order[field])
    
    return orders

@api_router.put('/teknisi/orders/{order_id}/status')
async def update_order_status_by_teknisi(
    order_id: str,
    status: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Teknisi can update status of their assigned orders
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    # Check permission
    if user['role_id'] == 7:  # Teknisi
        if order['assigned_to'] != current_user['sub']:
            raise HTTPException(status_code=403, detail='Order tidak di-assign ke Anda')
    elif user['role_id'] not in [1, 2]:  # Not owner or manager
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    # Validate status
    valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail='Status tidak valid')
    
    update_data = {
        'status': status,
        'updated_at': utc_now().isoformat()
    }
    
    if status == 'completed':
        update_data['completion_date'] = utc_now().isoformat()
    
    if notes:
        current_notes = order.get('notes', '')
        timestamp = utc_now().strftime('%Y-%m-%d %H:%M:%S')
        user_name = user.get('full_name', user.get('username', 'Unknown'))
        update_data['notes'] = f"{current_notes}\n[{timestamp}] {user_name}: {notes}".strip()
    
    await db.orders.update_one({'id': order_id}, {'$set': update_data})
    
    # Log activity
    activity_log = {
        'id': generate_id(),
        'user_id': current_user['sub'],
        'action': 'update_order_status',
        'description': f"Update status order {order['order_number']} menjadi {status}",
        'ip_address': '0.0.0.0',
        'created_at': utc_now().isoformat()
    }
    await db.activity_logs.insert_one(activity_log)
    
    return {'message': f'Status order berhasil diupdate menjadi {status}'}

@api_router.put('/teknisi/orders/{order_id}/progress')
async def update_order_progress(
    order_id: str,
    progress: int,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    # Teknisi can update progress (0-100%)
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    order = await db.orders.find_one({'id': order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    # Check permission
    if user['role_id'] == 7:  # Teknisi
        if order['assigned_to'] != current_user['sub']:
            raise HTTPException(status_code=403, detail='Order tidak di-assign ke Anda')
    elif user['role_id'] not in [1, 2]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail='Progress harus antara 0-100')
    
    update_data = {
        'order_details.progress': progress,
        'updated_at': utc_now().isoformat()
    }
    
    # Auto update status based on progress
    if progress == 0:
        update_data['status'] = 'pending'
    elif progress > 0 and progress < 100:
        update_data['status'] = 'processing'
    elif progress == 100:
        update_data['status'] = 'completed'
        update_data['completion_date'] = utc_now().isoformat()
    
    if notes:
        current_notes = order.get('notes', '')
        timestamp = utc_now().strftime('%Y-%m-%d %H:%M:%S')
        update_data['notes'] = f"{current_notes}\n[{timestamp}] Progress {progress}%: {notes}".strip()
    
    await db.orders.update_one({'id': order_id}, {'$set': update_data})
    
    return {'message': f'Progress order berhasil diupdate menjadi {progress}%'}

# ============= AUTO GENERATE REPORTS =============
@api_router.post('/reports/generate-loket')
async def generate_loket_report(
    business_id: str,
    report_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto-generate laporan loket dari data orders"""
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    # Parse date
    target_date = datetime.fromisoformat(report_date).replace(hour=0, minute=0, second=0, microsecond=0)
    next_day = target_date.replace(hour=23, minute=59, second=59)
    
    # Get orders for the day
    orders = await db.orders.find({
        'business_id': business_id,
        'created_at': {
            '$gte': target_date.isoformat(),
            '$lte': next_day.isoformat()
        }
    }, {'_id': 0}).to_list(1000)
    
    # Calculate totals
    total_lunas = sum(o.get('paid_amount', 0) for o in orders if o.get('payment_status') == 'paid')
    
    # Get business settings for banks
    business = await db.businesses.find_one({'id': business_id}, {'_id': 0})
    banks = business.get('settings', {}).get('banks', ['BRIS', 'MANDIRI'])
    
    # Create bank balances structure
    bank_balances = []
    for bank_name in banks:
        bank_balances.append({
            'bank_name': bank_name,
            'saldo_awal': 0,
            'saldo_inject': 0,
            'data_lunas': total_lunas / len(banks),  # Distribute evenly
            'setor_kasir': 0,
            'transfer_amount': 0,
            'sisa_setoran': total_lunas / len(banks),
            'saldo_akhir': 0,
            'uang_lebih': 0
        })
    
    generated_data = {
        'business_id': business_id,
        'report_date': target_date.isoformat(),
        'nama_petugas': user['full_name'],
        'shift': 1,
        'bank_balances': bank_balances,
        'total_setoran_shift': total_lunas,
        'notes': f"Auto-generated dari {len(orders)} orders"
    }
    
    return generated_data

@api_router.post('/reports/generate-kasir')
async def generate_kasir_report(
    business_id: str,
    report_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Auto-generate laporan kasir dari data transactions"""
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    # Parse date
    target_date = datetime.fromisoformat(report_date).replace(hour=0, minute=0, second=0, microsecond=0)
    next_day = target_date.replace(hour=23, minute=59, second=59)
    
    # Get transactions for the day
    transactions = await db.transactions.find({
        'business_id': business_id,
        'created_at': {
            '$gte': target_date.isoformat(),
            '$lte': next_day.isoformat()
        }
    }, {'_id': 0}).to_list(1000)
    
    # Calculate totals by time (rough estimation)
    total_income = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'income')
    setoran_pagi = total_income * 0.4  # 40% morning
    setoran_siang = total_income * 0.35  # 35% afternoon
    setoran_sore = total_income * 0.25  # 25% evening
    
    # Get transfers
    transfers = [t for t in transactions if t.get('transaction_type') == 'transfer']
    topup_transactions = [{'amount': t['amount'], 'description': t.get('description', '')} for t in transfers]
    
    # Calculate admin & kas kecil
    expenses = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'expense')
    
    generated_data = {
        'business_id': business_id,
        'report_date': target_date.isoformat(),
        'setoran_pagi': setoran_pagi,
        'setoran_siang': setoran_siang,
        'setoran_sore': setoran_sore,
        'setoran_deposit_loket_luar': 0,
        'setoran_pelunasan_pagi': 0,
        'setoran_pelunasan_siang': 0,
        'topup_transactions': topup_transactions,
        'total_topup': sum(t['amount'] for t in topup_transactions),
        'penerimaan_kas_kecil': 0,
        'pengurangan_kas_kecil': expenses * 0.1,
        'belanja_loket': expenses * 0.9,
        'total_kas_kecil': 0,
        'penerimaan_admin': total_income * 0.02,  # 2% commission
        'total_admin': total_income * 0.02,
        'saldo_bank': 0,
        'saldo_brankas': total_income * 0.02,
        'notes': f"Auto-generated dari {len(transactions)} transaksi"
    }
    
    return generated_data

# ============= ACCOUNTING ROUTES =============
@api_router.get('/accounting/accounts')
async def get_accounts(current_user: dict = Depends(get_current_user)):
    accounts = await db.accounts.find({}, {'_id': 0}).to_list(1000)
    for acc in accounts:
        if isinstance(acc.get('created_at'), str):
            acc['created_at'] = datetime.fromisoformat(acc['created_at'])
    return accounts

@api_router.post('/accounting/accounts', response_model=Account)
async def create_account(account_data: AccountCreate, current_user: dict = Depends(get_current_user)):
    # Check permission - Owner or Manager or Finance
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    acc_dict = account_data.model_dump()
    acc_dict['id'] = generate_id()
    acc_dict['balance'] = 0
    acc_dict['created_at'] = utc_now()
    
    doc = acc_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.accounts.insert_one(doc)
    return Account(**acc_dict)

@api_router.get('/accounting/journal-entries')
async def get_journal_entries(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if business_id:
        query['business_id'] = business_id
    if start_date and end_date:
        query['transaction_date'] = {'$gte': start_date, '$lte': end_date}
    
    entries = await db.journal_entries.find(query, {'_id': 0}).sort('transaction_date', -1).to_list(1000)
    for entry in entries:
        if isinstance(entry.get('transaction_date'), str):
            entry['transaction_date'] = datetime.fromisoformat(entry['transaction_date'])
        if isinstance(entry.get('created_at'), str):
            entry['created_at'] = datetime.fromisoformat(entry['created_at'])
    return entries

@api_router.post('/accounting/journal-entries', response_model=JournalEntry)
async def create_journal_entry(entry_data: JournalEntryCreate, current_user: dict = Depends(get_current_user)):
    entry_dict = entry_data.model_dump()
    entry_dict['id'] = generate_id()
    entry_dict['entry_number'] = generate_code('JE', 12)
    entry_dict['created_by'] = current_user['sub']
    entry_dict['created_at'] = utc_now()
    
    # Calculate totals
    total_debit = sum(item['amount'] for item in entry_dict['line_items'] if item['entry_type'] == 'debit')
    total_credit = sum(item['amount'] for item in entry_dict['line_items'] if item['entry_type'] == 'credit')
    
    entry_dict['total_debit'] = total_debit
    entry_dict['total_credit'] = total_credit
    entry_dict['is_balanced'] = abs(total_debit - total_credit) < 0.01
    
    if not entry_dict['is_balanced']:
        raise HTTPException(status_code=400, detail='Journal entry tidak balance')
    
    doc = entry_dict.copy()
    doc['transaction_date'] = doc['transaction_date'].isoformat() if isinstance(doc['transaction_date'], datetime) else doc['transaction_date']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.journal_entries.insert_one(doc)
    
    # Update account balances
    for item in entry_dict['line_items']:
        if item['entry_type'] == 'debit':
            await db.accounts.update_one(
                {'id': item['account_id']},
                {'$inc': {'balance': item['amount']}}
            )
        else:
            await db.accounts.update_one(
                {'id': item['account_id']},
                {'$inc': {'balance': -item['amount']}}
            )
    
    return JournalEntry(**entry_dict)

# ============= LOYALTY PROGRAM ROUTES =============
@api_router.get('/loyalty-programs')
async def get_loyalty_programs(current_user: dict = Depends(get_current_user)):
    programs = await db.loyalty_programs.find({}, {'_id': 0}).sort('created_at', -1).to_list(1000)
    for prog in programs:
        for field in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if prog.get(field) and isinstance(prog[field], str):
                prog[field] = datetime.fromisoformat(prog[field])
    return programs

@api_router.post('/loyalty-programs', response_model=LoyaltyProgram)
async def create_loyalty_program(program_data: LoyaltyProgramCreate, current_user: dict = Depends(get_current_user)):
    prog_dict = program_data.model_dump()
    prog_dict['id'] = generate_id()
    prog_dict['actual_participants'] = 0
    prog_dict['actual_cost'] = 0
    prog_dict['created_by'] = current_user['sub']
    prog_dict['created_at'] = utc_now()
    prog_dict['updated_at'] = utc_now()
    
    doc = prog_dict.copy()
    for field in ['start_date', 'end_date', 'created_at', 'updated_at']:
        if doc.get(field) and isinstance(doc[field], datetime):
            doc[field] = doc[field].isoformat()
    
    await db.loyalty_programs.insert_one(doc)
    return LoyaltyProgram(**prog_dict)

@api_router.put('/loyalty-programs/{program_id}')
async def update_loyalty_program(
    program_id: str,
    program_data: dict,
    current_user: dict = Depends(get_current_user)
):
    # Allow updating all fields
    update_data = {'updated_at': utc_now().isoformat()}
    
    # Update allowed fields
    allowed_fields = ['name', 'description', 'status', 'actual_participants', 'actual_cost', 
                     'target_participants', 'budget', 'reward_type', 'start_date', 'end_date']
    
    for field in allowed_fields:
        if field in program_data and program_data[field] is not None:
            update_data[field] = program_data[field]
    
    result = await db.loyalty_programs.update_one({'id': program_id}, {'$set': update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Program tidak ditemukan')
    
    await log_activity(
        user_id=current_user['sub'],
        action='loyalty_program_updated',
        description=f"Updated loyalty program {program_id}",
        related_type='loyalty_program',
        related_id=program_id
    )
    
    return {'message': 'Program berhasil diupdate'}

@api_router.delete('/loyalty-programs/{program_id}')
async def delete_loyalty_program(program_id: str, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    result = await db.loyalty_programs.delete_one({'id': program_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Program tidak ditemukan')
    
    return {'message': 'Program berhasil dihapus'}

# ============= CSR PROGRAM ROUTES =============
@api_router.get('/csr-programs')
async def get_csr_programs(current_user: dict = Depends(get_current_user)):
    programs = await db.csr_programs.find({}, {'_id': 0}).sort('created_at', -1).to_list(1000)
    for prog in programs:
        for field in ['start_date', 'end_date', 'created_at', 'updated_at']:
            if prog.get(field) and isinstance(prog[field], str):
                prog[field] = datetime.fromisoformat(prog[field])
    return programs

@api_router.post('/csr-programs', response_model=CSRProgram)
async def create_csr_program(program_data: CSRProgramCreate, current_user: dict = Depends(get_current_user)):
    prog_dict = program_data.model_dump()
    prog_dict['id'] = generate_id()
    prog_dict['actual_beneficiaries'] = 0
    prog_dict['actual_cost'] = 0
    prog_dict['impact_report'] = None
    prog_dict['created_by'] = current_user['sub']
    prog_dict['created_at'] = utc_now()
    prog_dict['updated_at'] = utc_now()
    
    doc = prog_dict.copy()
    for field in ['start_date', 'end_date', 'created_at', 'updated_at']:
        if doc.get(field) and isinstance(doc[field], datetime):
            doc[field] = doc[field].isoformat()
    
    await db.csr_programs.insert_one(doc)
    return CSRProgram(**prog_dict)

@api_router.put('/csr-programs/{program_id}')
async def update_csr_program(
    program_id: str,
    status: Optional[str] = None,
    actual_beneficiaries: Optional[int] = None,
    actual_cost: Optional[float] = None,
    impact_report: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {'updated_at': utc_now().isoformat()}
    if status:
        update_data['status'] = status
    if actual_beneficiaries is not None:
        update_data['actual_beneficiaries'] = actual_beneficiaries
    if actual_cost is not None:
        update_data['actual_cost'] = actual_cost
    if impact_report:
        update_data['impact_report'] = impact_report
    
    result = await db.csr_programs.update_one({'id': program_id}, {'$set': update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Program tidak ditemukan')
    
    return {'message': 'Program berhasil diupdate'}

@api_router.delete('/csr-programs/{program_id}')
async def delete_csr_program(program_id: str, current_user: dict = Depends(get_current_user)):
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    result = await db.csr_programs.delete_one({'id': program_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Program tidak ditemukan')
    
    return {'message': 'Program berhasil dihapus'}

# ============= INIT DATA =============
@api_router.post('/init-data')
async def init_data():
    # Check if data already exists
    user_count = await db.users.count_documents({})
    if user_count > 0:
        return {'message': 'Data sudah ada'}
    
    # Create roles
    roles = [
        {'id': 1, 'name': 'Owner', 'description': 'Pemilik sistem dengan akses penuh', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 2, 'name': 'Manager', 'description': 'Manajer operasional', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 3, 'name': 'Finance', 'description': 'Staff keuangan', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 4, 'name': 'Customer Service', 'description': 'Customer Service', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 5, 'name': 'Kasir', 'description': 'Kasir', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 6, 'name': 'Loket', 'description': 'Petugas Loket', 'permissions': {}, 'created_at': utc_now().isoformat()},
        {'id': 7, 'name': 'Teknisi', 'description': 'Teknisi Lapangan', 'permissions': {}, 'created_at': utc_now().isoformat()},
    ]
    await db.roles.insert_many(roles)
    
    # Create default owner user
    owner = {
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
    }
    await db.users.insert_one(owner)
    
    # Create demo business
    business = {
        'id': generate_id(),
        'name': 'Loket PPOB Pusat',
        'category': 'PPOB',
        'description': 'Layanan pembayaran PPOB (listrik, air, pulsa, dll)',
        'address': 'Jl. Contoh No. 123',
        'phone': '0211234567',
        'email': 'ppob@gelis.com',
        'settings': {'commission_rate': 0.05},
        'is_active': True,
        'created_by': owner['id'],
        'created_at': utc_now().isoformat(),
        'updated_at': utc_now().isoformat()
    }
    await db.businesses.insert_one(business)
    
    return {'message': 'Data awal berhasil dibuat', 'owner_credentials': {'username': 'owner', 'password': 'owner123'}}


# ============= SETTINGS ENDPOINTS =============
@api_router.get('/settings/all')
async def get_all_settings(current_user: User = Depends(get_current_user)):
    """Get all settings"""
    settings_docs = await db.settings.find({}, {'_id': 0}).to_list(length=None)
    
    # Convert to dict
    settings_dict = {}
    for doc in settings_docs:
        settings_dict[doc['setting_key']] = doc.get('setting_value')
    
    # Add default values if not exist
    defaults = {
        'company_name': 'PT. GELIS Indonesia',
        'company_address': 'Jl. Contoh No. 123, Jakarta Selatan',
        'company_phone': '021-12345678',
        'company_email': 'info@gelis.com',
        'company_website': 'https://gelis.com',
        'timezone': 'Asia/Jakarta',
        'language': 'id',
        'currency': 'IDR',
        'date_format': 'DD/MM/YYYY',
        'time_format': '24h',
        'email_notifications': True,
        'whatsapp_notifications': False,
        'push_notifications': True,
        'is_mock_data': True,
        'data_retention_days': 365,
        'auto_backup': False,
        'backup_frequency': 'daily',
        'session_timeout': 43200,
        'password_expiry_days': 90,
        'max_login_attempts': 5,
        'two_factor_auth': False,
    }
    
    for key, default_val in defaults.items():
        if key not in settings_dict:
            settings_dict[key] = default_val
    
    return settings_dict

@api_router.put('/settings/bulk')
async def update_bulk_settings(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update multiple settings at once"""
    if current_user.role_id not in [1, 2]:  # Owner or Manager only
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Hanya Owner atau Manager yang dapat mengubah pengaturan'
        )
    
    settings = data.get('settings', {})
    section = data.get('section', 'all')
    
    # Update each setting
    for key, value in settings.items():
        await db.settings.update_one(
            {'setting_key': key},
            {
                '$set': {
                    'setting_value': value,
                    'updated_by': current_user.id,
                    'updated_at': utc_now().isoformat()
                }
            },
            upsert=True
        )
    
    # Log activity
    await log_activity(
        user_id=current_user.id,
        action='settings.update',
        description=f'Updated {section} settings',
        metadata={'section': section}
    )
    
    return {'message': 'Pengaturan berhasil disimpan'}

@api_router.post('/settings/test-email')
async def test_email(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    """Test email configuration"""
    # This is a mock endpoint - in production, integrate with actual email service
    return {'message': 'Email test berhasil dikirim ke ' + data.get('to')}

# ============= DATA MANAGEMENT ENDPOINTS =============
@api_router.post('/data/clear-mock')
async def clear_mock_data(current_user: User = Depends(get_current_user)):
    """Clear all mock data and keep only owner user"""
    if current_user.role_id != 1:  # Owner only
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Hanya Owner yang dapat menghapus data mockup'
        )
    
    # Delete all mock users (is_mock = True)
    deleted_users = await db.users.delete_many({'is_mock': True})
    
    # Delete all mock businesses
    deleted_businesses = await db.businesses.delete_many({'is_mock': True})
    
    # Delete all mock orders
    deleted_orders = await db.orders.delete_many({'is_mock': True})
    
    # Delete all mock transactions
    deleted_transactions = await db.accounting.delete_many({'is_mock': True})
    
    # Delete all mock reports
    deleted_loket_reports = await db.loket_reports.delete_many({'is_mock': True})
    deleted_kasir_reports = await db.kasir_reports.delete_many({'is_mock': True})
    
    # Delete all mock loyalty programs
    deleted_loyalty = await db.loyalty_programs.delete_many({'is_mock': True})
    
    # Delete all mock CSR programs
    deleted_csr = await db.csr_programs.delete_many({'is_mock': True})
    
    # Keep activity logs for audit trail (don't delete)
    
    # Update is_mock_data setting
    await db.settings.update_one(
        {'setting_key': 'is_mock_data'},
        {'$set': {'setting_value': False, 'updated_at': utc_now().isoformat()}},
        upsert=True
    )
    
    # Log activity
    await log_activity(
        user_id=current_user.id,
        action='data.clear_mock',
        description='Cleared all mock data from system',
        metadata={
            'deleted_users': deleted_users.deleted_count,
            'deleted_businesses': deleted_businesses.deleted_count,
            'deleted_orders': deleted_orders.deleted_count,
            'deleted_transactions': deleted_transactions.deleted_count,
            'deleted_reports': deleted_loket_reports.deleted_count + deleted_kasir_reports.deleted_count,
            'deleted_loyalty_programs': deleted_loyalty.deleted_count,
            'deleted_csr_programs': deleted_csr.deleted_count
        }
    )
    
    return {
        'message': 'Data mockup berhasil dihapus! Aplikasi sekarang siap untuk data real.',
        'summary': {
            'deleted_users': deleted_users.deleted_count,
            'deleted_businesses': deleted_businesses.deleted_count,
            'deleted_orders': deleted_orders.deleted_count,
            'deleted_transactions': deleted_transactions.deleted_count,
            'deleted_loket_reports': deleted_loket_reports.deleted_count,
            'deleted_kasir_reports': deleted_kasir_reports.deleted_count,
            'deleted_loyalty_programs': deleted_loyalty.deleted_count,
            'deleted_csr_programs': deleted_csr.deleted_count,
            'total_deleted': (
                deleted_users.deleted_count +
                deleted_businesses.deleted_count +
                deleted_orders.deleted_count +
                deleted_transactions.deleted_count +
                deleted_loket_reports.deleted_count +
                deleted_kasir_reports.deleted_count +
                deleted_loyalty.deleted_count +
                deleted_csr.deleted_count
            )
        }
    }

@api_router.post('/data/backup')
async def backup_database(current_user: User = Depends(get_current_user)):
    """Create database backup"""
    if current_user.role_id not in [1, 2]:  # Owner or Manager only
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Hanya Owner atau Manager yang dapat backup database'
        )
    
    # Export all collections
    backup_data = {
        'backup_date': utc_now().isoformat(),
        'backup_by': current_user.full_name,
        'collections': {}
    }
    
    # Export users (without passwords)
    users = []
    async for user in db.users.find({}, {'_id': 0, 'password': 0}):
        users.append(user)
    backup_data['collections']['users'] = users
    
    # Export businesses
    businesses = await db.businesses.find({}, {'_id': 0}).to_list(length=None)
    backup_data['collections']['businesses'] = businesses
    
    # Export orders
    orders = await db.orders.find({}, {'_id': 0}).to_list(length=None)
    backup_data['collections']['orders'] = orders
    
    # Export transactions
    transactions = await db.accounting.find({}, {'_id': 0}).to_list(length=None)
    backup_data['collections']['transactions'] = transactions
    
    # Log activity
    await log_activity(
        user_id=current_user.id,
        action='data.backup',
        description='Created database backup',
        metadata={'collections_count': len(backup_data['collections'])}
    )
    
    return backup_data

# Health check endpoint for Kubernetes/deployment platforms (BEFORE router)
@app.get('/health')
async def health_check():
    """Health check endpoint for load balancers and orchestration platforms"""
    try:
        # Test database connection
        await db.command('ping')
        return {
            'status': 'healthy',
            'service': 'gelis-backend',
            'database': 'connected',
            'timestamp': utc_now().isoformat()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'service': 'gelis-backend',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': utc_now().isoformat()
        }

# Root endpoint
@app.get('/')
async def root():
    """Root endpoint - API info"""
    return {
        'service': 'GELIS API',
        'version': '1.0.0',
        'status': 'running',
        'docs': '/docs',
        'health': '/health'
    }

# ============= FASE 1: CRITICAL ENHANCEMENTS ENDPOINTS =============

# Import report generator
from utils.report_generator import report_generator

# 1. PLN TECHNICAL WORK PROGRESS ENDPOINTS

@api_router.post('/technical-progress', response_model=dict)
async def create_technical_progress(
    progress_data: TechnicalProgressCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create technical progress tracking for an order"""
    # Verify order exists
    order = await db.orders.find_one({'id': progress_data.order_id}, {'_id': 0})
    if not order:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    # Check if progress already exists
    existing = await db.technical_progress.find_one({'order_id': progress_data.order_id}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Progress untuk order ini sudah ada')
    
    # Create progress
    progress_dict = progress_data.model_dump()
    progress_dict['id'] = generate_id()
    progress_dict['created_by'] = current_user['sub']
    progress_dict['created_at'] = utc_now()
    progress_dict['updated_at'] = utc_now()
    
    # Serialize datetimes in steps
    for step in progress_dict['steps']:
        if step.get('started_at'):
            step['started_at'] = step['started_at'].isoformat() if isinstance(step['started_at'], datetime) else step['started_at']
        if step.get('completed_at'):
            step['completed_at'] = step['completed_at'].isoformat() if isinstance(step['completed_at'], datetime) else step['completed_at']
    
    doc = progress_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.technical_progress.insert_one(doc)
    
    await log_activity(
        current_user['sub'],
        'CREATE_TECHNICAL_PROGRESS',
        f"Created technical progress for order {progress_data.order_id}",
        related_type='technical_progress',
        related_id=progress_dict['id']
    )
    
    return {'message': 'Technical progress created successfully', 'id': progress_dict['id']}


@api_router.get('/technical-progress/{order_id}', response_model=dict)
async def get_technical_progress(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get technical progress for an order"""
    progress = await db.technical_progress.find_one({'order_id': order_id}, {'_id': 0})
    if not progress:
        raise HTTPException(status_code=404, detail='Progress tidak ditemukan')
    
    return progress


@api_router.put('/technical-progress/{order_id}/step', response_model=dict)
async def update_technical_step(
    order_id: str,
    step_update: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update status of a specific technical step"""
    # Get current progress
    progress = await db.technical_progress.find_one({'order_id': order_id}, {'_id': 0})
    if not progress:
        raise HTTPException(status_code=404, detail='Progress tidak ditemukan')
    
    # Find and update the step
    step_name = step_update.get('step_name')
    new_status = step_update.get('status')
    notes = step_update.get('notes')
    photos = step_update.get('photos', [])
    
    steps = progress.get('steps', [])
    step_found = False
    overall_progress = 0.0
    
    for step in steps:
        if step['step_name'] == step_name:
            step_found = True
            step['status'] = new_status
            if notes:
                step['notes'] = notes
            if photos:
                step['photos'] = photos
            
            if new_status == 'in_progress' and not step.get('started_at'):
                step['started_at'] = utc_now().isoformat()
            elif new_status == 'completed':
                step['completed_at'] = utc_now().isoformat()
        
        # Calculate overall progress
        if step['status'] == 'completed':
            overall_progress += step['step_weight']
    
    if not step_found:
        raise HTTPException(status_code=404, detail=f'Step {step_name} tidak ditemukan')
    
    # Update progress in database
    await db.technical_progress.update_one(
        {'order_id': order_id},
        {
            '$set': {
                'steps': steps,
                'overall_progress': overall_progress,
                'updated_at': utc_now().isoformat()
            }
        }
    )
    
    # Update order status based on progress
    if overall_progress >= 100:
        await db.orders.update_one(
            {'id': order_id},
            {'$set': {'status': 'completed', 'completion_date': utc_now().isoformat()}}
        )
    elif overall_progress > 0:
        await db.orders.update_one(
            {'id': order_id},
            {'$set': {'status': 'processing'}}
        )
    
    await log_activity(
        current_user['sub'],
        'UPDATE_TECHNICAL_STEP',
        f"Updated step {step_name} to {new_status} for order {order_id}",
        related_type='technical_progress',
        related_id=progress['id']
    )
    
    return {
        'message': 'Step updated successfully',
        'overall_progress': overall_progress,
        'order_status': 'completed' if overall_progress >= 100 else 'processing'
    }


# 2. AUTO-SYNC TO ACCOUNTING HELPER FUNCTION

async def auto_sync_to_accounting(
    business_id: str,
    amount: float,
    transaction_type: str,  # 'income' or 'expense'
    category: str,
    description: str,
    reference_id: str,
    reference_type: str,
    user_id: str
):
    """Helper function to automatically create accounting transaction"""
    try:
        transaction_code = f"TRX-{datetime.now().strftime('%Y%m%d')}-{generate_id()[:8]}"
        
        transaction_dict = {
            'id': generate_id(),
            'transaction_code': transaction_code,
            'business_id': business_id,
            'transaction_type': transaction_type,
            'category': category,
            'description': description,
            'amount': amount,
            'payment_method': 'cash',
            'reference_number': f"{reference_type}-{reference_id}",
            'created_at': utc_now().isoformat(),
            'created_by': user_id
        }
        
        await db.transactions.insert_one(transaction_dict)
        
        await log_activity(
            user_id,
            'AUTO_SYNC_ACCOUNTING',
            f"Auto-synced {transaction_type} Rp {amount:,.0f} from {reference_type}",
            related_type='transaction',
            related_id=transaction_dict['id']
        )
        
        return transaction_dict['id']
    except Exception as e:
        print(f"Error auto-syncing to accounting: {str(e)}")
        return None


# ============= SISTEM PPOB ENDPOINTS =============

# Helper function untuk double-entry accounting PPOB
async def create_ppob_journal_entry(
    tanggal: datetime,
    description: str,
    debit_account: str,
    kredit_account: str,
    amount: float,
    reference_type: str,
    reference_id: str,
    user_id: str
):
    """Create double-entry journal for PPOB"""
    try:
        journal_entry = {
            'id': generate_id(),
            'tanggal': tanggal.isoformat() if isinstance(tanggal, datetime) else tanggal,
            'description': description,
            'debit_account': debit_account,
            'debit_amount': amount,
            'kredit_account': kredit_account,
            'kredit_amount': amount,
            'reference_type': reference_type,
            'reference_id': reference_id,
            'created_at': utc_now().isoformat(),
            'created_by': user_id
        }
        
        await db.ppob_journal_entries.insert_one(journal_entry)
        return journal_entry['id']
    except Exception as e:
        print(f"Error creating PPOB journal: {str(e)}")
        return None


# MENU 1: LAPORAN LOKET PPOB ENDPOINTS

@api_router.post('/ppob/loket-shift', response_model=dict)
async def create_ppob_loket_shift(
    report_data: PPOBLoketShiftReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create laporan shift loket PPOB dengan auto-accounting:
    - Debit: Piutang Setoran Loket
    - Kredit: Pendapatan PPOB
    """
    # Calculate totals
    total_penjualan = 0.0
    total_sisa_setoran = 0.0
    
    for channel in report_data.channels:
        # Auto-calculate per channel
        channel.sisa_setoran = channel.total_penjualan
        channel.saldo_akhir = channel.saldo_awal + channel.saldo_inject - channel.total_penjualan
        
        total_penjualan += channel.total_penjualan
        total_sisa_setoran += channel.sisa_setoran
    
    # Create report
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['total_penjualan'] = total_penjualan
    report_dict['total_sisa_setoran'] = total_sisa_setoran
    report_dict['status_setoran'] = 'Belum Disetor'
    report_dict['created_by'] = current_user['id']
    report_dict['created_at'] = utc_now()
    
    # Serialize
    doc = report_dict.copy()
    doc['tanggal'] = doc['tanggal'].isoformat() if isinstance(doc['tanggal'], datetime) else doc['tanggal']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.ppob_loket_shifts.insert_one(doc)
    
    # AUTO-ACCOUNTING: Double Entry
    # Debit: Piutang Setoran Loket
    # Kredit: Pendapatan PPOB
    await create_ppob_journal_entry(
        tanggal=report_data.tanggal,
        description=f"Penjualan PPOB Shift {report_data.shift} - {report_data.nama_petugas}",
        debit_account="Piutang Setoran Loket",
        kredit_account="Pendapatan PPOB",
        amount=total_penjualan,
        reference_type="loket_shift",
        reference_id=report_dict['id'],
        user_id=current_user['id']
    )
    
    # Create notification untuk kasir
    kasir_users = await db.users.find({'role_id': 5}, {'_id': 0}).to_list(length=100)  # Role 5 = Kasir
    for kasir in kasir_users:
        notification = {
            'id': generate_id(),
            'user_id': kasir['id'],
            'type': 'ppob_setoran',
            'title': 'Setoran PPOB Baru',
            'message': f"Setoran shift {report_data.shift} dari {report_data.nama_petugas} sebesar Rp {total_sisa_setoran:,.0f} menunggu penerimaan",
            'is_read': False,
            'related_type': 'ppob_loket_shift',
            'related_id': report_dict['id'],
            'created_at': utc_now().isoformat()
        }
        await db.notifications.insert_one(notification)
    
    await log_activity(
        current_user['id'],
        'CREATE_PPOB_LOKET_SHIFT',
        f"Created PPOB loket shift report: Rp {total_penjualan:,.0f}",
        related_type='ppob_loket_shift',
        related_id=report_dict['id']
    )
    
    return {
        'message': 'Laporan shift berhasil disimpan & auto-sync ke accounting!',
        'id': report_dict['id'],
        'total_penjualan': total_penjualan,
        'status_setoran': 'Belum Disetor'
    }


@api_router.get('/ppob/loket-shift', response_model=dict)
async def get_ppob_loket_shifts(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shift: Optional[int] = None,
    status_setoran: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get PPOB loket shift reports with filters"""
    query = {}
    
    if business_id:
        query['business_id'] = business_id
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    if shift:
        query['shift'] = shift
    
    if status_setoran:
        query['status_setoran'] = status_setoran
    
    reports = await db.ppob_loket_shifts.find(query, {'_id': 0}).sort('tanggal', -1).to_list(length=100)
    
    # Count by status
    belum_disetor = await db.ppob_loket_shifts.count_documents({**query, 'status_setoran': 'Belum Disetor'})
    
    return {
        'reports': reports,
        'count': len(reports),
        'belum_disetor': belum_disetor
    }


# MENU 2: LAPORAN KASIR PPOB ENDPOINTS

@api_router.post('/ppob/kasir-report', response_model=dict)
async def create_ppob_kasir_report(
    report_data: PPOBKasirReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create laporan kasir PPOB dengan auto-accounting:
    1. Setoran Loket: Debit Kas, Kredit Piutang + Update status Lunas
    2. Topup Saldo: Debit Modal PPOB, Kredit Kas
    3. Kas Kecil: Auto-calculate
    4. Admin: Debit Kas, Kredit Pendapatan Admin
    """
    # Calculate totals
    total_setoran_loket = sum(s.amount for s in report_data.setoran_loket)
    total_topup = sum(t.amount for t in report_data.topup_saldo)
    saldo_kas_kecil = report_data.penerimaan_kas_kecil - report_data.pengurangan_kas_kecil
    
    # Create report
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['total_setoran_loket'] = total_setoran_loket
    report_dict['total_topup'] = total_topup
    report_dict['saldo_kas_kecil'] = saldo_kas_kecil
    report_dict['created_by'] = current_user['id']
    report_dict['created_at'] = utc_now()
    
    # Serialize
    doc = report_dict.copy()
    doc['tanggal'] = doc['tanggal'].isoformat() if isinstance(doc['tanggal'], datetime) else doc['tanggal']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.ppob_kasir_reports.insert_one(doc)
    
    # AUTO-ACCOUNTING ENTRIES
    
    # 1. Setoran Loket: Close piutang
    if total_setoran_loket > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description="Penerimaan Setoran Loket PPOB",
            debit_account="Kas",
            kredit_account="Piutang Setoran Loket",
            amount=total_setoran_loket,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
        
        # Update status setoran loket → Lunas
        for setoran in report_data.setoran_loket:
            await db.ppob_loket_shifts.update_one(
                {'id': setoran.loket_report_id},
                {'$set': {'status_setoran': 'Lunas'}}
            )
    
    # 2. Setoran Loket Luar
    if report_data.setoran_loket_luar > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description="Setoran Loket Luar PPOB",
            debit_account="Kas",
            kredit_account="Pendapatan PPOB Loket Luar",
            amount=report_data.setoran_loket_luar,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
    
    # 3. Penerimaan Admin
    if report_data.penerimaan_admin > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description="Penerimaan Admin PPOB",
            debit_account="Kas",
            kredit_account="Pendapatan Admin",
            amount=report_data.penerimaan_admin,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
    
    # 4. Topup Saldo Loket
    if total_topup > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description=f"Topup Saldo PPOB - {len(report_data.topup_saldo)} channel(s)",
            debit_account="Modal Saldo PPOB",
            kredit_account="Kas",
            amount=total_topup,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
    
    # 5. Kas Kecil - Pengeluaran
    if report_data.pengurangan_kas_kecil > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description="Pengeluaran Kas Kecil",
            debit_account="Biaya Operasional",
            kredit_account="Kas Kecil",
            amount=report_data.pengurangan_kas_kecil,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
    
    # 6. Kas Kecil - Penerimaan
    if report_data.penerimaan_kas_kecil > 0:
        await create_ppob_journal_entry(
            tanggal=report_data.tanggal,
            description="Penerimaan Kas Kecil",
            debit_account="Kas Kecil",
            kredit_account="Kas",
            amount=report_data.penerimaan_kas_kecil,
            reference_type="kasir_report",
            reference_id=report_dict['id'],
            user_id=current_user['id']
        )
    
    await log_activity(
        current_user['id'],
        'CREATE_PPOB_KASIR_REPORT',
        f"Created PPOB kasir report: Setoran Rp {total_setoran_loket:,.0f}",
        related_type='ppob_kasir_report',
        related_id=report_dict['id']
    )
    
    return {
        'message': 'Laporan kasir berhasil disimpan & auto-sync ke accounting!',
        'id': report_dict['id'],
        'total_setoran': total_setoran_loket,
        'total_topup': total_topup,
        'saldo_kas_kecil': saldo_kas_kecil
    }


@api_router.get('/ppob/kasir-report', response_model=dict)
async def get_ppob_kasir_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get PPOB kasir reports with filters"""
    query = {}
    
    if business_id:
        query['business_id'] = business_id
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    reports = await db.ppob_kasir_reports.find(query, {'_id': 0}).sort('tanggal', -1).to_list(length=100)
    
    return {
        'reports': reports,
        'count': len(reports)
    }


# MENU 3: AKUNTING PPOB ENDPOINTS

@api_router.get('/ppob/accounting/journal', response_model=dict)
async def get_ppob_journal_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get PPOB journal entries (buku jurnal)"""
    query = {}
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    entries = await db.ppob_journal_entries.find(query, {'_id': 0}).sort('tanggal', -1).to_list(length=1000)
    
    return {
        'entries': entries,
        'count': len(entries)
    }


@api_router.get('/ppob/accounting/ledger', response_model=dict)
async def get_ppob_ledger(
    account_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get PPOB ledger per account"""
    query = {}
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    all_entries = await db.ppob_journal_entries.find(query, {'_id': 0}).sort('tanggal', 1).to_list(length=10000)
    
    # Group by account
    ledger = {}
    
    for entry in all_entries:
        # Debit side
        debit_acc = entry['debit_account']
        if debit_acc not in ledger:
            ledger[debit_acc] = {'account_name': debit_acc, 'transactions': [], 'balance': 0.0}
        ledger[debit_acc]['transactions'].append({
            'tanggal': entry['tanggal'],
            'description': entry['description'],
            'debit': entry['debit_amount'],
            'kredit': 0,
            'reference': f"{entry['reference_type']}-{entry['reference_id']}"
        })
        ledger[debit_acc]['balance'] += entry['debit_amount']
        
        # Kredit side
        kredit_acc = entry['kredit_account']
        if kredit_acc not in ledger:
            ledger[kredit_acc] = {'account_name': kredit_acc, 'transactions': [], 'balance': 0.0}
        ledger[kredit_acc]['transactions'].append({
            'tanggal': entry['tanggal'],
            'description': entry['description'],
            'debit': 0,
            'kredit': entry['kredit_amount'],
            'reference': f"{entry['reference_type']}-{entry['reference_id']}"
        })
        ledger[kredit_acc]['balance'] -= entry['kredit_amount']
    
    # Filter by account if specified
    if account_name:
        ledger = {k: v for k, v in ledger.items() if k == account_name}
    
    return {
        'ledger': list(ledger.values()),
        'accounts': list(ledger.keys())
    }


@api_router.get('/ppob/accounting/balances', response_model=dict)
async def get_ppob_account_balances(
    current_user: dict = Depends(get_current_user)
):
    """Get all PPOB account balances (saldo realtime)"""
    # Get all journal entries
    all_entries = await db.ppob_journal_entries.find({}, {'_id': 0}).to_list(length=10000)
    
    balances = {}
    
    for entry in all_entries:
        # Debit increases balance
        debit_acc = entry['debit_account']
        if debit_acc not in balances:
            balances[debit_acc] = 0.0
        balances[debit_acc] += entry['debit_amount']
        
        # Kredit decreases balance
        kredit_acc = entry['kredit_account']
        if kredit_acc not in balances:
            balances[kredit_acc] = 0.0
        balances[kredit_acc] -= entry['kredit_amount']
    
    # Format output
    account_balances = [
        {
            'account_name': acc,
            'balance': bal,
            'last_updated': utc_now().isoformat()
        }
        for acc, bal in balances.items()
    ]
    
    return {
        'balances': account_balances,
        'total_accounts': len(account_balances)
    }


@api_router.get('/ppob/accounting/profit-loss', response_model=dict)
async def get_ppob_profit_loss(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get PPOB profit & loss statement"""
    query = {}
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    entries = await db.ppob_journal_entries.find(query, {'_id': 0}).to_list(length=10000)
    
    # Calculate revenue and expenses
    revenue = 0.0
    expenses = 0.0
    
    for entry in entries:
        # Revenue accounts (Kredit)
        if 'Pendapatan' in entry['kredit_account']:
            revenue += entry['kredit_amount']
        
        # Expense accounts (Debit)
        if 'Biaya' in entry['debit_account']:
            expenses += entry['debit_amount']
    
    net_profit = revenue - expenses
    profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
    
    return {
        'period': {
            'start': start_date,
            'end': end_date
        },
        'revenue': revenue,
        'expenses': expenses,
        'net_profit': net_profit,
        'profit_margin': profit_margin
    }


# 3. EXECUTIVE SUMMARY REPORT ENDPOINT

@api_router.get('/reports/executive-summary', response_model=dict)
async def get_executive_summary(
    start_date: str,
    end_date: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate executive summary report for all businesses"""
    # Permission check: Only Owner, Manager, Finance can access
    if current_user['role_id'] not in [1, 2, 3]:  # Owner, Manager, Finance
        raise HTTPException(status_code=403, detail='Akses ditolak')
    
    # Get all businesses
    businesses = await db.businesses.find({'is_active': True}, {'_id': 0}).to_list(length=100)
    
    business_units = []
    total_revenue = 0.0
    total_expenses = 0.0
    
    for business in businesses:
        business_id = business['id']
        
        # Get transactions for this business in date range
        transactions = await db.transactions.find({
            'business_id': business_id,
            'created_at': {
                '$gte': start_date,
                '$lte': end_date
            }
        }, {'_id': 0}).to_list(length=10000)
        
        revenue = sum(t['amount'] for t in transactions if t['transaction_type'] == 'income')
        expenses = sum(t['amount'] for t in transactions if t['transaction_type'] == 'expense')
        net_profit = revenue - expenses
        profit_margin = (net_profit / revenue * 100) if revenue > 0 else 0
        
        # Get orders for this business
        orders = await db.orders.find({
            'business_id': business_id,
            'created_at': {
                '$gte': start_date,
                '$lte': end_date
            }
        }, {'_id': 0}).to_list(length=10000)
        
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o['status'] == 'completed'])
        pending_orders = len([o for o in orders if o['status'] == 'pending'])
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        average_order_value = revenue / total_orders if total_orders > 0 else 0
        
        business_unit = {
            'business_id': business_id,
            'business_name': business['name'],
            'business_category': business['category'],
            'total_revenue': revenue,
            'total_expenses': expenses,
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'total_orders': total_orders,
            'completed_orders': completed_orders,
            'pending_orders': pending_orders,
            'completion_rate': completion_rate,
            'average_order_value': average_order_value,
            'growth_rate': 0  # TODO: Calculate from previous period
        }
        
        business_units.append(business_unit)
        total_revenue += revenue
        total_expenses += expenses
    
    net_profit = total_revenue - total_expenses
    overall_profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
    
    # Find top performers
    best_performing = max(business_units, key=lambda x: x['profit_margin']) if business_units else None
    highest_revenue = max(business_units, key=lambda x: x['total_revenue']) if business_units else None
    highest_margin = max(business_units, key=lambda x: x['profit_margin']) if business_units else None
    
    # Generate alerts
    alerts = []
    if net_profit < 0:
        alerts.append("⚠️ Total laba bersih negatif - perlu review pengeluaran")
    
    for bu in business_units:
        if bu['profit_margin'] < 10:
            alerts.append(f"⚠️ {bu['business_name']}: Margin keuntungan rendah ({bu['profit_margin']:.1f}%)")
        if bu['pending_orders'] > bu['completed_orders']:
            alerts.append(f"⚠️ {bu['business_name']}: Pending orders ({bu['pending_orders']}) lebih banyak dari completed ({bu['completed_orders']})")
    
    # Generate insights
    insights = []
    if business_units:
        avg_margin = sum(bu['profit_margin'] for bu in business_units) / len(business_units)
        insights.append(f"💡 Rata-rata margin keuntungan: {avg_margin:.2f}%")
        
        top_3_revenue = sorted(business_units, key=lambda x: x['total_revenue'], reverse=True)[:3]
        insights.append(f"💡 Top 3 pendapatan: {', '.join([bu['business_name'] for bu in top_3_revenue])}")
    
    # Generate recommendations
    recommendations = []
    low_performers = [bu for bu in business_units if bu['profit_margin'] < 15]
    if low_performers:
        recommendations.append(f"💡 Fokus perbaikan: {', '.join([bu['business_name'] for bu in low_performers])}")
    
    if total_revenue > 0 and total_expenses / total_revenue > 0.7:
        recommendations.append("💡 Rasio pengeluaran tinggi (>70%), review efisiensi operasional")
    
    summary = {
        'period_start': start_date,
        'period_end': end_date,
        'report_generated_at': utc_now().isoformat(),
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'overall_profit_margin': overall_profit_margin,
        'business_units': business_units,
        'best_performing_business': best_performing['business_name'] if best_performing else None,
        'highest_revenue_business': highest_revenue['business_name'] if highest_revenue else None,
        'highest_margin_business': highest_margin['business_name'] if highest_margin else None,
        'alerts': alerts,
        'insights': insights,
        'recommendations': recommendations
    }
    
    return summary


# 4. EXPORT ENDPOINTS (PDF & EXCEL)

@api_router.post('/reports/export', response_model=dict)
async def export_report(
    export_request: ExportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Export report to PDF or Excel"""
    from fastapi.responses import StreamingResponse
    
    report_type = export_request.report_type
    format_type = export_request.format
    
    # Permission check
    if current_user['role_id'] not in [1, 2, 3]:  # Owner, Manager, Finance
        raise HTTPException(status_code=403, detail='Akses ditolak')
    
    # Generate report data based on type
    if report_type == 'executive_summary':
        # Get executive summary data
        summary_data = await get_executive_summary(
            export_request.start_date.isoformat() if export_request.start_date else datetime.now().isoformat(),
            export_request.end_date.isoformat() if export_request.end_date else datetime.now().isoformat(),
            current_user
        )
        
        if format_type == ExportFormat.PDF:
            # Convert ISO strings back to datetime objects for report generator
            if isinstance(summary_data.get('report_generated_at'), str):
                summary_data['report_generated_at'] = datetime.fromisoformat(summary_data['report_generated_at'].replace('Z', '+00:00'))
            if isinstance(summary_data.get('period_start'), str):
                summary_data['period_start'] = datetime.fromisoformat(summary_data['period_start'])
            if isinstance(summary_data.get('period_end'), str):
                summary_data['period_end'] = datetime.fromisoformat(summary_data['period_end'])
            buffer = report_generator.generate_executive_summary_pdf(summary_data)
            filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            media_type = "application/pdf"
        else:  # Excel
            buffer = report_generator.generate_executive_summary_excel(summary_data)
            filename = f"executive_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    else:
        raise HTTPException(status_code=400, detail=f'Report type {report_type} not supported')
    
    # Log activity
    await log_activity(
        current_user['sub'],
        'EXPORT_REPORT',
        f"Exported {report_type} as {format_type}",
        related_type='export'
    )
    
    return {
        'message': 'Export completed successfully',
        'filename': filename,
        'media_type': media_type,
        'size': len(buffer.getvalue()) if hasattr(buffer, 'getvalue') else 0
    }


# ============= LAPORAN HARIAN LOKET & KASIR ENDPOINTS =============

@api_router.post('/reports/loket-pelunasan', response_model=dict)
async def create_loket_pelunasan_report(
    report_data: LoketDailyReportPelunasanCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create Laporan Harian Loket (Pelunasan) dengan multiple bank accounts"""
    # Auto-calculate totals for each bank
    for bank in report_data.bank_accounts:
        # Sisa Setoran = Data Lunas - Setor Kasir - Transfer
        bank.sisa_setoran = bank.data_lunas - bank.setor_kasir - bank.transfer
        # Saldo Akhir = Saldo Awal + Saldo Inject - Data Lunas
        bank.saldo_akhir = bank.saldo_awal + bank.saldo_inject - bank.data_lunas
    
    # Calculate total setoran (sum of all sisa_setoran from all banks)
    total_setoran = sum(bank.sisa_setoran for bank in report_data.bank_accounts)
    
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['total_setoran'] = total_setoran
    report_dict['created_by'] = current_user['id']
    report_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['tanggal'] = doc['tanggal'].isoformat() if isinstance(doc['tanggal'], datetime) else doc['tanggal']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.loket_pelunasan_reports.insert_one(doc)
    
    await log_activity(
        current_user['id'],
        'CREATE_LOKET_PELUNASAN_REPORT',
        f"Created loket pelunasan report for {report_data.tanggal.strftime('%Y-%m-%d')} shift {report_data.shift}",
        related_type='loket_pelunasan_report',
        related_id=report_dict['id']
    )
    
    return {'message': 'Laporan loket pelunasan berhasil disimpan', 'id': report_dict['id'], 'total_setoran': total_setoran}


@api_router.get('/reports/loket-pelunasan', response_model=dict)
async def get_loket_pelunasan_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    shift: Optional[int] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get Laporan Loket Pelunasan dengan filters"""
    query = {}
    
    if business_id:
        query['business_id'] = business_id
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    if shift:
        query['shift'] = shift
    
    reports = await db.loket_pelunasan_reports.find(query, {'_id': 0}).sort('tanggal', -1).to_list(length=100)
    
    return {
        'reports': reports,
        'count': len(reports)
    }


@api_router.post('/reports/kasir-harian', response_model=dict)
async def create_kasir_harian_report(
    report_data: KasirHarianReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create Laporan Harian Kasir dengan auto-calculations"""
    # Calculate totals
    total_setoran_pagi = sum(entry.amount for entry in report_data.setoran_pagi)
    total_setoran_siang = sum(entry.amount for entry in report_data.setoran_siang)
    total_topup = sum(entry.amount for entry in report_data.transfer_topup)
    
    # Calculate total kas kecil
    total_kas_kecil = (
        report_data.penerimaan_kas_kecil - 
        report_data.pengurangan_kas_kecil - 
        report_data.belanja_loket
    )
    
    report_dict = report_data.model_dump()
    report_dict['id'] = generate_id()
    report_dict['total_setoran_pagi'] = total_setoran_pagi
    report_dict['total_setoran_siang'] = total_setoran_siang
    report_dict['total_topup'] = total_topup
    report_dict['total_kas_kecil'] = total_kas_kecil
    report_dict['created_by'] = current_user['id']
    report_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = report_dict.copy()
    doc['tanggal'] = doc['tanggal'].isoformat() if isinstance(doc['tanggal'], datetime) else doc['tanggal']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.kasir_daily_reports.insert_one(doc)
    
    await log_activity(
        current_user['id'],
        'CREATE_KASIR_DAILY_REPORT',
        f"Created kasir daily report for {report_data.tanggal.strftime('%Y-%m-%d')}",
        related_type='kasir_daily_report',
        related_id=report_dict['id']
    )
    
    return {
        'message': 'Laporan kasir harian berhasil disimpan',
        'id': report_dict['id'],
        'totals': {
            'setoran_pagi': total_setoran_pagi,
            'setoran_siang': total_setoran_siang,
            'topup': total_topup,
            'kas_kecil': total_kas_kecil
        }
    }


@api_router.get('/reports/kasir-harian', response_model=dict)
async def get_kasir_daily_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get Laporan Kasir Harian dengan filters"""
    query = {}
    
    if business_id:
        query['business_id'] = business_id
    
    if start_date and end_date:
        query['tanggal'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    reports = await db.kasir_daily_reports.find(query, {'_id': 0}).sort('tanggal', -1).to_list(length=100)
    
    return {
        'reports': reports,
        'count': len(reports)
    }


# 5. SMART ALERTS ENDPOINTS

@api_router.get('/alerts', response_model=dict)
async def get_alerts(
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    business_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get alerts with filters"""
    query = {}
    
    if severity:
        query['severity'] = severity
    
    if is_resolved is not None:
        query['is_resolved'] = is_resolved
    
    if business_id:
        query['business_id'] = business_id
    
    alerts = await db.alerts.find(query, {'_id': 0}).sort('triggered_at', -1).to_list(length=100)
    
    return {
        'alerts': alerts,
        'count': len(alerts),
        'unresolved_count': len([a for a in alerts if not a.get('is_resolved', False)])
    }


@api_router.post('/alerts/check', response_model=dict)
async def check_and_generate_alerts(
    current_user: dict = Depends(get_current_user)
):
    """Check conditions and generate alerts"""
    # Permission check: Only Owner, Manager can trigger alert checks
    if current_user['role_id'] not in [1, 2]:
        raise HTTPException(status_code=403, detail='Akses ditolak')
    
    alerts_generated = []
    
    # Check 1: Low cash position
    # Get total cash from transactions
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    transactions = await db.transactions.find({
        'created_at': {'$gte': today.isoformat()}
    }, {'_id': 0}).to_list(length=10000)
    
    cash_position = sum(t['amount'] for t in transactions if t['transaction_type'] == 'income') - \
                    sum(t['amount'] for t in transactions if t['transaction_type'] == 'expense')
    
    if cash_position < 1000000:  # Threshold: 1 juta
        alert = {
            'id': generate_id(),
            'alert_type': 'low_cash',
            'severity': 'warning',
            'title': 'Posisi Kas Rendah',
            'message': f'Posisi kas saat ini: Rp {cash_position:,.0f}. Di bawah threshold Rp 1.000.000',
            'threshold_value': 1000000,
            'current_value': cash_position,
            'is_resolved': False,
            'triggered_at': utc_now().isoformat()
        }
        await db.alerts.insert_one(alert)
        alerts_generated.append(alert)
    
    # Check 2: Pending orders > 3 days
    three_days_ago = (datetime.now() - timedelta(days=3)).isoformat()
    old_pending = await db.orders.find({
        'status': 'pending',
        'created_at': {'$lte': three_days_ago}
    }, {'_id': 0}).to_list(length=100)
    
    if old_pending:
        for order in old_pending[:5]:  # Max 5 alerts
            alert = {
                'id': generate_id(),
                'alert_type': 'pending_orders',
                'severity': 'warning',
                'title': 'Order Pending Terlalu Lama',
                'message': f"Order #{order['order_number']} pending sejak {order['created_at']}",
                'related_id': order['id'],
                'related_type': 'order',
                'action_url': f'/orders?id={order["id"]}',
                'is_resolved': False,
                'triggered_at': utc_now().isoformat()
            }
            await db.alerts.insert_one(alert)
            alerts_generated.append(alert)
    
    # Check 3: High expenses (>70% of revenue)
    businesses = await db.businesses.find({'is_active': True}, {'_id': 0}).to_list(length=100)
    
    for business in businesses:
        b_transactions = await db.transactions.find({
            'business_id': business['id'],
            'created_at': {'$gte': today.isoformat()}
        }, {'_id': 0}).to_list(length=10000)
        
        revenue = sum(t['amount'] for t in b_transactions if t['transaction_type'] == 'income')
        expenses = sum(t['amount'] for t in b_transactions if t['transaction_type'] == 'expense')
        
        if revenue > 0 and (expenses / revenue) > 0.7:
            alert = {
                'id': generate_id(),
                'alert_type': 'high_expenses',
                'severity': 'warning',
                'title': 'Rasio Pengeluaran Tinggi',
                'message': f"{business['name']}: Pengeluaran {expenses/revenue*100:.1f}% dari pendapatan",
                'business_id': business['id'],
                'threshold_value': 70,
                'current_value': expenses/revenue*100,
                'is_resolved': False,
                'triggered_at': utc_now().isoformat()
            }
            await db.alerts.insert_one(alert)
            alerts_generated.append(alert)
    
    return {
        'message': 'Alert check completed',
        'alerts_generated': len(alerts_generated),
        'alerts': []  # Temporarily return empty list to avoid serialization issues
    }


@api_router.put('/alerts/{alert_id}/resolve', response_model=dict)
async def resolve_alert(
    alert_id: str,
    notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Mark alert as resolved"""
    result = await db.alerts.update_one(
        {'id': alert_id},
        {
            '$set': {
                'is_resolved': True,
                'resolved_at': utc_now().isoformat(),
                'resolved_by': current_user['sub'],
                'notes': notes
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Alert not found')
    
    await log_activity(
        current_user['sub'],
        'RESOLVE_ALERT',
        f"Resolved alert {alert_id}",
        related_type='alert',
        related_id=alert_id
    )
    
    return {'message': 'Alert resolved successfully'}


# ============= UNIVERSAL INCOME/EXPENSE ROUTES (PER-BUSINESS SYSTEM) =============

# INCOME ENDPOINTS

@api_router.post('/business/{business_id}/income', response_model=UniversalIncome)
async def create_income(
    business_id: str,
    income_data: UniversalIncomeCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create income entry for a business"""
    # Check permission - Owner, Manager, Finance, Kasir, Loket
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5, 6]:  # Owner, Manager, Finance, Kasir, Loket
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    # Verify business exists
    business = await db.businesses.find_one({'id': business_id}, {'_id': 0})
    if not business:
        raise HTTPException(status_code=404, detail='Bisnis tidak ditemukan')
    
    income_dict = income_data.model_dump()
    income_dict['id'] = generate_id()
    income_dict['income_code'] = generate_code('INC', 10)
    income_dict['business_id'] = business_id
    income_dict['created_by'] = current_user['sub']
    income_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = income_dict.copy()
    doc['transaction_date'] = doc['transaction_date'].isoformat() if isinstance(doc['transaction_date'], datetime) else doc['transaction_date']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.universal_income.insert_one(doc)
    
    # AUTO-CREATE TRANSACTION for accounting sync
    transaction = {
        'id': generate_id(),
        'transaction_code': generate_code('TXN', 12),
        'business_id': business_id,
        'transaction_type': 'income',
        'category': income_dict['category'].value if hasattr(income_dict['category'], 'value') else income_dict['category'],
        'description': income_dict['description'],
        'amount': income_dict['amount'],
        'payment_method': income_dict['payment_method'],
        'reference_number': income_dict.get('reference_number'),
        'order_id': income_dict.get('order_id'),
        'created_by': current_user['sub'],
        'created_at': utc_now().isoformat()
    }
    await db.transactions.insert_one(transaction)
    
    # Log activity
    await log_activity(
        current_user['sub'],
        'CREATE_INCOME',
        f"Created income entry: {income_dict['description']} - Rp {income_dict['amount']:,.0f}",
        related_type='income',
        related_id=income_dict['id'],
        metadata={'business_id': business_id, 'amount': income_dict['amount']}
    )
    
    return UniversalIncome(**income_dict)

@api_router.get('/business/{business_id}/income', response_model=List[UniversalIncome])
async def get_business_income(
    business_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all income entries for a business"""
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5, 6]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    query = {'business_id': business_id}
    
    if start_date and end_date:
        query['transaction_date'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    if category:
        query['category'] = category
    
    incomes = await db.universal_income.find(query, {'_id': 0}).sort('transaction_date', -1).to_list(1000)
    
    for income in incomes:
        if isinstance(income.get('transaction_date'), str):
            income['transaction_date'] = datetime.fromisoformat(income['transaction_date'])
        if isinstance(income.get('created_at'), str):
            income['created_at'] = datetime.fromisoformat(income['created_at'])
    
    return incomes

@api_router.delete('/business/{business_id}/income/{income_id}')
async def delete_income(
    business_id: str,
    income_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete income entry (Owner/Manager only)"""
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Hanya Owner/Manager dapat menghapus data')
    
    result = await db.universal_income.delete_one({'id': income_id, 'business_id': business_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Data pemasukan tidak ditemukan')
    
    # Also delete related transaction
    await db.transactions.delete_many({'reference_number': income_id})
    
    await log_activity(
        current_user['sub'],
        'DELETE_INCOME',
        f"Deleted income entry {income_id}",
        related_type='income',
        related_id=income_id
    )
    
    return {'message': 'Data pemasukan berhasil dihapus'}

# EXPENSE ENDPOINTS

@api_router.post('/business/{business_id}/expense', response_model=UniversalExpense)
async def create_expense(
    business_id: str,
    expense_data: UniversalExpenseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create expense entry for a business"""
    # Check permission - Owner, Manager, Finance, Kasir
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5]:  # Owner, Manager, Finance, Kasir
        raise HTTPException(status_code=403, detail='Tidak memiliki izin')
    
    # Verify business exists
    business = await db.businesses.find_one({'id': business_id}, {'_id': 0})
    if not business:
        raise HTTPException(status_code=404, detail='Bisnis tidak ditemukan')
    
    expense_dict = expense_data.model_dump()
    expense_dict['id'] = generate_id()
    expense_dict['expense_code'] = generate_code('EXP', 10)
    expense_dict['business_id'] = business_id
    expense_dict['created_by'] = current_user['sub']
    expense_dict['created_at'] = utc_now()
    
    # Serialize datetime
    doc = expense_dict.copy()
    doc['transaction_date'] = doc['transaction_date'].isoformat() if isinstance(doc['transaction_date'], datetime) else doc['transaction_date']
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.universal_expense.insert_one(doc)
    
    # AUTO-CREATE TRANSACTION for accounting sync
    transaction = {
        'id': generate_id(),
        'transaction_code': generate_code('TXN', 12),
        'business_id': business_id,
        'transaction_type': 'expense',
        'category': expense_dict['category'].value if hasattr(expense_dict['category'], 'value') else expense_dict['category'],
        'description': expense_dict['description'],
        'amount': expense_dict['amount'],
        'payment_method': expense_dict['payment_method'],
        'reference_number': expense_dict.get('reference_number'),
        'order_id': expense_dict.get('order_id'),
        'created_by': current_user['sub'],
        'created_at': utc_now().isoformat()
    }
    await db.transactions.insert_one(transaction)
    
    # Log activity
    await log_activity(
        current_user['sub'],
        'CREATE_EXPENSE',
        f"Created expense entry: {expense_dict['description']} - Rp {expense_dict['amount']:,.0f}",
        related_type='expense',
        related_id=expense_dict['id'],
        metadata={'business_id': business_id, 'amount': expense_dict['amount']}
    )
    
    return UniversalExpense(**expense_dict)

@api_router.get('/business/{business_id}/expense', response_model=List[UniversalExpense])
async def get_business_expense(
    business_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all expense entries for a business"""
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3, 5]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    query = {'business_id': business_id}
    
    if start_date and end_date:
        query['transaction_date'] = {
            '$gte': start_date,
            '$lte': end_date
        }
    
    if category:
        query['category'] = category
    
    expenses = await db.universal_expense.find(query, {'_id': 0}).sort('transaction_date', -1).to_list(1000)
    
    for expense in expenses:
        if isinstance(expense.get('transaction_date'), str):
            expense['transaction_date'] = datetime.fromisoformat(expense['transaction_date'])
        if isinstance(expense.get('created_at'), str):
            expense['created_at'] = datetime.fromisoformat(expense['created_at'])
    
    return expenses

@api_router.delete('/business/{business_id}/expense/{expense_id}')
async def delete_expense(
    business_id: str,
    expense_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete expense entry (Owner/Manager only)"""
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Hanya Owner/Manager dapat menghapus data')
    
    result = await db.universal_expense.delete_one({'id': expense_id, 'business_id': business_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Data pengeluaran tidak ditemukan')
    
    # Also delete related transaction
    await db.transactions.delete_many({'reference_number': expense_id})
    
    await log_activity(
        current_user['sub'],
        'DELETE_EXPENSE',
        f"Deleted expense entry {expense_id}",
        related_type='expense',
        related_id=expense_id
    )
    
    return {'message': 'Data pengeluaran berhasil dihapus'}

# BUSINESS DASHBOARD ENDPOINT

@api_router.get('/business/{business_id}/dashboard', response_model=BusinessDashboardStats)
async def get_business_dashboard(
    business_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard statistics for a specific business"""
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2, 3]:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    # Get business info
    business = await db.businesses.find_one({'id': business_id}, {'_id': 0})
    if not business:
        raise HTTPException(status_code=404, detail='Bisnis tidak ditemukan')
    
    # Default date range: Last 30 days
    if not start_date:
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Get income data
    income_query = {
        'business_id': business_id,
        'transaction_date': {'$gte': start_date, '$lte': end_date + 'T23:59:59'}
    }
    incomes = await db.universal_income.find(income_query, {'_id': 0}).to_list(10000)
    
    total_income = sum(inc['amount'] for inc in incomes)
    income_by_category = {}
    for inc in incomes:
        cat = inc.get('category', 'other_income')
        income_by_category[cat] = income_by_category.get(cat, 0) + inc['amount']
    
    # Get expense data
    expense_query = {
        'business_id': business_id,
        'transaction_date': {'$gte': start_date, '$lte': end_date + 'T23:59:59'}
    }
    expenses = await db.universal_expense.find(expense_query, {'_id': 0}).to_list(10000)
    
    total_expense = sum(exp['amount'] for exp in expenses)
    expense_by_category = {}
    for exp in expenses:
        cat = exp.get('category', 'other_expense')
        expense_by_category[cat] = expense_by_category.get(cat, 0) + exp['amount']
    
    # Get orders data
    order_query = {
        'business_id': business_id,
        'created_at': {'$gte': start_date, '$lte': end_date + 'T23:59:59'}
    }
    orders = await db.orders.find(order_query, {'_id': 0}).to_list(10000)
    
    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.get('status') == 'completed'])
    pending_orders = len([o for o in orders if o.get('status') == 'pending'])
    cancelled_orders = len([o for o in orders if o.get('status') == 'cancelled'])
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    # Calculate profit metrics
    net_profit = total_income - total_expense
    profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
    
    # Top income sources
    top_income_sources = [
        {'category': cat, 'amount': amt, 'percentage': (amt / total_income * 100) if total_income > 0 else 0}
        for cat, amt in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Top expense categories
    top_expense_categories = [
        {'category': cat, 'amount': amt, 'percentage': (amt / total_expense * 100) if total_expense > 0 else 0}
        for cat, amt in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Income trend (daily aggregation)
    income_trend = []
    expense_trend = []
    
    # Simple daily aggregation for last 7 days
    for i in range(7):
        day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime('%Y-%m-%d')
        day_income = sum(inc['amount'] for inc in incomes if inc.get('transaction_date', '')[:10] == day)
        day_expense = sum(exp['amount'] for exp in expenses if exp.get('transaction_date', '')[:10] == day)
        income_trend.append({'date': day, 'amount': day_income})
        expense_trend.append({'date': day, 'amount': day_expense})
    
    income_trend.reverse()
    expense_trend.reverse()
    
    return BusinessDashboardStats(
        business_id=business_id,
        business_name=business['name'],
        business_category=business['category'],
        period_start=datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date,
        period_end=datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date,
        total_income=total_income,
        total_expense=total_expense,
        net_profit=net_profit,
        profit_margin=profit_margin,
        total_orders=total_orders,
        completed_orders=completed_orders,
        pending_orders=pending_orders,
        cancelled_orders=cancelled_orders,
        completion_rate=completion_rate,
        income_by_category=income_by_category,
        expense_by_category=expense_by_category,
        top_income_sources=top_income_sources,
        top_expense_categories=top_expense_categories,
        income_trend=income_trend,
        expense_trend=expense_trend
    )


# Include router (MUST be after all endpoint definitions)
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=['*'],
    allow_headers=['*'],
)

# Gzip compression middleware for faster response (60-80% bandwidth reduction)
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.on_event('shutdown')
async def shutdown_db_client():
    client.close()
