# 🔐 GELIS - Role Permission Reference

> **Developer Guide**: Panduan lengkap untuk implementasi permission check yang benar

---

## ⚠️ CRITICAL RULE: Always Use `role_id`

### ✅ CORRECT - Using role_id
```python
# Backend permission check
user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
if user['role_id'] in [1, 2, 3]:  # ✅ Use role_id (integer)
    # Allow access
```

### ❌ WRONG - Using role name
```python
# JANGAN GUNAKAN INI!
if user['role_name'] == 'Owner':  # ❌ Wrong! Don't use name
    # This is fragile and will break
```

---

## 📊 Role ID Mapping (FIXED - DO NOT CHANGE)

| role_id | Role Name | Constant |
|---------|-----------|----------|
| **1** | Owner | `ROLE_OWNER = 1` |
| **2** | Manager | `ROLE_MANAGER = 2` |
| **3** | Finance | `ROLE_FINANCE = 3` |
| **4** | Customer Service | `ROLE_CS = 4` |
| **5** | Kasir | `ROLE_KASIR = 5` |
| **6** | Loket | `ROLE_LOKET = 6` |
| **7** | Teknisi | `ROLE_TEKNISI = 7` |

---

## 🎯 Permission Matrix (by role_id)

### API Endpoints Permission

#### `/api/businesses` (GET)
```python
allowed_roles = [1, 2, 3, 5, 6]  # Owner, Manager, Finance, Kasir, Loket
```

#### `/api/businesses` (POST/PUT/DELETE)
```python
allowed_roles = [1, 2]  # Owner, Manager
```

#### `/api/users` (GET)
```python
allowed_roles = [1, 2, 8]  # Owner, Manager, IT Developer
```

#### `/api/users/{id}` (PUT)
```python
allowed_roles = [1, 2]  # Owner, Manager
# Special rule: Manager cannot edit Owner (role_id 1)
if user['role_id'] == 2 and target_user['role_id'] == 1:
    raise HTTPException(403)
```

#### `/api/users/{id}` (DELETE)
```python
allowed_roles = [1]  # Owner only
```

#### `/api/accounting` (GET/POST)
```python
allowed_roles = [1, 2, 3]  # Owner, Manager, Finance
```

#### `/api/transactions` (GET)
```python
allowed_roles = [1, 2, 3, 5]  # Owner, Manager, Finance, Kasir
```

#### `/api/orders` (GET/POST)
```python
allowed_roles = [1, 2, 5, 6]  # Owner, Manager, Kasir, Loket
```

#### `/api/reports/*` (GET)
```python
allowed_roles = [1, 2, 3, 5, 6]  # Owner, Manager, Finance, Kasir, Loket
```

#### `/api/teknisi/orders` (GET)
```python
# Special logic:
if user['role_id'] == 7:  # Teknisi
    # Return only jobs assigned to this technician
    filter = {'assigned_to': current_user['sub']}
elif user['role_id'] in [1, 2, 5]:  # Owner, Manager, Kasir
    # Return all technical jobs
    filter = {'requires_technician': True}
```

#### `/api/teknisi/orders/{id}/assign` (PUT)
```python
allowed_roles = [1, 2]  # Owner, Manager
```

---

## 🛠️ Implementation Examples

### Backend (FastAPI)

```python
@api_router.get('/endpoint')
async def get_endpoint(current_user: dict = Depends(get_current_user)):
    # Step 1: Get user from database
    user = await db.users.find_one({'id': current_user['sub']}, {'_id': 0})
    
    # Step 2: Check role_id (NOT role_name!)
    if user['role_id'] not in [1, 2, 3]:  # ✅ Use role_id
        raise HTTPException(status_code=403, detail='Tidak memiliki akses')
    
    # Step 3: Proceed with logic
    # ...
```

### Frontend (React)

```javascript
// Get current user
const currentUser = getUser();

// Check role_id (NOT role_name!)
const isManagerOrOwner = currentUser?.role_id === 1 || currentUser?.role_id === 2;

// Conditional rendering
{isManagerOrOwner && (
  <Button>Admin Only Feature</Button>
)}
```

---

## 📝 Adding New User - Checklist

When adding a new user via UI or API:

```javascript
// ✅ CORRECT
const newUser = {
  username: "budi",
  password: "budi123",
  full_name: "Budi Santoso",
  email: "budi@gelis.com",
  role_id: 7,  // ✅ Must be valid role_id (1-7)
  is_active: true
}

// ❌ WRONG
const newUser = {
  username: "budi",
  password: "budi123",
  full_name: "Budi Santoso",
  email: "budi@gelis.com",
  role_name: "Teknisi",  // ❌ Don't use role_name!
  is_active: true
}
```

**Validation checklist:**
- [ ] `role_id` is integer (1-7)
- [ ] `role_id` exists in roles table
- [ ] `is_active` is boolean
- [ ] `password` is hashed (backend)
- [ ] `email` is unique
- [ ] `username` is unique

---

## 🔍 Testing Permission

### Test with curl:
```bash
# 1. Login as specific role
TOKEN=$(curl -s -X POST "https://your-api.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier":"owner","password":"owner123"}' \
  | jq -r '.access_token')

# 2. Test endpoint
curl -X GET "https://your-api.com/api/users" \
  -H "Authorization: Bearer $TOKEN"
```

### Expected responses:
- ✅ 200: Success (user has permission)
- ❌ 403: Forbidden (user doesn't have permission)
- ❌ 401: Unauthorized (invalid/expired token)

---

## 🚨 Common Mistakes to Avoid

### ❌ Mistake 1: Using role name instead of role_id
```python
# WRONG!
if user['role_name'] == 'Owner':
    # Fragile - breaks if role name changes
```

### ❌ Mistake 2: Hardcoding role names in code
```python
# WRONG!
ADMIN_ROLES = ['Owner', 'Manager']  # String names
```

### ❌ Mistake 3: Not validating role_id when creating user
```python
# WRONG!
new_user = {
    'role_id': request.form['role_id']  # No validation!
}
```

### ❌ Mistake 4: Inconsistent permission checks
```python
# WRONG! Some endpoints use [1, 2], others use [1, 2, 3] for same feature
# Maintain consistency!
```

---

## ✅ Best Practices

1. **Always use `role_id` for permission checks**
2. **Define role constants at the top of your file**
3. **Document which roles can access each endpoint**
4. **Test ALL roles when modifying permissions**
5. **Use comments to explain permission logic**
6. **Keep permission checks consistent across similar endpoints**

---

**Last Updated**: 2025-12-14  
**Verified**: All 6 roles tested & working ✅
