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

@api_router.delete('/reports/kasir-daily/{report_id}')
async def delete_kasir_daily_report(report_id: str, current_user: dict = Depends(get_current_user)):
    # Check permission - only Owner or Manager
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    if user['role_id'] not in [1, 2]:  # Owner or Manager
        raise HTTPException(status_code=403, detail='Tidak memiliki izin untuk menghapus laporan')
    
    result = await db.kasir_daily_reports.delete_one({'id': report_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail='Laporan tidak ditemukan')
    
    return {'message': 'Laporan berhasil dihapus'}

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
