# 🔐 Update Credentials & Roles - GELIS

## 🎯 Perubahan yang Dilakukan

### 1. ✅ Owner Credentials Updated
**Previous:**
- Username: `owner`
- Password: `owner123`
- Full Name: "Pak Budi Santoso (Owner)"

**Current:**
- Username: `edy`
- Password: `edy123`
- Full Name: "Edy (Owner)"
- Email: `edy@gelis.com`
- Role ID: 1

---

### 2. ✅ IT Developer Role Added
**New Role Added: IT Developer (Role ID: 8)**

**Credentials:**
- Username: `indra`
- Password: `indra123`
- Full Name: "Indra (IT Developer)"
- Email: `indra@gelis.com`
- Role ID: 8

**Access Level:**
- ✅ **Setara dengan Owner** (Full Access)
- ✅ Dapat manage semua users
- ✅ Akses Financial Dashboard
- ✅ Akses Reconciliation & Verification
- ✅ Akses semua business data
- ✅ Maintenance & troubleshooting capabilities

---

### 3. ✅ Permission Updates

**Endpoints dengan IT Developer Access:**
- `/api/users` - View all users
- `/api/financial/dashboard` - Financial dashboard
- `/api/accounting/summary` - Accounting summary
- `/api/reports/reconciliation/kasir` - Kasir reconciliation
- `/api/reports/reconciliation/loket` - Loket reconciliation
- `/api/reports/verification/summary` - Verification summary
- `/api/businesses` - Business management
- All other Owner-level endpoints

**Permission Matrix:**

| Endpoint | Owner (1) | IT Dev (8) | Manager (2) | Finance (3) | Loket/Kasir |
|----------|-----------|------------|-------------|-------------|-------------|
| User Management | ✅ | ✅ | ❌ | ❌ | ❌ |
| Financial Dashboard | ✅ | ✅ | ✅ | ✅ | ❌ |
| Reconciliation | ✅ | ✅ | ✅ | ✅ | ❌ |
| Business Management | ✅ | ✅ | ✅ | ❌ | ❌ |
| Orders | ✅ | ✅ | ✅ | ✅ | ✅ |
| Reports View | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔑 All Login Credentials

### **Administrative Users:**

**Owner:**
```
Username: edy
Password: edy123
Access: Full (Owner Level)
```

**IT Developer:**
```
Username: indra
Password: indra123
Access: Full (Owner Level)
```

---

### **Staff Users (Mock Data):**

**Manager:**
```
Username: manager
Password: manager123
Access: Business Management, Reports, Orders
```

**Finance:**
```
Username: finance
Password: finance123
Access: Financial Dashboard, Accounting, Reports
```

**Kasir:**
```
Username: kasir1, kasir2, kasir3
Password: kasir123 (all)
Access: Orders, Kasir Reports
```

**Loket:**
```
Username: loket1, loket2, loket3
Password: loket123 (all)
Access: Orders, Loket Reports
```

**Teknisi:**
```
Username: teknisi1, teknisi2, teknisi3, teknisi4
Password: teknisi123 (all)
Access: Order Updates, Field Work
```

---

## 📊 Role Hierarchy

```
Level 1 (Full Access):
├── Owner (Role ID: 1) - Edy
└── IT Developer (Role ID: 8) - Indra

Level 2 (Management):
├── Manager (Role ID: 2)
└── Finance (Role ID: 3)

Level 3 (Operations):
├── Customer Service (Role ID: 4)
├── Kasir (Role ID: 5)
└── Loket (Role ID: 6)

Level 4 (Field):
└── Teknisi (Role ID: 7)
```

---

## 🛠️ IT Developer Use Cases

### **1. Application Maintenance**
- Debug production issues
- Monitor system performance
- Check database integrity
- Review error logs

### **2. User Management**
- Create/update/delete users
- Reset passwords
- Manage roles & permissions
- Investigate user issues

### **3. Financial Audit**
- Deep dive into transactions
- Verify reconciliation accuracy
- Export financial data
- Generate custom reports

### **4. System Configuration**
- Update application settings
- Manage business configurations
- Adjust system parameters
- Deploy updates

---

## 🔒 Security Notes

### **Password Policy:**
- Minimum 6 characters (current setup)
- **Recommendation**: Change to 12+ characters in production
- Enable 2FA for Owner & IT Developer accounts
- Regular password rotation (every 90 days)

### **Access Control:**
- IT Developer has same privileges as Owner
- Both roles should have audit logging enabled
- Monitor all administrative actions
- Review access logs regularly

### **Best Practices:**
1. Change default passwords immediately in production
2. Use strong, unique passwords
3. Enable session timeout (currently: 30 days)
4. Implement IP whitelisting for Owner/IT Developer if possible
5. Regular security audits

---

## 🧪 Testing IT Developer Access

### Test Full Access:
```bash
# Login as IT Developer
curl -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"identifier":"indra","password":"indra123"}'

# Get token from response, then test endpoints:
curl -X GET "$API_URL/api/users" \
  -H "Authorization: Bearer $TOKEN"

curl -X GET "$API_URL/api/financial/dashboard" \
  -H "Authorization: Bearer $TOKEN"

curl -X GET "$API_URL/api/reports/verification/summary" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📝 Changes Summary

### Files Modified:
1. `/app/backend/models.py` - Added IT_DEVELOPER to RoleEnum
2. `/app/backend/server.py` - Updated permissions to include role_id 8
3. `/app/scripts/seed_complete_mockup.py` - Updated owner name & added IT Developer

### Database Changes:
- **Roles:** 7 → 8 (Added IT Developer)
- **Users:** 14 → 15 (Added Indra)
- **Owner Name:** Changed to "Edy"
- **Permissions:** IT Developer has full access

### Testing Results:
- ✅ Edy (Owner) login successful
- ✅ Indra (IT Developer) login successful
- ✅ IT Developer can access all owner-level endpoints
- ✅ Businesses: 5 found
- ✅ Orders: 346 found
- ✅ Financial Dashboard working
- ✅ All mock data loaded successfully

---

## 🚀 Deployment Notes

**Kubernetes Environment Variables:**
- No changes needed for MONGO_URL or DB_NAME
- SECRET_KEY remains the same
- CORS_ORIGINS unchanged

**Production Checklist:**
- [ ] Change Edy's password from `edy123`
- [ ] Change Indra's password from `indra123`
- [ ] Enable 2FA for both accounts
- [ ] Set up audit logging for admin actions
- [ ] Configure session timeout
- [ ] Review and update permission matrix if needed

---

**Last Updated:** 12 Desember 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
