from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from datetime import datetime, timezone
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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
    
    # Log activity
    activity_log = {
        'id': generate_id(),
        'user_id': user['id'],
        'action': 'login',
        'description': f"Login dari {request.client.host}",
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'created_at': utc_now().isoformat()
    }
    await db.activity_logs.insert_one(activity_log)
    
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
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if business_id:
        query['business_id'] = business_id
    if status_filter:
        query['status'] = status_filter
    
    orders = await db.orders.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
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
    order_dict['payment_status'] = PaymentStatus.UNPAID
    order_dict['created_by'] = current_user['sub']
    order_dict['created_at'] = utc_now()
    order_dict['updated_at'] = utc_now()
    
    # Serialize datetimes
    doc = order_dict.copy()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.orders.insert_one(doc)
    
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
            'message': f"Anda ditugaskan untuk pesanan {order_id}",
            'type': 'info',
            'related_id': order_id,
            'related_type': 'order',
            'is_read': False,
            'created_at': utc_now().isoformat()
        }
        await db.notifications.insert_one(notif)
    
    if paid_amount is not None:
        update_data['paid_amount'] = paid_amount
    
    result = await db.orders.update_one({'id': order_id}, {'$set': update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Order tidak ditemukan')
    
    return {'message': 'Order berhasil diupdate'}

# ============= TRANSACTION ROUTES =============
@api_router.get('/transactions', response_model=List[Transaction])
async def get_transactions(
    business_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    query = {}
    if business_id:
        query['business_id'] = business_id
    if transaction_type:
        query['transaction_type'] = transaction_type
    
    transactions = await db.transactions.find(query, {'_id': 0}).sort('created_at', -1).to_list(1000)
    for txn in transactions:
        if isinstance(txn.get('created_at'), str):
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

# ============= USER MANAGEMENT ROUTES =============
@api_router.get('/users', response_model=List[UserResponse])
async def get_users(current_user: dict = Depends(get_current_user)):
    # Check permission
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] != ROLE_OWNER:
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
    
    return LoketDailyReport(**report_dict)

@api_router.get('/reports/kasir-daily', response_model=List[KasirDailyReport])
async def get_kasir_daily_reports(
    business_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
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
    
    return KasirDailyReport(**report_dict)

@api_router.delete('/reports/loket-daily/{report_id}')
async def delete_loket_daily_report(report_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - only Owner or Manager
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin untuk menghapus laporan')
    
    result = await db.loket_daily_reports.delete_one({'id': report_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    return {'message': 'Laporan berhasil dihapus'}

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
    # Get orders assigned to current teknisi
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    # If teknisi, only show assigned orders. If manager/owner, show all
    if user['role_id'] == 7:  # Teknisi
        query = {'assigned_to': current_user['sub']}
    elif user['role_id'] in [1, 2]:  # Owner or Manager
        query = {}
    else:
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
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
        update_data['notes'] = f"{current_notes}\n[{timestamp}] {user['full_name']}: {notes}".strip()
    
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
    status: Optional[str] = None,
    actual_participants: Optional[int] = None,
    actual_cost: Optional[float] = None,
    current_user: dict = Depends(get_current_user)
):
    update_data = {'updated_at': utc_now().isoformat()}
    if status:
        update_data['status'] = status
    if actual_participants is not None:
        update_data['actual_participants'] = actual_participants
    if actual_cost is not None:
        update_data['actual_cost'] = actual_cost
    
    result = await db.loyalty_programs.update_one({'id': program_id}, {'$set': update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail='Program tidak ditemukan')
    
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

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('shutdown')
async def shutdown_db_client():
    client.close()
