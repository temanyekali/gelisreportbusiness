# Script to add comprehensive logging to all critical operations
# This will be integrated into server.py

LOGGING_ADDITIONS = {
    # Business Operations
    'create_business': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_business',
        description=f"Created business: {biz_dict['name']}",
        related_type='business',
        related_id=biz_dict['id'],
        metadata={'business_name': biz_dict['name'], 'category': biz_dict.get('category')}
    )
    ''',
    
    'update_business': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_business',
        description=f"Updated business: {existing['name']}",
        related_type='business',
        related_id=business_id,
        metadata={'business_name': existing['name']}
    )
    ''',
    
    'delete_business': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_business',
        description=f"Deleted business: {business['name']}",
        related_type='business',
        related_id=business_id,
        metadata={'business_name': business['name'], 'deleted_by': user['full_name']}
    )
    ''',
    
    # Order Operations
    'create_order': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_order',
        description=f"Created order {order_dict['order_number']} for {order_dict['customer_name']}",
        related_type='order',
        related_id=order_dict['id'],
        metadata={
            'order_number': order_dict['order_number'],
            'customer_name': order_dict['customer_name'],
            'service_type': order_dict['service_type'],
            'total_amount': order_dict['total_amount'],
            'requires_technician': order_dict.get('requires_technician', False)
        }
    )
    ''',
    
    'update_order': '''
    log_metadata = {'order_number': order['order_number']}
    if status:
        log_metadata['new_status'] = status
    if payment_status:
        log_metadata['new_payment_status'] = payment_status
    if assigned_to:
        log_metadata['assigned_to'] = assigned_to
    if paid_amount:
        log_metadata['paid_amount'] = paid_amount
    
    await log_activity(
        user_id=current_user['sub'],
        action='update_order',
        description=f"Updated order {order['order_number']}",
        related_type='order',
        related_id=order_id,
        metadata=log_metadata
    )
    ''',
    
    'delete_order': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_order',
        description=f"Deleted order {order['order_number']} - Customer: {order['customer_name']}",
        related_type='order',
        related_id=order_id,
        metadata={
            'order_number': order['order_number'],
            'customer_name': order['customer_name'],
            'total_amount': order['total_amount']
        }
    )
    ''',
    
    # Transaction Operations
    'create_transaction_manual': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_transaction',
        description=f"Created {txn_dict['transaction_type']} transaction: {txn_dict['description']}",
        related_type='transaction',
        related_id=txn_dict['id'],
        metadata={
            'transaction_code': txn_dict['transaction_code'],
            'transaction_type': txn_dict['transaction_type'],
            'category': txn_dict['category'],
            'amount': txn_dict['amount'],
            'source': 'manual_input'
        }
    )
    ''',
    
    'update_transaction': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_transaction',
        description=f"Updated transaction {existing['transaction_code']}",
        related_type='transaction',
        related_id=transaction_id,
        metadata={
            'transaction_code': existing['transaction_code'],
            'old_amount': existing['amount'],
            'new_amount': txn_dict['amount']
        }
    )
    ''',
    
    # User Operations
    'create_user': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_user',
        description=f"Created new user: {user_dict['username']} ({user_dict['full_name']})",
        related_type='user',
        related_id=user_dict['id'],
        metadata={
            'username': user_dict['username'],
            'email': user_dict['email'],
            'role_id': user_dict['role_id'],
            'created_by': user['full_name']
        }
    )
    ''',
    
    'update_user': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_user',
        description=f"Updated user: {target_user['username']}",
        related_type='user',
        related_id=user_id,
        metadata={
            'username': target_user['username'],
            'updated_by': user['full_name']
        }
    )
    ''',
    
    'delete_user': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_user',
        description=f"Deleted user: {target_user['username']} ({target_user['full_name']})",
        related_type='user',
        related_id=user_id,
        metadata={
            'username': target_user['username'],
            'email': target_user['email'],
            'role_id': target_user['role_id'],
            'deleted_by': user['full_name']
        }
    )
    ''',
    
    'toggle_user_active': '''
    await log_activity(
        user_id=current_user['sub'],
        action='toggle_user_status',
        description=f"{'Activated' if new_status else 'Deactivated'} user: {target_user['username']}",
        related_type='user',
        related_id=user_id,
        metadata={
            'username': target_user['username'],
            'new_status': 'active' if new_status else 'inactive',
            'changed_by': user['full_name']
        }
    )
    ''',
    
    # Report Operations
    'create_loket_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_loket_report',
        description=f"Submitted loket report shift {report_dict['shift']} - {report_dict['nama_petugas']}",
        related_type='report',
        related_id=report_dict['id'],
        metadata={
            'report_type': 'loket_daily',
            'shift': report_dict['shift'],
            'total_setoran': report_dict.get('total_setoran_shift', 0),
            'petugas': report_dict['nama_petugas']
        }
    )
    ''',
    
    'create_kasir_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_kasir_report',
        description=f"Submitted kasir daily report",
        related_type='report',
        related_id=report_dict['id'],
        metadata={
            'report_type': 'kasir_daily',
            'total_setoran': report_dict.get('setoran_pagi', 0) + report_dict.get('setoran_siang', 0) + report_dict.get('setoran_sore', 0),
            'total_topup': report_dict.get('total_topup', 0)
        }
    )
    ''',
    
    'update_loket_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_loket_report',
        description=f"Updated loket report shift {existing['shift']}",
        related_type='report',
        related_id=report_id,
        metadata={
            'report_type': 'loket_daily',
            'updated_by': user['full_name']
        }
    )
    ''',
    
    'update_kasir_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_kasir_report',
        description=f"Updated kasir daily report",
        related_type='report',
        related_id=report_id,
        metadata={
            'report_type': 'kasir_daily',
            'updated_by': user['full_name']
        }
    )
    ''',
    
    'delete_loket_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_loket_report',
        description=f"Deleted loket report shift {report['shift']}",
        related_type='report',
        related_id=report_id,
        metadata={
            'report_type': 'loket_daily',
            'deleted_by': user['full_name']
        }
    )
    ''',
    
    'delete_kasir_report': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_kasir_report',
        description=f"Deleted kasir daily report",
        related_type='report',
        related_id=report_id,
        metadata={
            'report_type': 'kasir_daily',
            'deleted_by': user['full_name']
        }
    )
    ''',
    
    # Teknisi Operations
    'update_order_status_teknisi': '''
    await log_activity(
        user_id=current_user['sub'],
        action='teknisi_update_status',
        description=f"Teknisi updated order {order['order_number']} status to {status}",
        related_type='order',
        related_id=order_id,
        metadata={
            'order_number': order['order_number'],
            'new_status': status,
            'teknisi_name': user['full_name'],
            'notes': notes
        }
    )
    ''',
    
    'update_order_progress_teknisi': '''
    await log_activity(
        user_id=current_user['sub'],
        action='teknisi_update_progress',
        description=f"Teknisi updated order {order['order_number']} progress to {progress}%",
        related_type='order',
        related_id=order_id,
        metadata={
            'order_number': order['order_number'],
            'progress': progress,
            'teknisi_name': user['full_name']
        }
    )
    ''',
    
    # Loyalty & CSR Operations
    'create_loyalty_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_loyalty_program',
        description=f"Created loyalty program: {program_dict['name']}",
        related_type='loyalty',
        related_id=program_dict['id'],
        metadata={
            'program_name': program_dict['name'],
            'target_participants': program_dict['target_participants'],
            'budget': program_dict['budget']
        }
    )
    ''',
    
    'update_loyalty_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_loyalty_program',
        description=f"Updated loyalty program: {existing['name']}",
        related_type='loyalty',
        related_id=program_id,
        metadata={'program_name': existing['name']}
    )
    ''',
    
    'delete_loyalty_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_loyalty_program',
        description=f"Deleted loyalty program: {program['name']}",
        related_type='loyalty',
        related_id=program_id,
        metadata={'program_name': program['name']}
    )
    ''',
    
    'create_csr_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='create_csr_program',
        description=f"Created CSR program: {program_dict['name']}",
        related_type='csr',
        related_id=program_dict['id'],
        metadata={
            'program_name': program_dict['name'],
            'category': program_dict['category'],
            'target_beneficiaries': program_dict['target_beneficiaries']
        }
    )
    ''',
    
    'update_csr_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='update_csr_program',
        description=f"Updated CSR program: {existing['name']}",
        related_type='csr',
        related_id=program_id,
        metadata={'program_name': existing['name']}
    )
    ''',
    
    'delete_csr_program': '''
    await log_activity(
        user_id=current_user['sub'],
        action='delete_csr_program',
        description=f"Deleted CSR program: {program['name']}",
        related_type='csr',
        related_id=program_id,
        metadata={'program_name': program['name']}
        )
    ''',
}
