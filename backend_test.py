#!/usr/bin/env python3
"""
GELIS Backend API Testing Suite - Phase 1-2
Tests authentication, reports module, teknisi module, and permissions
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://responsive-design-52.preview.emergentagent.com/api"

class GelisAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tokens = {}
        self.test_results = []
        self.users = {
            'owner': {'username': 'owner', 'password': 'owner123'},
            'manager': {'username': 'manager', 'password': 'manager123'},
            'loket1': {'username': 'loket1', 'password': 'loket123'},
            'kasir1': {'username': 'kasir1', 'password': 'kasir123'},
            'teknisi1': {'username': 'teknisi1', 'password': 'teknisi123'}
        }
        self.test_data = {}
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details or {}
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def login_user(self, user_type):
        """Login and get token for user"""
        try:
            user_creds = self.users[user_type]
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "identifier": user_creds['username'],
                    "password": user_creds['password']
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.tokens[user_type] = data['access_token']
                self.log_result(f"Login {user_type}", True, f"Successfully logged in as {user_type}")
                return True
            else:
                self.log_result(f"Login {user_type}", False, f"Login failed: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(f"Login {user_type}", False, f"Login error: {str(e)}")
            return False
    
    def get_headers(self, user_type):
        """Get authorization headers for user"""
        if user_type not in self.tokens:
            return {}
        return {"Authorization": f"Bearer {self.tokens[user_type]}"}
    
    def test_authentication(self):
        """Test authentication for all user types"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        for user_type in self.users.keys():
            self.login_user(user_type)
    
    def test_reports_get_endpoints(self):
        """Test GET endpoints for reports"""
        print("\n=== TESTING REPORTS GET ENDPOINTS ===")
        
        # Test with owner login
        headers = self.get_headers('owner')
        
        # Test GET loket reports
        try:
            response = requests.get(f"{self.base_url}/reports/loket-daily", headers=headers, timeout=30)
            if response.status_code == 200:
                loket_reports = response.json()
                self.test_data['loket_reports'] = loket_reports
                self.log_result("GET Loket Reports", True, f"Retrieved {len(loket_reports)} loket reports")
            else:
                self.log_result("GET Loket Reports", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Loket Reports", False, f"Error: {str(e)}")
        
        # Test GET kasir reports
        try:
            response = requests.get(f"{self.base_url}/reports/kasir-daily", headers=headers, timeout=30)
            if response.status_code == 200:
                kasir_reports = response.json()
                self.test_data['kasir_reports'] = kasir_reports
                self.log_result("GET Kasir Reports", True, f"Retrieved {len(kasir_reports)} kasir reports")
            else:
                self.log_result("GET Kasir Reports", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Kasir Reports", False, f"Error: {str(e)}")
    
    def test_edit_loket_report_permissions(self):
        """Test EDIT Loket Report with different user permissions"""
        print("\n=== TESTING EDIT LOKET REPORT PERMISSIONS ===")
        
        # Get a report ID to test with
        if 'loket_reports' not in self.test_data or not self.test_data['loket_reports']:
            self.log_result("Edit Loket Report Setup", False, "No loket reports available for testing")
            return
        
        report_id = self.test_data['loket_reports'][0]['id']
        test_data = {
            "business_id": self.test_data['loket_reports'][0]['business_id'],
            "report_date": "2024-01-15",
            "nama_petugas": "Test Petugas",
            "shift": 1,
            "bank_balances": [
                {
                    "bank_name": "BRIS",
                    "saldo_awal": 1000000,
                    "saldo_inject": 0,
                    "data_lunas": 500000,
                    "setor_kasir": 0,
                    "transfer_amount": 0,
                    "sisa_setoran": 500000,
                    "saldo_akhir": 1500000,
                    "uang_lebih": 0
                }
            ],
            "total_setoran_shift": 500000,
            "notes": "Test edit report"
        }
        
        # Test with Manager login - should succeed
        headers = self.get_headers('manager')
        try:
            response = requests.put(
                f"{self.base_url}/reports/loket-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Edit Loket Report - Manager", True, "Manager successfully edited loket report")
            else:
                self.log_result("Edit Loket Report - Manager", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Loket Report - Manager", False, f"Error: {str(e)}")
        
        # Test with Owner login - should succeed
        headers = self.get_headers('owner')
        try:
            response = requests.put(
                f"{self.base_url}/reports/loket-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Edit Loket Report - Owner", True, "Owner successfully edited loket report")
            else:
                self.log_result("Edit Loket Report - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Loket Report - Owner", False, f"Error: {str(e)}")
        
        # Test with Loket login - should fail (403)
        headers = self.get_headers('loket1')
        try:
            response = requests.put(
                f"{self.base_url}/reports/loket-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Edit Loket Report - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("Edit Loket Report - Loket (403)", False, f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Loket Report - Loket (403)", False, f"Error: {str(e)}")
    
    def test_edit_kasir_report_permissions(self):
        """Test EDIT Kasir Report with different user permissions"""
        print("\n=== TESTING EDIT KASIR REPORT PERMISSIONS ===")
        
        # Get a report ID to test with
        if 'kasir_reports' not in self.test_data or not self.test_data['kasir_reports']:
            self.log_result("Edit Kasir Report Setup", False, "No kasir reports available for testing")
            return
        
        report_id = self.test_data['kasir_reports'][0]['id']
        test_data = {
            "business_id": self.test_data['kasir_reports'][0]['business_id'],
            "report_date": "2024-01-15",
            "setoran_pagi": 200000,
            "setoran_siang": 300000,
            "setoran_sore": 150000,
            "setoran_deposit_loket_luar": 0,
            "setoran_pelunasan_pagi": 0,
            "setoran_pelunasan_siang": 0,
            "topup_transactions": [],
            "total_topup": 0,
            "penerimaan_kas_kecil": 0,
            "pengurangan_kas_kecil": 50000,
            "belanja_loket": 25000,
            "total_kas_kecil": 0,
            "penerimaan_admin": 13000,
            "total_admin": 13000,
            "saldo_bank": 0,
            "saldo_brankas": 13000,
            "notes": "Test edit kasir report"
        }
        
        # Test with Manager login - should succeed
        headers = self.get_headers('manager')
        try:
            response = requests.put(
                f"{self.base_url}/reports/kasir-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Edit Kasir Report - Manager", True, "Manager successfully edited kasir report")
            else:
                self.log_result("Edit Kasir Report - Manager", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Kasir Report - Manager", False, f"Error: {str(e)}")
        
        # Test with Owner login - should succeed
        headers = self.get_headers('owner')
        try:
            response = requests.put(
                f"{self.base_url}/reports/kasir-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Edit Kasir Report - Owner", True, "Owner successfully edited kasir report")
            else:
                self.log_result("Edit Kasir Report - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Kasir Report - Owner", False, f"Error: {str(e)}")
        
        # Test with Kasir login - should fail (403)
        headers = self.get_headers('kasir1')
        try:
            response = requests.put(
                f"{self.base_url}/reports/kasir-daily/{report_id}",
                json=test_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Edit Kasir Report - Kasir (403)", True, "Kasir correctly denied access (403)")
            else:
                self.log_result("Edit Kasir Report - Kasir (403)", False, f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Edit Kasir Report - Kasir (403)", False, f"Error: {str(e)}")
    
    def test_delete_report_permissions(self):
        """Test DELETE Report permissions"""
        print("\n=== TESTING DELETE REPORT PERMISSIONS ===")
        
        # Get report IDs to test with
        if 'loket_reports' not in self.test_data or not self.test_data['loket_reports']:
            self.log_result("Delete Report Setup", False, "No reports available for testing")
            return
        
        # Use the last report for deletion test
        report_id = self.test_data['loket_reports'][-1]['id'] if len(self.test_data['loket_reports']) > 1 else self.test_data['loket_reports'][0]['id']
        
        # Test with Manager login - should fail (403 - only owner can delete)
        headers = self.get_headers('manager')
        try:
            response = requests.delete(
                f"{self.base_url}/reports/loket-daily/{report_id}",
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Delete Report - Manager (403)", True, "Manager correctly denied delete access (403)")
            else:
                self.log_result("Delete Report - Manager (403)", False, f"Expected 403, got {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Delete Report - Manager (403)", False, f"Error: {str(e)}")
        
        # Test with Owner login - should succeed
        headers = self.get_headers('owner')
        try:
            response = requests.delete(
                f"{self.base_url}/reports/loket-daily/{report_id}",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Delete Report - Owner", True, "Owner successfully deleted report")
            else:
                self.log_result("Delete Report - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Delete Report - Owner", False, f"Error: {str(e)}")
    
    def test_teknisi_orders_endpoint(self):
        """Test Teknisi Orders endpoint with different user roles"""
        print("\n=== TESTING TEKNISI ORDERS ENDPOINT ===")
        
        # Test with Teknisi login - should return only assigned orders
        headers = self.get_headers('teknisi1')
        try:
            response = requests.get(f"{self.base_url}/teknisi/orders", headers=headers, timeout=30)
            if response.status_code == 200:
                teknisi_orders = response.json()
                self.test_data['teknisi_orders'] = teknisi_orders
                self.log_result("GET Teknisi Orders - Teknisi", True, f"Teknisi retrieved {len(teknisi_orders)} assigned orders")
            else:
                self.log_result("GET Teknisi Orders - Teknisi", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Teknisi Orders - Teknisi", False, f"Error: {str(e)}")
        
        # Test with Manager login - should return all orders
        headers = self.get_headers('manager')
        try:
            response = requests.get(f"{self.base_url}/teknisi/orders", headers=headers, timeout=30)
            if response.status_code == 200:
                manager_orders = response.json()
                self.log_result("GET Teknisi Orders - Manager", True, f"Manager retrieved {len(manager_orders)} total orders")
            else:
                self.log_result("GET Teknisi Orders - Manager", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Teknisi Orders - Manager", False, f"Error: {str(e)}")
        
        # Test with Owner login - should return all orders
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/teknisi/orders", headers=headers, timeout=30)
            if response.status_code == 200:
                owner_orders = response.json()
                self.log_result("GET Teknisi Orders - Owner", True, f"Owner retrieved {len(owner_orders)} total orders")
            else:
                self.log_result("GET Teknisi Orders - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Teknisi Orders - Owner", False, f"Error: {str(e)}")
    
    def test_teknisi_update_status(self):
        """Test teknisi update order status"""
        print("\n=== TESTING TEKNISI UPDATE ORDER STATUS ===")
        
        # Get orders to test with
        if 'teknisi_orders' not in self.test_data or not self.test_data['teknisi_orders']:
            # Try to get orders from regular orders endpoint
            headers = self.get_headers('owner')
            try:
                response = requests.get(f"{self.base_url}/orders", headers=headers, timeout=30)
                if response.status_code == 200:
                    orders = response.json()
                    if orders:
                        self.test_data['teknisi_orders'] = orders[:1]  # Use first order
                    else:
                        self.log_result("Update Status Setup", False, "No orders available for testing")
                        return
                else:
                    self.log_result("Update Status Setup", False, "Could not retrieve orders for testing")
                    return
            except Exception as e:
                self.log_result("Update Status Setup", False, f"Error getting orders: {str(e)}")
                return
        
        if not self.test_data['teknisi_orders']:
            self.log_result("Update Status Setup", False, "No orders available for testing")
            return
        
        order_id = self.test_data['teknisi_orders'][0]['id']
        
        # Test update status to "processing"
        headers = self.get_headers('teknisi1')
        try:
            response = requests.put(
                f"{self.base_url}/teknisi/orders/{order_id}/status",
                params={"status": "processing", "notes": "Started working on order"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Update Order Status - Processing", True, "Successfully updated status to processing")
            else:
                self.log_result("Update Order Status - Processing", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update Order Status - Processing", False, f"Error: {str(e)}")
        
        # Test update status to "completed"
        try:
            response = requests.put(
                f"{self.base_url}/teknisi/orders/{order_id}/status",
                params={"status": "completed", "notes": "Order completed successfully"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Update Order Status - Completed", True, "Successfully updated status to completed")
            else:
                self.log_result("Update Order Status - Completed", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update Order Status - Completed", False, f"Error: {str(e)}")
    
    def test_teknisi_update_progress(self):
        """Test teknisi update order progress"""
        print("\n=== TESTING TEKNISI UPDATE ORDER PROGRESS ===")
        
        if 'teknisi_orders' not in self.test_data or not self.test_data['teknisi_orders']:
            self.log_result("Update Progress Setup", False, "No orders available for testing")
            return
        
        order_id = self.test_data['teknisi_orders'][0]['id']
        headers = self.get_headers('teknisi1')
        
        # Test update progress to 50%
        try:
            response = requests.put(
                f"{self.base_url}/teknisi/orders/{order_id}/progress",
                params={"progress": 50, "notes": "Work in progress - 50% complete"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Update Order Progress - 50%", True, "Successfully updated progress to 50%")
            else:
                self.log_result("Update Order Progress - 50%", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update Order Progress - 50%", False, f"Error: {str(e)}")
        
        # Test update progress to 100%
        try:
            response = requests.put(
                f"{self.base_url}/teknisi/orders/{order_id}/progress",
                params={"progress": 100, "notes": "Work completed - 100%"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("Update Order Progress - 100%", True, "Successfully updated progress to 100%")
            else:
                self.log_result("Update Order Progress - 100%", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update Order Progress - 100%", False, f"Error: {str(e)}")
    
    def test_auto_generate_reports(self):
        """Test auto-generate report endpoints"""
        print("\n=== TESTING AUTO-GENERATE REPORTS ===")
        
        # Get business ID for testing
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/businesses", headers=headers, timeout=30)
            if response.status_code == 200:
                businesses = response.json()
                if businesses:
                    business_id = businesses[0]['id']
                else:
                    self.log_result("Auto-Generate Setup", False, "No businesses available for testing")
                    return
            else:
                self.log_result("Auto-Generate Setup", False, "Could not retrieve businesses")
                return
        except Exception as e:
            self.log_result("Auto-Generate Setup", False, f"Error getting businesses: {str(e)}")
            return
        
        # Test auto-generate loket report
        try:
            response = requests.post(
                f"{self.base_url}/reports/generate-loket",
                params={
                    "business_id": business_id,
                    "report_date": "2024-01-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                loket_data = response.json()
                self.log_result("Auto-Generate Loket Report", True, "Successfully generated loket report data")
            else:
                self.log_result("Auto-Generate Loket Report", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Auto-Generate Loket Report", False, f"Error: {str(e)}")
        
        # Test auto-generate kasir report
        try:
            response = requests.post(
                f"{self.base_url}/reports/generate-kasir",
                params={
                    "business_id": business_id,
                    "report_date": "2024-01-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                kasir_data = response.json()
                self.log_result("Auto-Generate Kasir Report", True, "Successfully generated kasir report data")
            else:
                self.log_result("Auto-Generate Kasir Report", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Auto-Generate Kasir Report", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting GELIS Backend API Testing Suite - Phase 1-2")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_authentication()
        self.test_reports_get_endpoints()
        self.test_edit_loket_report_permissions()
        self.test_edit_kasir_report_permissions()
        self.test_delete_report_permissions()
        self.test_teknisi_orders_endpoint()
        self.test_teknisi_update_status()
        self.test_teknisi_update_progress()
        self.test_auto_generate_reports()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if "✅ PASS" in r['status'])
        failed = sum(1 for r in self.test_results if "❌ FAIL" in r['status'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if "✅ PASS" in result['status']:
                print(f"  - {result['test']}: {result['message']}")

if __name__ == "__main__":
    tester = GelisAPITester()
    tester.run_all_tests()