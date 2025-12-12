#!/usr/bin/env python3
"""
GELIS Reconciliation & Verification Testing - Focused Test
"""

import requests
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://accounting-sync-1.preview.emergentagent.com/api"

def login_user(username, password):
    """Login and get token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"identifier": username, "password": password},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(f"Login failed for {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Login error for {username}: {str(e)}")
        return None

def test_reconciliation_endpoints():
    """Test all reconciliation endpoints"""
    print("🔍 Testing GELIS Reconciliation & Verification System")
    print("=" * 60)
    
    # Login as owner
    owner_token = login_user('owner', 'owner123')
    finance_token = login_user('finance', 'finance123')
    loket_token = login_user('loket1', 'loket123')
    
    if not owner_token:
        print("❌ Cannot login as owner - aborting tests")
        return
    
    headers_owner = {"Authorization": f"Bearer {owner_token}"}
    headers_finance = {"Authorization": f"Bearer {finance_token}"} if finance_token else {}
    headers_loket = {"Authorization": f"Bearer {loket_token}"} if loket_token else {}
    
    # Test 1: Verification Summary
    print("\n1. Testing Verification Summary Endpoint")
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/verification/summary",
            params={"start_date": "2024-12-01", "end_date": "2024-12-15"},
            headers=headers_owner,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Owner: Retrieved summary - {data['summary']['total_kasir_reports']} kasir + {data['summary']['total_loket_reports']} loket reports")
            print(f"   Accuracy Rate: {data['verification_status']['accuracy_rate']}%")
        else:
            print(f"❌ Owner: Failed {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Owner: Error - {str(e)}")
    
    # Test with Finance user
    if finance_token:
        try:
            response = requests.get(
                f"{BACKEND_URL}/reports/verification/summary",
                headers=headers_finance,
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Finance: Can access verification summary")
            else:
                print(f"❌ Finance: Failed {response.status_code}")
        except Exception as e:
            print(f"❌ Finance: Error - {str(e)}")
    
    # Test with Loket user (should fail)
    if loket_token:
        try:
            response = requests.get(
                f"{BACKEND_URL}/reports/verification/summary",
                headers=headers_loket,
                timeout=30
            )
            if response.status_code == 403:
                print("✅ Loket: Correctly denied access (403)")
            else:
                print(f"❌ Loket: Expected 403, got {response.status_code}")
        except Exception as e:
            print(f"❌ Loket: Error - {str(e)}")
    
    # Test 2: Kasir Reconciliation
    print("\n2. Testing Kasir Reconciliation Endpoint")
    test_date = "2024-12-10"
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/kasir",
            params={"report_date": test_date},
            headers=headers_owner,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Owner: Kasir reconciliation - {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
        elif response.status_code == 404:
            print(f"✅ Owner: No kasir reports found for {test_date} (404 expected)")
        else:
            print(f"❌ Owner: Failed {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Owner: Error - {str(e)}")
    
    # Test 3: Loket Reconciliation
    print("\n3. Testing Loket Reconciliation Endpoint")
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/loket",
            params={"report_date": test_date},
            headers=headers_owner,
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Owner: Loket reconciliation - {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
            if data['reports']:
                report = data['reports'][0]
                print(f"   First report: {report['status']}, Banks balanced: {report['all_banks_balanced']}")
        elif response.status_code == 404:
            print(f"✅ Owner: No loket reports found for {test_date} (404 expected)")
        else:
            print(f"❌ Owner: Failed {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Owner: Error - {str(e)}")
    
    # Test 4: Edge Cases
    print("\n4. Testing Edge Cases")
    
    # Non-existent date
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/kasir",
            params={"report_date": "2020-01-01"},
            headers=headers_owner,
            timeout=30
        )
        if response.status_code == 404:
            print("✅ Non-existent date: Correctly returns 404")
        else:
            print(f"❌ Non-existent date: Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"❌ Non-existent date: Error - {str(e)}")
    
    # Invalid date format
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/kasir",
            params={"report_date": "invalid-date"},
            headers=headers_owner,
            timeout=30
        )
        if response.status_code in [400, 404]:
            print(f"✅ Invalid date format: Correctly handled ({response.status_code})")
        else:
            print(f"❌ Invalid date format: Unexpected response {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid date format: Error - {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 RECONCILIATION TESTING COMPLETED")

if __name__ == "__main__":
    test_reconciliation_endpoints()