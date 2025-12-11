from typing import List
from fastapi import HTTPException, status

# Role IDs
ROLE_OWNER = 1
ROLE_MANAGER = 2
ROLE_FINANCE = 3
ROLE_CS = 4
ROLE_KASIR = 5
ROLE_LOKET = 6
ROLE_TEKNISI = 7

# Permission constants
PERMISSIONS = {
    'customer_data': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_CS, ROLE_KASIR, ROLE_LOKET],
    'transaction_entry': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_CS, ROLE_KASIR, ROLE_LOKET],
    'payment_processing': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_KASIR, ROLE_LOKET],
    'financial_reports': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE],
    'user_management': [ROLE_OWNER],
    'system_config': [ROLE_OWNER],
    'view_orders': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_CS, ROLE_KASIR, ROLE_LOKET, ROLE_TEKNISI],
    'create_orders': [ROLE_OWNER, ROLE_MANAGER, ROLE_CS, ROLE_KASIR, ROLE_LOKET],
    'approve_transactions': [ROLE_OWNER, ROLE_MANAGER],
    'payroll_management': [ROLE_OWNER, ROLE_FINANCE],
}

def check_permission(user_data: dict, permission: str) -> bool:
    role_id = user_data.get('role_id')
    if not role_id:
        return False
    return role_id in PERMISSIONS.get(permission, [])

def require_permission(user_data: dict, permission: str):
    if not check_permission(user_data, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Anda tidak memiliki izin untuk mengakses resource ini',
        )
