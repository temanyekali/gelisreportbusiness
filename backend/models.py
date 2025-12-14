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
    IT_DEVELOPER = 'IT Developer'

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
    requires_technician: bool = False  # Flag untuk sync dengan modul teknisi

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

# Accounting Models
class AccountType(str, Enum):
    ASSET = 'asset'
    LIABILITY = 'liability'
    EQUITY = 'equity'
    REVENUE = 'revenue'
    EXPENSE = 'expense'

class JournalEntryType(str, Enum):
    DEBIT = 'debit'
    CREDIT = 'credit'

class AccountBase(BaseModel):
    account_code: str
    account_name: str
    account_type: AccountType
    parent_account: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    balance: float = 0
    created_at: datetime

class JournalLineItem(BaseModel):
    account_id: str
    account_name: str
    entry_type: JournalEntryType
    amount: float
    description: Optional[str] = None

class JournalEntryBase(BaseModel):
    business_id: str
    transaction_date: datetime
    reference_number: Optional[str] = None
    description: str
    line_items: List[JournalLineItem]
    notes: Optional[str] = None

class JournalEntryCreate(JournalEntryBase):
    pass

class JournalEntry(JournalEntryBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    entry_number: str
    total_debit: float
    total_credit: float
    is_balanced: bool
    created_by: str
    created_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class CashFlowCategory(str, Enum):
    OPERATING = 'operating'
    INVESTING = 'investing'
    FINANCING = 'financing'

class CashFlowEntry(BaseModel):
    category: CashFlowCategory
    description: str
    amount: float
    is_inflow: bool  # True for cash in, False for cash out

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

# Loyalty Program Models
class ProgramStatus(str, Enum):
    PLANNED = 'planned'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class LoyaltyProgramBase(BaseModel):
    program_name: str
    description: str
    start_date: datetime
    end_date: datetime
    target_customers: Optional[int] = None
    budget: float = 0
    rewards_offered: Optional[str] = None
    status: ProgramStatus = ProgramStatus.PLANNED
    notes: Optional[str] = None

class LoyaltyProgramCreate(LoyaltyProgramBase):
    pass

class LoyaltyProgram(LoyaltyProgramBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    actual_participants: int = 0
    actual_cost: float = 0
    created_by: str
    created_at: datetime
    updated_at: datetime

# CSR Program Models
class CSRProgramBase(BaseModel):
    program_name: str
    description: str
    category: str  # Pendidikan, Kesehatan, Lingkungan, dll
    start_date: datetime
    end_date: Optional[datetime] = None
    budget: float = 0
    beneficiary_target: Optional[int] = None
    location: Optional[str] = None
    status: ProgramStatus = ProgramStatus.PLANNED
    notes: Optional[str] = None

class CSRProgramCreate(CSRProgramBase):
    pass

class CSRProgram(CSRProgramBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    actual_beneficiaries: int = 0
    actual_cost: float = 0
    impact_report: Optional[str] = None
    created_by: str
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

# Daily Loket Report Models
class BankBalance(BaseModel):
    bank_name: str  # BRIS, Mandiri, BCA, dll
    saldo_awal: float
    saldo_inject: float
    data_lunas: float
    setor_kasir: float
    transfer_amount: float
    sisa_setoran: float
    saldo_akhir: float
    uang_lebih: float = 0

class LoketDailyReportBase(BaseModel):
    business_id: str
    report_date: datetime
    nama_petugas: str
    shift: int  # 1, 2, 3
    bank_balances: List[BankBalance] = []
    total_setoran_shift: float = 0
    notes: Optional[str] = None

class LoketDailyReportCreate(LoketDailyReportBase):
    pass

class LoketDailyReport(LoketDailyReportBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_by: str
    created_at: datetime

# Cashier Daily Report Models
class TopupTransaction(BaseModel):
    amount: float
    description: Optional[str] = None

class KasirDailyReportBase(BaseModel):
    business_id: str
    report_date: datetime
    setoran_pagi: float = 0
    setoran_siang: float = 0
    setoran_sore: float = 0
    setoran_deposit_loket_luar: float = 0
    setoran_pelunasan_pagi: float = 0
    setoran_pelunasan_siang: float = 0
    topup_transactions: List[TopupTransaction] = []
    total_topup: float = 0
    penerimaan_kas_kecil: float = 0
    pengurangan_kas_kecil: float = 0
    belanja_loket: float = 0
    total_kas_kecil: float = 0
    penerimaan_admin: float = 0
    total_admin: float = 0
    saldo_bank: float = 0
    saldo_brankas: float = 0
    notes: Optional[str] = None

class KasirDailyReportCreate(KasirDailyReportBase):
    pass

class KasirDailyReport(KasirDailyReportBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_by: str
    created_at: datetime


# ============= FASE 1: CRITICAL ENHANCEMENTS MODELS =============

# PLN Technical Work Step Models
class TechnicalStepStatus(str, Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'

class TechnicalWorkStep(BaseModel):
    step_name: str
    step_weight: float  # Bobot dalam persen (0-100)
    status: TechnicalStepStatus = TechnicalStepStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    photos: List[str] = []  # URLs/paths to uploaded photos
    assigned_to: Optional[str] = None

class TechnicalProgressBase(BaseModel):
    order_id: str
    steps: List[TechnicalWorkStep] = [
        TechnicalWorkStep(step_name="Survey Teknis", step_weight=50.0),
        TechnicalWorkStep(step_name="Pemasangan/Instalasi", step_weight=20.0),
        TechnicalWorkStep(step_name="Pemeriksaan NIDI/SLO", step_weight=20.0),
        TechnicalWorkStep(step_name="Pemberkasan Teknis", step_weight=8.0),
        TechnicalWorkStep(step_name="Pemasangan KWH Meter", step_weight=2.0),
    ]
    overall_progress: float = 0.0  # Auto-calculated from completed steps
    notes: Optional[str] = None

class TechnicalProgressCreate(TechnicalProgressBase):
    pass

class TechnicalProgress(TechnicalProgressBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_by: str
    created_at: datetime
    updated_at: datetime

# PPOB Product Breakdown Models
class PPOBProductBreakdown(BaseModel):
    product_type: str  # Token PLN, Pulsa, PDAM, Paket Data, TV Kabel, dll
    transaction_count: int = 0
    total_amount: float = 0.0
    total_fee: float = 0.0
    total_commission: float = 0.0

class PPOBShiftReport(BaseModel):
    business_id: str
    report_date: datetime
    shift: int  # 1, 2, atau 3
    petugas_name: str
    product_breakdown: List[PPOBProductBreakdown] = []
    total_transactions: int = 0
    total_amount: float = 0.0
    total_fee: float = 0.0
    total_commission: float = 0.0
    bank_deposit: float = 0.0
    notes: Optional[str] = None

class PPOBShiftReportCreate(BaseModel):
    business_id: str
    report_date: datetime
    shift: int
    petugas_name: str
    product_breakdown: List[PPOBProductBreakdown] = []
    notes: Optional[str] = None

class PPOBShiftReportResponse(PPOBShiftReport):
    model_config = ConfigDict(extra='ignore')
    id: str
    created_by: str
    created_at: datetime

# Executive Summary Report Models
class BusinessUnitKPI(BaseModel):
    business_id: str
    business_name: str
    business_category: str
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    profit_margin: float = 0.0  # Percentage
    total_orders: int = 0
    completed_orders: int = 0
    pending_orders: int = 0
    completion_rate: float = 0.0  # Percentage
    average_order_value: float = 0.0
    growth_rate: float = 0.0  # Compared to previous period

class ExecutiveSummary(BaseModel):
    period_start: datetime
    period_end: datetime
    report_generated_at: datetime
    
    # Overall Summary
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    net_profit: float = 0.0
    overall_profit_margin: float = 0.0
    
    # Business Units Performance
    business_units: List[BusinessUnitKPI] = []
    
    # Top Performers
    best_performing_business: Optional[str] = None
    highest_revenue_business: Optional[str] = None
    highest_margin_business: Optional[str] = None
    
    # Alerts & Insights
    alerts: List[str] = []
    insights: List[str] = []
    recommendations: List[str] = []

# Smart Alerts Models
class AlertSeverity(str, Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'

class AlertType(str, Enum):
    LOW_CASH = 'low_cash'
    PENDING_ORDERS = 'pending_orders'
    AGING_RECEIVABLES = 'aging_receivables'
    HIGH_EXPENSES = 'high_expenses'
    MISSING_REPORTS = 'missing_reports'
    SYSTEM = 'system'

class AlertBase(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    business_id: Optional[str] = None
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    action_url: Optional[str] = None
    is_resolved: bool = False

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    model_config = ConfigDict(extra='ignore')
    id: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

# Export Models
class ExportFormat(str, Enum):
    PDF = 'pdf'
    EXCEL = 'excel'
    CSV = 'csv'

class ExportRequest(BaseModel):
    report_type: str  # executive_summary, loket_daily, kasir_daily, etc
    format: ExportFormat
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    business_id: Optional[str] = None
    filters: Dict[str, Any] = {}

# Financial Intelligence Models
class AgingBucket(BaseModel):
    bucket_name: str  # Current, 1-30 days, 31-60 days, 61-90 days, >90 days
    amount: float = 0.0
    count: int = 0
    percentage: float = 0.0

class AgingAnalysis(BaseModel):
    report_date: datetime
    receivables_aging: List[AgingBucket] = []
    payables_aging: List[AgingBucket] = []
    total_receivables: float = 0.0
    total_payables: float = 0.0
    overdue_receivables: float = 0.0
    overdue_payables: float = 0.0

class CashFlowProjection(BaseModel):
    projection_date: datetime
    projected_inflow: float = 0.0
    projected_outflow: float = 0.0
    projected_balance: float = 0.0
    confidence_level: str = 'medium'  # low, medium, high
    assumptions: List[str] = []

class BudgetVsActual(BaseModel):
    category: str
    budgeted_amount: float = 0.0
    actual_amount: float = 0.0
    variance: float = 0.0
    variance_percentage: float = 0.0
    status: str = 'on_track'  # on_track, over_budget, under_budget

class CostCenterAnalysis(BaseModel):
    business_id: str
    business_name: str
    period_start: datetime
    period_end: datetime
    direct_costs: float = 0.0
    indirect_costs: float = 0.0
    total_costs: float = 0.0
    cost_per_order: float = 0.0
    efficiency_score: float = 0.0  # 0-100

# Comparative Analysis Models
class PeriodComparison(BaseModel):
    metric_name: str
    current_period: float = 0.0
    previous_period: float = 0.0
    change_amount: float = 0.0
    change_percentage: float = 0.0
    trend: str = 'neutral'  # up, down, neutral

class BusinessBenchmark(BaseModel):
    business_id: str
    business_name: str
    metric_name: str
    current_value: float = 0.0
    average_value: float = 0.0
    best_value: float = 0.0
    rank: int = 0
    percentile: float = 0.0
