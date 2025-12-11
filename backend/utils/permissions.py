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

# Permission constants - Updated strict permission matrix
PERMISSIONS = {
    # Dashboard - All roles
    'view_dashboard': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_CS, ROLE_KASIR, ROLE_LOKET, ROLE_TEKNISI],
    
    # Businesses - Owner & Manager only
    'view_businesses': [ROLE_OWNER, ROLE_MANAGER],
    'create_businesses': [ROLE_OWNER, ROLE_MANAGER],
    'edit_businesses': [ROLE_OWNER, ROLE_MANAGER],
    'delete_businesses': [ROLE_OWNER],
    
    # Orders - Owner, Manager, Kasir, Loket
    'view_orders': [ROLE_OWNER, ROLE_MANAGER, ROLE_KASIR, ROLE_LOKET],
    'create_orders': [ROLE_OWNER, ROLE_MANAGER, ROLE_KASIR, ROLE_LOKET],
    'edit_orders': [ROLE_OWNER, ROLE_MANAGER, ROLE_KASIR, ROLE_LOKET],
    'delete_orders': [ROLE_OWNER],
    
    # Teknisi Jobs - Owner, Manager, Kasir, Teknisi
    'view_teknisi_jobs': [ROLE_OWNER, ROLE_MANAGER, ROLE_KASIR, ROLE_TEKNISI],
    'update_teknisi_jobs': [ROLE_OWNER, ROLE_MANAGER, ROLE_TEKNISI],
    
    # Accounting - Owner, Manager, Finance only
    'view_accounting': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE],
    'create_accounting': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE],
    'edit_accounting': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE],
    'delete_accounting': [ROLE_OWNER],
    
    # Users - Owner & Manager
    'view_users': [ROLE_OWNER, ROLE_MANAGER],
    'create_users': [ROLE_OWNER],
    'edit_users': [ROLE_OWNER, ROLE_MANAGER],
    'delete_users': [ROLE_OWNER],
    
    # Reports - Owner, Manager, Finance, Kasir, Loket
    'view_reports': [ROLE_OWNER, ROLE_MANAGER, ROLE_FINANCE, ROLE_KASIR, ROLE_LOKET],
    'create_loket_report': [ROLE_OWNER, ROLE_MANAGER, ROLE_LOKET],
    'create_kasir_report': [ROLE_OWNER, ROLE_MANAGER, ROLE_KASIR],
    'edit_reports': [ROLE_OWNER, ROLE_MANAGER],
    'delete_reports': [ROLE_OWNER],
    
    # Loyalty & CSR - Owner & Manager only
    'view_loyalty': [ROLE_OWNER, ROLE_MANAGER],
    'manage_loyalty': [ROLE_OWNER, ROLE_MANAGER],
    'delete_loyalty': [ROLE_OWNER],
    'view_csr': [ROLE_OWNER, ROLE_MANAGER],
    'manage_csr': [ROLE_OWNER, ROLE_MANAGER],
    'delete_csr': [ROLE_OWNER],
    
    # Activity Logs - Owner & Manager
    'view_activity_logs': [ROLE_OWNER, ROLE_MANAGER],
    
    # Settings - Owner only
    'view_settings': [ROLE_OWNER],
    'manage_settings': [ROLE_OWNER],
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
