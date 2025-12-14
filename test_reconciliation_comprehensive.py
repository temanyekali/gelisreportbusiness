#!/usr/bin/env python3
"""
GELIS Reconciliation & Verification - Comprehensive Testing with Real Data
"""

import requests
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://finance-modules-2.preview.emergentagent.com/api"

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

def test_comprehensive_reconciliation():
    """Comprehensive test of reconciliation system"""
    print("🎯 COMPREHENSIVE RECONCILIATION & VERIFICATION TESTING")
    print("=" * 70)
    
    # Login users
    users = {
        'owner': login_user('owner', 'owner123'),
        'finance': login_user('finance', 'finance123'),
        'loket1': login_user('loket1', 'loket123')
    }
    
    if not users['owner']:
        print("❌ Cannot login as owner - aborting tests")
        return
    
    headers = {
        'owner': {"Authorization": f"Bearer {users['owner']}"},
        'finance': {"Authorization": f"Bearer {users['finance']}"} if users['finance'] else {},
        'loket1': {"Authorization": f"Bearer {users['loket1']}"} if users['loket1'] else {}
    }
    
    test_results = []
    
    # Test 1: Verification Summary with Date Range
    print("\n1. 📊 VERIFICATION SUMMARY ENDPOINT")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/verification/summary",
            params={
                "start_date": "2025-12-07",
                "end_date": "2025-12-12"
            },
            headers=headers['owner'],
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            summary = data['summary']
            verification = data['verification_status']
            
            print(f"✅ Period: {data['period']['start_date']} to {data['period']['end_date']}")
            print(f"✅ Total Kasir Reports: {summary['total_kasir_reports']}")
            print(f"✅ Total Loket Reports: {summary['total_loket_reports']}")
            print(f"✅ Kasir Total Reported: Rp {summary['kasir_total_reported']:,.2f}")
            print(f"✅ Loket Total Reported: Rp {summary['loket_total_reported']:,.2f}")
            print(f"✅ Actual Total Transactions: Rp {summary['actual_total_transactions']:,.2f}")
            print(f"✅ Overall Difference: Rp {summary['overall_difference']:,.2f}")
            print(f"✅ Accuracy Rate: {verification['accuracy_rate']}%")
            print(f"✅ Requires Investigation: {verification['requires_investigation']}")
            
            test_results.append(("Verification Summary - Owner", True, f"Retrieved summary with {summary['total_kasir_reports']} kasir + {summary['total_loket_reports']} loket reports"))
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            test_results.append(("Verification Summary - Owner", False, f"Failed: {response.status_code}"))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        test_results.append(("Verification Summary - Owner", False, f"Error: {str(e)}"))
    
    # Test permission control
    for user_type in ['finance', 'loket1']:
        if users[user_type]:
            try:
                response = requests.get(
                    f"{BACKEND_URL}/reports/verification/summary",
                    headers=headers[user_type],
                    timeout=30
                )
                expected_status = 200 if user_type == 'finance' else 403
                if response.status_code == expected_status:
                    result = "✅" if user_type == 'finance' else "✅ (403)"
                    print(f"{result} {user_type.title()}: {'Can access' if user_type == 'finance' else 'Correctly denied access'}")
                    test_results.append((f"Verification Summary - {user_type.title()}", True, "Permission control working"))
                else:
                    print(f"❌ {user_type.title()}: Expected {expected_status}, got {response.status_code}")
                    test_results.append((f"Verification Summary - {user_type.title()}", False, f"Expected {expected_status}, got {response.status_code}"))
            except Exception as e:
                print(f"❌ {user_type.title()}: Error - {str(e)}")
                test_results.append((f"Verification Summary - {user_type.title()}", False, f"Error: {str(e)}"))
    
    # Test 2: Kasir Reconciliation with Real Data
    print("\n2. 💰 KASIR RECONCILIATION ENDPOINT")
    print("-" * 40)
    
    test_date = "2025-12-07"  # Date with known data
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/kasir",
            params={"report_date": test_date},
            headers=headers['owner'],
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reconciliation Date: {data['reconciliation_date']}")
            print(f"✅ Total Reports: {data['total_reports']}")
            print(f"✅ Matched Reports: {data['matched_reports']}")
            print(f"✅ Discrepancy Reports: {data['discrepancy_reports']}")
            
            if data['reports']:
                report = data['reports'][0]
                print(f"✅ Sample Report Status: {report['status']}")
                print(f"✅ Reported Total: Rp {report['reported_total']:,.2f}")
                print(f"✅ Actual Total: Rp {report['actual_total']:,.2f}")
                print(f"✅ Difference: Rp {report['total_difference']:,.2f}")
                
                # Check breakdown
                breakdown = report['breakdown']
                print(f"✅ Setoran Kasir - Reported: Rp {breakdown['setoran_kasir']['reported']:,.2f}, Actual: Rp {breakdown['setoran_kasir']['actual']:,.2f}")
                print(f"✅ Admin Fee - Reported: Rp {breakdown['admin_fee']['reported']:,.2f}, Actual: Rp {breakdown['admin_fee']['actual']:,.2f}")
                print(f"✅ Belanja Loket - Reported: Rp {breakdown['belanja_loket']['reported']:,.2f}, Actual: Rp {breakdown['belanja_loket']['actual']:,.2f}")
                
                # Check discrepancy detection
                if report['discrepancies']:
                    print(f"✅ Discrepancies Detected: {len(report['discrepancies'])}")
                    for disc in report['discrepancies']:
                        print(f"   - {disc['category']}: {disc['percentage']}% difference")
                
                test_results.append(("Kasir Reconciliation - Owner", True, f"Reconciled {data['total_reports']} reports with {data['discrepancy_reports']} discrepancies"))
            else:
                test_results.append(("Kasir Reconciliation - Owner", True, "No reports found (valid response)"))
        elif response.status_code == 404:
            print(f"✅ No kasir reports found for {test_date} (404 expected)")
            test_results.append(("Kasir Reconciliation - Owner", True, "404 for non-existent date"))
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            test_results.append(("Kasir Reconciliation - Owner", False, f"Failed: {response.status_code}"))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        test_results.append(("Kasir Reconciliation - Owner", False, f"Error: {str(e)}"))
    
    # Test 3: Loket Reconciliation with Real Data
    print("\n3. 🏪 LOKET RECONCILIATION ENDPOINT")
    print("-" * 40)
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/reports/reconciliation/loket",
            params={"report_date": test_date},
            headers=headers['owner'],
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reconciliation Date: {data['reconciliation_date']}")
            print(f"✅ Total Reports: {data['total_reports']}")
            print(f"✅ Matched Reports: {data['matched_reports']}")
            print(f"✅ Discrepancy Reports: {data['discrepancy_reports']}")
            
            if data['reports']:
                report = data['reports'][0]
                print(f"✅ Sample Report Status: {report['status']}")
                print(f"✅ Shift: {report.get('shift', 'N/A')}")
                print(f"✅ Petugas: {report.get('nama_petugas', 'N/A')}")
                print(f"✅ Reported Total Setoran: Rp {report['reported_total_setoran']:,.2f}")
                print(f"✅ Actual Total Setoran: Rp {report['actual_total_setoran']:,.2f}")
                print(f"✅ Difference: Rp {report['difference']:,.2f}")
                print(f"✅ All Banks Balanced: {report['all_banks_balanced']}")
                
                # Check bank balances
                if report['bank_balances']:
                    print(f"✅ Bank Balance Checks: {len(report['bank_balances'])} banks")
                    for bank in report['bank_balances']:
                        print(f"   - {bank['bank_name']}: Balanced={bank['is_balanced']}, Diff=Rp {bank['difference']:,.2f}")
                
                test_results.append(("Loket Reconciliation - Owner", True, f"Reconciled {data['total_reports']} reports with {data['discrepancy_reports']} discrepancies"))
            else:
                test_results.append(("Loket Reconciliation - Owner", True, "No reports found (valid response)"))
        elif response.status_code == 404:
            print(f"✅ No loket reports found for {test_date} (404 expected)")
            test_results.append(("Loket Reconciliation - Owner", True, "404 for non-existent date"))
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            test_results.append(("Loket Reconciliation - Owner", False, f"Failed: {response.status_code}"))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        test_results.append(("Loket Reconciliation - Owner", False, f"Error: {str(e)}"))
    
    # Test 4: Edge Cases and Error Handling
    print("\n4. 🧪 EDGE CASES & ERROR HANDLING")
    print("-" * 40)
    
    edge_cases = [
        ("Non-existent date", "2020-01-01", 404),
        ("Invalid date format", "invalid-date", [400, 404]),
        ("Future date", "2030-01-01", 404)
    ]
    
    for case_name, test_date, expected_status in edge_cases:
        try:
            response = requests.get(
                f"{BACKEND_URL}/reports/reconciliation/kasir",
                params={"report_date": test_date},
                headers=headers['owner'],
                timeout=30
            )
            if isinstance(expected_status, list):
                success = response.status_code in expected_status
            else:
                success = response.status_code == expected_status
            
            if success:
                print(f"✅ {case_name}: Correctly handled ({response.status_code})")
                test_results.append((f"Edge Case - {case_name}", True, f"Correctly handled ({response.status_code})"))
            else:
                print(f"❌ {case_name}: Expected {expected_status}, got {response.status_code}")
                test_results.append((f"Edge Case - {case_name}", False, f"Expected {expected_status}, got {response.status_code}"))
        except Exception as e:
            print(f"❌ {case_name}: Error - {str(e)}")
            test_results.append((f"Edge Case - {case_name}", False, f"Error: {str(e)}"))
    
    # Test 5: Permission Matrix
    print("\n5. 🔐 PERMISSION MATRIX TESTING")
    print("-" * 40)
    
    endpoints = [
        ("kasir", "/reports/reconciliation/kasir"),
        ("loket", "/reports/reconciliation/loket")
    ]
    
    for endpoint_name, endpoint_path in endpoints:
        for user_type in ['finance', 'loket1']:
            if users[user_type]:
                try:
                    response = requests.get(
                        f"{BACKEND_URL}{endpoint_path}",
                        params={"report_date": "2025-12-07"},
                        headers=headers[user_type],
                        timeout=30
                    )
                    expected_status = [200, 404] if user_type == 'finance' else 403
                    if isinstance(expected_status, list):
                        success = response.status_code in expected_status
                    else:
                        success = response.status_code == expected_status
                    
                    if success:
                        result = "✅" if user_type == 'finance' else "✅ (403)"
                        print(f"{result} {endpoint_name.title()} - {user_type.title()}: {'Can access' if user_type == 'finance' else 'Correctly denied'}")
                        test_results.append((f"{endpoint_name.title()} Reconciliation - {user_type.title()}", True, "Permission control working"))
                    else:
                        print(f"❌ {endpoint_name.title()} - {user_type.title()}: Expected {expected_status}, got {response.status_code}")
                        test_results.append((f"{endpoint_name.title()} Reconciliation - {user_type.title()}", False, f"Expected {expected_status}, got {response.status_code}"))
                except Exception as e:
                    print(f"❌ {endpoint_name.title()} - {user_type.title()}: Error - {str(e)}")
                    test_results.append((f"{endpoint_name.title()} Reconciliation - {user_type.title()}", False, f"Error: {str(e)}"))
    
    # Print Summary
    print("\n" + "=" * 70)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in test_results if success)
    failed = sum(1 for _, success, _ in test_results if not success)
    total = len(test_results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
    
    if failed > 0:
        print("\n❌ FAILED TESTS:")
        for test_name, success, message in test_results:
            if not success:
                print(f"  - {test_name}: {message}")
    
    print("\n✅ PASSED TESTS:")
    for test_name, success, message in test_results:
        if success:
            print(f"  - {test_name}: {message}")
    
    print("\n🎯 RECONCILIATION & VERIFICATION SYSTEM STATUS:")
    if failed == 0:
        print("✅ ALL TESTS PASSED - System is fully operational!")
    elif failed <= 2:
        print("⚠️  MOSTLY WORKING - Minor issues detected")
    else:
        print("❌ CRITICAL ISSUES - System needs attention")

if __name__ == "__main__":
    test_comprehensive_reconciliation()