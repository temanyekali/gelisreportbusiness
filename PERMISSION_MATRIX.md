# 🔐 GELIS Permission Matrix - Complete Documentation

**Version**: 3.1  
**Last Updated**: December 11, 2024  
**Status**: ✅ Production Ready

---

## 📋 Complete Permission Matrix

| Menu / Feature | Owner (1) | Manager (2) | Finance (3) | Kasir (5) | Loket (6) | Teknisi (7) |
|----------------|-----------|-------------|-------------|-----------|-----------|-------------|
| **Dashboard** | ✅ View | ✅ View | ✅ View | ✅ View | ✅ View | ✅ View |
| **Businesses** | ✅ CRUD | ✅ CRU | ❌ | ❌ | ❌ | ❌ |
| **Orders** | ✅ CRUD | ✅ CRU | ❌ | ✅ CRU | ✅ CRU | ❌ |
| **Teknisi Jobs** | ✅ View All | ✅ View All | ❌ | ✅ View All | ❌ | ✅ Assigned Only |
| **Accounting** | ✅ CRUD | ✅ CRU | ✅ CRU | ❌ | ❌ | ❌ |
| **Users** | ✅ CRUD | ✅ View/Edit | ❌ | ❌ | ❌ | ❌ |
| **Reports** | ✅ CRUD | ✅ CRU | ✅ View | ✅ Create Own | ✅ Create Own | ❌ |
| **Loyalty** | ✅ CRUD | ✅ CRU | ❌ | ❌ | ❌ | ❌ |
| **CSR** | ✅ CRUD | ✅ CRU | ❌ | ❌ | ❌ | ❌ |
| **Activity Logs** | ✅ View | ✅ View | ❌ | ❌ | ❌ | ❌ |
| **Settings** | ✅ CRUD | ❌ | ❌ | ❌ | ❌ | ❌ |

**Legend**:
- ✅ = Has Access
- ❌ = No Access
- CRUD = Create, Read, Update, Delete
- CRU = Create, Read, Update (No Delete)

---

## 👤 Role Descriptions

### 1. Owner (role_id: 1)
**Full System Access + DELETE Permission**

✅ **Can Access**:
- ALL menus and features
- Create, View, Edit, DELETE all data
- User management
- System settings
- Activity logs
- Financial data

❌ **Restrictions**:
- Cannot delete own account
- Activity logged for all critical actions

**Use Case**: System administrator, business owner

---

### 2. Manager (role_id: 2)
**Full Operational Access - NO DELETE**

✅ **Can Access**:
- ALL menus except Settings
- Create, View, Edit data
- Assign tasks to technicians
- Manage operations
- View activity logs
- Financial oversight

❌ **Cannot**:
- Delete any data
- Modify system settings
- Delete users

**Use Case**: Operations manager, branch manager

---

### 3. Finance (role_id: 3)
**Financial & Reporting Focus**

✅ **Can Access**:
- Dashboard (overview)
- Accounting (view, edit, create manual entries)
- All Reports (Loket & Kasir - view all)

✅ **Can Do**:
- View all financial transactions
- Edit transaction details
- Create manual transaction entries
- View all daily reports
- Generate financial summaries

❌ **Cannot Access**:
- Businesses management
- Orders management
- Teknisi operations
- User management
- Loyalty/CSR programs
- Delete transactions (Owner only)

**Use Case**: Finance staff, accountant, auditor

---

### 4. Kasir (role_id: 5)
**Cashier Operations**

✅ **Can Access**:
- Dashboard
- Orders (create, view, edit)
- Teknisi Jobs (view all, for coordination)
- Reports (create Kasir report, view own)

✅ **Can Do**:
- Process customer orders
- Update payment status
- Create daily cash reports
- View teknisi job status
- Coordinate with field staff

❌ **Cannot Access**:
- Businesses settings
- Accounting (auto-creates only)
- User management
- Loyalty/CSR
- Delete any data

**Use Case**: Cashier, front desk staff

---

### 5. Loket (role_id: 6)
**Counter Service Staff**

✅ **Can Access**:
- Dashboard
- Orders (create, view, edit)
- Reports (create Loket report, view own)

✅ **Can Do**:
- Process counter transactions
- Create customer orders
- Submit daily counter reports
- View order history

❌ **Cannot Access**:
- Teknisi jobs
- Accounting
- Businesses management
- User management
- Delete any data

**Use Case**: Counter service staff, service window operator

---

### 6. Teknisi (role_id: 7)
**Field Technician - Minimal Access**

✅ **Can Access**:
- Dashboard (limited view)
- Teknisi Jobs (ONLY assigned orders)

✅ **Can Do**:
- View assigned work orders
- Update job status (pending → processing → completed)
- Update progress percentage (0-100%)
- Add work notes
- View customer contact info

❌ **Cannot Access**:
- All orders (only assigned)
- Businesses
- Accounting
- Reports
- User management
- Any other menu

**Use Case**: Field technician, installer, service engineer

---

## 🚫 DELETE Permission Matrix

**ONLY Owner can DELETE**:
- ✅ Businesses
- ✅ Orders
- ✅ Transactions
- ✅ Users
- ✅ Reports
- ✅ Loyalty Programs
- ✅ CSR Programs

**Everyone else**: ❌ NO DELETE permission

**Reason**: Data integrity, audit trail, prevent accidental loss

---

## 📊 Special Cases & Rules

### Auto-Transaction Creation
**All roles that can create reports/orders** → Auto-creates transactions

| Action | Auto-Transaction | Created By |
|--------|------------------|------------|
| Order Payment | Income | System (any role) |
| Loket Report | Income (Setoran) | System (Loket/Owner/Manager) |
| Kasir Report | Multiple (Income/Expense) | System (Kasir/Owner/Manager) |

**Permission**: Auto-transactions inherit creator's user_id but bypass accounting permission

---

### Report Creation Rules

| Report Type | Can Create | Can View | Can Edit | Can Delete |
|-------------|-----------|----------|----------|------------|
| **Loket Daily** | Owner, Manager, Loket | Finance + Creators | Owner, Manager | Owner |
| **Kasir Daily** | Owner, Manager, Kasir | Finance + Creators | Owner, Manager | Owner |

**Special**: Finance can view ALL reports but cannot create or edit

---

### Teknisi Job Assignment

| Role | View Jobs | Assign Jobs | Update Status | Update Progress |
|------|-----------|-------------|---------------|-----------------|
| Owner | All jobs | ✅ | ✅ | ✅ |
| Manager | All jobs | ✅ | ✅ | ✅ |
| Kasir | All jobs | ❌ | ❌ | ❌ |
| Teknisi | Assigned only | ❌ | ✅ (own) | ✅ (own) |

---

## 🔧 Implementation Details

### Backend Permission Checks

```python
# Example permission check
user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})

# Owner, Manager, Finance only
if user['role_id'] not in [1, 2, 3]:
    raise HTTPException(status_code=403, detail='Tidak memiliki akses')

# Delete: Owner only
if user['role_id'] != 1:
    raise HTTPException(status_code=403, detail='Hanya Owner yang dapat menghapus')
```

### Frontend Menu Visibility

```javascript
// In Layout.js
const navItems = [
  { path: '/businesses', role: [1, 2] },  // Owner, Manager
  { path: '/accounting', role: [1, 2, 3] },  // Owner, Manager, Finance
  { path: '/teknisi', role: [1, 2, 5, 7] },  // Owner, Manager, Kasir, Teknisi
  // ... etc
]
```

---

## 🧪 Testing Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Owner | owner | owner123 | Full + DELETE |
| Manager | manager | manager123 | Full - DELETE |
| Finance | finance | finance123 | Finance only |
| Kasir | kasir1 | kasir123 | Cashier ops |
| Loket | loket1 | loket123 | Counter ops |
| Teknisi | teknisi1 | teknisi123 | Field jobs only |

---

## 📝 Activity Logging

**All critical actions logged**:
- ✅ User login/logout
- ✅ Data creation
- ✅ Data updates
- ✅ Data deletion (with full details)
- ✅ Permission denials
- ✅ Payment processing
- ✅ Report submissions

**Log includes**:
- User ID
- Action type
- Description
- Timestamp
- IP address

---

## 🔒 Security Features

1. **Role-Based Access Control (RBAC)**
   - Enforced at API level
   - Frontend visibility control
   - Cannot bypass with direct URLs

2. **Permission Inheritance**
   - Owner > Manager > Others
   - Clear hierarchy
   - No permission escalation

3. **Audit Trail**
   - All actions logged
   - Cannot delete logs
   - Owner can view all logs

4. **Data Integrity**
   - Foreign key consistency
   - Cascade prevention on delete
   - Reference tracking

---

## ⚠️ Important Notes

1. **Owner Cannot Delete Self**
   - Prevents system lockout
   - Must create another owner first

2. **Manager Limitations**
   - Can manage operations
   - Cannot delete data
   - Cannot change system settings

3. **Finance Read-Only Operations**
   - Full visibility on finances
   - Cannot manage operations
   - Audit & reporting focused

4. **Field Staff Isolation**
   - Teknisi: Only assigned jobs
   - Prevents data leakage
   - Focus on work execution

---

## 🚀 Migration & Rollout

**Safe to deploy**: ✅ All permissions tested

**Steps**:
1. Backup current database
2. Deploy new code
3. Test with each role
4. Monitor activity logs
5. Verify no unauthorized access

**Rollback**: Previous version had looser permissions

---

## 📞 Support

For permission issues:
1. Check role assignment in Users menu
2. Verify in activity logs
3. Contact system administrator
4. Review this documentation

---

**Version History**:
- v3.1: Strict permission matrix implemented
- v3.0: Auto-transaction + auditing
- v2.0: Basic RBAC
- v1.0: Initial release

✅ **Current Status**: Production Ready
