#!/usr/bin/env python3
"""
Check what dates have reports in the system
"""

import requests
import json
from datetime import datetime

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

def check_report_dates():
    """Check what dates have reports"""
    print("📅 Checking Report Dates in System")
    print("=" * 50)
    
    # Login as owner
    owner_token = login_user('owner', 'owner123')
    if not owner_token:
        print("❌ Cannot login as owner")
        return
    
    headers = {"Authorization": f"Bearer {owner_token}"}
    
    # Get kasir reports
    try:
        response = requests.get(f"{BACKEND_URL}/reports/kasir-daily", headers=headers, timeout=30)
        if response.status_code == 200:
            kasir_reports = response.json()
            print(f"📊 Found {len(kasir_reports)} kasir reports")
            if kasir_reports:
                dates = set()
                for report in kasir_reports[:10]:  # Show first 10
                    date = report['report_date'][:10] if isinstance(report['report_date'], str) else str(report['report_date'])[:10]
                    dates.add(date)
                    print(f"   Kasir Report: {date} - Business: {report.get('business_id', 'N/A')}")
                print(f"   Unique dates: {sorted(dates)}")
        else:
            print(f"❌ Failed to get kasir reports: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting kasir reports: {str(e)}")
    
    # Get loket reports
    try:
        response = requests.get(f"{BACKEND_URL}/reports/loket-daily", headers=headers, timeout=30)
        if response.status_code == 200:
            loket_reports = response.json()
            print(f"\n📊 Found {len(loket_reports)} loket reports")
            if loket_reports:
                dates = set()
                for report in loket_reports[:10]:  # Show first 10
                    date = report['report_date'][:10] if isinstance(report['report_date'], str) else str(report['report_date'])[:10]
                    dates.add(date)
                    print(f"   Loket Report: {date} - Business: {report.get('business_id', 'N/A')} - Shift: {report.get('shift', 'N/A')}")
                print(f"   Unique dates: {sorted(dates)}")
                
                # Test reconciliation with first available date
                if dates:
                    test_date = sorted(dates)[0]
                    print(f"\n🔍 Testing reconciliation with date: {test_date}")
                    
                    # Test kasir reconciliation
                    try:
                        response = requests.get(
                            f"{BACKEND_URL}/reports/reconciliation/kasir",
                            params={"report_date": test_date},
                            headers=headers,
                            timeout=30
                        )
                        if response.status_code == 200:
                            data = response.json()
                            print(f"✅ Kasir Reconciliation: {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
                        elif response.status_code == 404:
                            print(f"ℹ️  No kasir reports for {test_date}")
                        else:
                            print(f"❌ Kasir reconciliation failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Kasir reconciliation error: {str(e)}")
                    
                    # Test loket reconciliation
                    try:
                        response = requests.get(
                            f"{BACKEND_URL}/reports/reconciliation/loket",
                            params={"report_date": test_date},
                            headers=headers,
                            timeout=30
                        )
                        if response.status_code == 200:
                            data = response.json()
                            print(f"✅ Loket Reconciliation: {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
                            if data['reports']:
                                report = data['reports'][0]
                                print(f"   Sample Report Status: {report['status']}")
                                print(f"   Banks Balanced: {report['all_banks_balanced']}")
                                print(f"   Reported Total: {report['reported_total_setoran']}")
                                print(f"   Actual Total: {report['actual_total_setoran']}")
                        elif response.status_code == 404:
                            print(f"ℹ️  No loket reports for {test_date}")
                        else:
                            print(f"❌ Loket reconciliation failed: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Loket reconciliation error: {str(e)}")
        else:
            print(f"❌ Failed to get loket reports: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting loket reports: {str(e)}")

if __name__ == "__main__":
    check_report_dates()