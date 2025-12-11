from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    OWNER = 'Owner'
    MANAGER = 'Manager'
    FINANCE = 'Finance'
    CS = 'Customer Service'
    KASIR = 'Kasir'
    LOKET = 'Loket'
    TEKNISI = 'Teknisi'

class OrderStatus(str, Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class PaymentStatus(str, Enum):
    UNPAID = 'unpaid'
    PARTIAL = 'partial'
    PAID = 'paid'
    REFUNDED = 'refunded'

class TransactionType(str, Enum):
    INCOME = 'income'
    EXPENSE = 'expense'
    TRANSFER = 'transfer'
    COMMISSION = 'commission'

class NotificationType(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    SUCCESS = 'success'

# User Models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role_id: int = 3
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    identifier: str  # username or email
    password: str

class User(UserBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

class UserResponse(User):
    role_name: Optional[str] = None

# Role Models
class Role(BaseModel):
    model_config = ConfigDict(extra='ignore')
    id: int
    name: str
    description: Optional[str] = None
    permissions: Dict[str, bool] = {}
    created_at: datetime

# Business Models
class BusinessBase(BaseModel):
    name: str
    category: str  # PPOB, PLN, Travel, PDAM, Inventory, Custom
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    settings: Dict[str, Any] = {}
    is_active: bool = True

class BusinessCreate(BusinessBase):
    pass

class Business(BusinessBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

# Business Field Models
class BusinessFieldBase(BaseModel):
    business_id: str
    field_name: str
    field_type: str  # text, number, date, dropdown, checkbox, textarea
    field_options: Optional[Dict[str, Any]] = None
    is_required: bool = False
    display_order: int = 0

class BusinessFieldCreate(BusinessFieldBase):
    pass

class BusinessField(BusinessFieldBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_at: datetime

# Order Models
class OrderBase(BaseModel):
    business_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    service_type: str
    order_details: Dict[str, Any] = {}
    total_amount: float = 0.0
    paid_amount: float = 0.0
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    order_number: str
    status: OrderStatus = OrderStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID
    assigned_to: Optional[str] = None
    completion_date: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: datetime

# Transaction Models
class TransactionBase(BaseModel):
    business_id: str
    transaction_type: TransactionType
    category: str
    description: str
    amount: float
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    order_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    transaction_code: str
    created_by: str
    created_at: datetime

# Payroll Models
class PayrollBase(BaseModel):
    user_id: str
    business_id: Optional[str] = None
    payroll_date: datetime
    period_start: datetime
    period_end: datetime
    base_salary: float = 0.0
    overtime_pay: float = 0.0
    bonus: float = 0.0
    deductions: float = 0.0
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class PayrollCreate(PayrollBase):
    pass

class Payroll(PayrollBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    total_salary: float = 0.0
    status: str = 'draft'
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_by: str
    created_at: datetime

# Commission Models
class CommissionBase(BaseModel):
    user_id: str
    order_id: Optional[str] = None
    business_id: str
    commission_type: str
    base_amount: float = 0.0
    commission_rate: float = 0.0
    commission_date: datetime
    notes: Optional[str] = None

class CommissionCreate(CommissionBase):
    pass

class Commission(CommissionBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    commission_amount: float = 0.0
    status: str = 'pending'
    paid_date: Optional[datetime] = None
    created_by: str
    created_at: datetime

# Notification Models
class NotificationBase(BaseModel):
    user_id: str
    title: str
    message: str
    type: NotificationType = NotificationType.INFO
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    action_url: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    is_read: bool = False
    created_at: datetime

# Activity Log Models
class ActivityLogBase(BaseModel):
    user_id: str
    action: str
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    related_id: Optional[str] = None
    related_type: Optional[str] = None

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLog(ActivityLogBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_at: datetime

# Settings Models
class SettingBase(BaseModel):
    setting_key: str
    setting_value: Dict[str, Any]
    description: Optional[str] = None

class SettingCreate(SettingBase):
    pass

class Setting(SettingBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    updated_by: Optional[str] = None
    updated_at: datetime

# Customer Models
class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    loyalty_points: int = 0
    loyalty_tier: str = 'Bronze'

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_at: datetime
    updated_at: datetime

# Token Response
class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserResponse

# Dashboard Stats
class DashboardStats(BaseModel):
    total_businesses: int
    total_orders: int
    total_revenue: float
    total_expenses: float
    active_orders: int
    pending_orders: int
    completed_orders_today: int
    revenue_today: float
    expenses_today: float
    net_today: float
