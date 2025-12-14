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
BACKEND_URL = "https://multibiz-hub-1.preview.emergentagent.com/api"

class GelisAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tokens = {}
        self.test_results = []
        self.users = {
            'owner': {'username': 'owner', 'password': 'owner123'},
            'manager': {'username': 'manager', 'password': 'manager123'},
            'finance': {'username': 'finance', 'password': 'finance123'},
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

    def test_verification_summary_endpoint(self):
        """Test GET /api/reports/verification/summary"""
        print("\n=== TESTING VERIFICATION SUMMARY ENDPOINT ===")
        
        # Test with Owner (should work)
        headers = self.get_headers('owner')
        try:
            response = requests.get(
                f"{self.base_url}/reports/verification/summary",
                params={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Verify required fields
                required_fields = ['period', 'summary', 'verification_status', 'recommendations']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    # Check summary fields
                    summary = data.get('summary', {})
                    summary_fields = ['total_kasir_reports', 'total_loket_reports', 'overall_difference', 'accuracy_rate']
                    missing_summary = [f for f in summary_fields if f not in summary]
                    
                    if not missing_summary:
                        self.log_result("Verification Summary - Owner", True, 
                                      f"Retrieved summary: {summary['total_kasir_reports']} kasir + {summary['total_loket_reports']} loket reports, accuracy: {data['verification_status'].get('accuracy_rate', 0)}%")
                        self.test_data['verification_summary'] = data
                    else:
                        self.log_result("Verification Summary - Owner", False, f"Missing summary fields: {missing_summary}")
                else:
                    self.log_result("Verification Summary - Owner", False, f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Verification Summary - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verification Summary - Owner", False, f"Error: {str(e)}")
        
        # Test with Finance (should work)
        if 'finance' in self.users:
            headers = self.get_headers('finance')
            try:
                response = requests.get(
                    f"{self.base_url}/reports/verification/summary",
                    headers=headers,
                    timeout=30
                )
                if response.status_code == 200:
                    self.log_result("Verification Summary - Finance", True, "Finance user can access verification summary")
                else:
                    self.log_result("Verification Summary - Finance", False, f"Failed: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Verification Summary - Finance", False, f"Error: {str(e)}")
        
        # Test with Loket (should fail with 403)
        headers = self.get_headers('loket1')
        try:
            response = requests.get(
                f"{self.base_url}/reports/verification/summary",
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Verification Summary - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("Verification Summary - Loket (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Verification Summary - Loket (403)", False, f"Error: {str(e)}")

    def test_kasir_reconciliation_endpoint(self):
        """Test GET /api/reports/reconciliation/kasir"""
        print("\n=== TESTING KASIR RECONCILIATION ENDPOINT ===")
        
        # Get a valid report date from existing kasir reports
        report_date = "2024-12-10"  # Use a recent date
        if 'kasir_reports' in self.test_data and self.test_data['kasir_reports']:
            # Extract date from first report
            first_report = self.test_data['kasir_reports'][0]
            if 'report_date' in first_report:
                report_date = first_report['report_date'][:10]  # Get YYYY-MM-DD part
        
        # Test with Owner (should work)
        headers = self.get_headers('owner')
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/kasir",
                params={"report_date": report_date},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Verify required fields
                required_fields = ['reconciliation_date', 'total_reports', 'matched_reports', 'discrepancy_reports', 'reports']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    reports = data.get('reports', [])
                    if reports:
                        # Check first report structure
                        report = reports[0]
                        report_fields = ['status', 'reported_total', 'actual_total', 'breakdown']
                        missing_report_fields = [f for f in report_fields if f not in report]
                        
                        if not missing_report_fields:
                            # Check breakdown structure
                            breakdown = report.get('breakdown', {})
                            breakdown_fields = ['setoran_kasir', 'admin_fee', 'belanja_loket']
                            missing_breakdown = [f for f in breakdown_fields if f not in breakdown]
                            
                            if not missing_breakdown:
                                self.log_result("Kasir Reconciliation - Owner", True, 
                                              f"Reconciled {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
                                self.test_data['kasir_reconciliation'] = data
                            else:
                                self.log_result("Kasir Reconciliation - Owner", False, f"Missing breakdown fields: {missing_breakdown}")
                        else:
                            self.log_result("Kasir Reconciliation - Owner", False, f"Missing report fields: {missing_report_fields}")
                    else:
                        self.log_result("Kasir Reconciliation - Owner", True, f"No reports found for date {report_date} (valid response)")
                else:
                    self.log_result("Kasir Reconciliation - Owner", False, f"Missing required fields: {missing_fields}")
            elif response.status_code == 404:
                self.log_result("Kasir Reconciliation - Owner", True, f"No reports found for date {report_date} (404 expected)")
            else:
                self.log_result("Kasir Reconciliation - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Kasir Reconciliation - Owner", False, f"Error: {str(e)}")
        
        # Test with Finance (should work)
        if 'finance' in self.users:
            headers = self.get_headers('finance')
            try:
                response = requests.get(
                    f"{self.base_url}/reports/reconciliation/kasir",
                    params={"report_date": report_date},
                    headers=headers,
                    timeout=30
                )
                if response.status_code in [200, 404]:
                    self.log_result("Kasir Reconciliation - Finance", True, "Finance user can access kasir reconciliation")
                else:
                    self.log_result("Kasir Reconciliation - Finance", False, f"Failed: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Kasir Reconciliation - Finance", False, f"Error: {str(e)}")
        
        # Test with Loket (should fail with 403)
        headers = self.get_headers('loket1')
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/kasir",
                params={"report_date": report_date},
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Kasir Reconciliation - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("Kasir Reconciliation - Loket (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Kasir Reconciliation - Loket (403)", False, f"Error: {str(e)}")

    def test_loket_reconciliation_endpoint(self):
        """Test GET /api/reports/reconciliation/loket"""
        print("\n=== TESTING LOKET RECONCILIATION ENDPOINT ===")
        
        # Get a valid report date from existing loket reports
        report_date = "2024-12-10"  # Use a recent date
        if 'loket_reports' in self.test_data and self.test_data['loket_reports']:
            # Extract date from first report
            first_report = self.test_data['loket_reports'][0]
            if 'report_date' in first_report:
                report_date = first_report['report_date'][:10]  # Get YYYY-MM-DD part
        
        # Test with Owner (should work)
        headers = self.get_headers('owner')
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/loket",
                params={"report_date": report_date},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                # Verify required fields
                required_fields = ['reconciliation_date', 'total_reports', 'matched_reports', 'discrepancy_reports', 'reports']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    reports = data.get('reports', [])
                    if reports:
                        # Check first report structure
                        report = reports[0]
                        report_fields = ['status', 'reported_total_setoran', 'actual_total_setoran', 'bank_balances', 'all_banks_balanced']
                        missing_report_fields = [f for f in report_fields if f not in report]
                        
                        if not missing_report_fields:
                            # Check bank balance structure
                            bank_balances = report.get('bank_balances', [])
                            if bank_balances:
                                bank = bank_balances[0]
                                bank_fields = ['bank_name', 'reported_saldo_akhir', 'calculated_saldo_akhir', 'is_balanced']
                                missing_bank_fields = [f for f in bank_fields if f not in bank]
                                
                                if not missing_bank_fields:
                                    self.log_result("Loket Reconciliation - Owner", True, 
                                                  f"Reconciled {data['total_reports']} reports, {data['matched_reports']} matched, {data['discrepancy_reports']} discrepancies")
                                    self.test_data['loket_reconciliation'] = data
                                else:
                                    self.log_result("Loket Reconciliation - Owner", False, f"Missing bank fields: {missing_bank_fields}")
                            else:
                                self.log_result("Loket Reconciliation - Owner", True, f"No bank balances in reports for date {report_date}")
                        else:
                            self.log_result("Loket Reconciliation - Owner", False, f"Missing report fields: {missing_report_fields}")
                    else:
                        self.log_result("Loket Reconciliation - Owner", True, f"No reports found for date {report_date} (valid response)")
                else:
                    self.log_result("Loket Reconciliation - Owner", False, f"Missing required fields: {missing_fields}")
            elif response.status_code == 404:
                self.log_result("Loket Reconciliation - Owner", True, f"No reports found for date {report_date} (404 expected)")
            else:
                self.log_result("Loket Reconciliation - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Loket Reconciliation - Owner", False, f"Error: {str(e)}")
        
        # Test with Finance (should work)
        if 'finance' in self.users:
            headers = self.get_headers('finance')
            try:
                response = requests.get(
                    f"{self.base_url}/reports/reconciliation/loket",
                    params={"report_date": report_date},
                    headers=headers,
                    timeout=30
                )
                if response.status_code in [200, 404]:
                    self.log_result("Loket Reconciliation - Finance", True, "Finance user can access loket reconciliation")
                else:
                    self.log_result("Loket Reconciliation - Finance", False, f"Failed: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Loket Reconciliation - Finance", False, f"Error: {str(e)}")
        
        # Test with Loket (should fail with 403)
        headers = self.get_headers('loket1')
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/loket",
                params={"report_date": report_date},
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Loket Reconciliation - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("Loket Reconciliation - Loket (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Loket Reconciliation - Loket (403)", False, f"Error: {str(e)}")

    def test_reconciliation_edge_cases(self):
        """Test edge cases for reconciliation endpoints"""
        print("\n=== TESTING RECONCILIATION EDGE CASES ===")
        
        headers = self.get_headers('owner')
        
        # Test with non-existent date (should return 404)
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/kasir",
                params={"report_date": "2020-01-01"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 404:
                self.log_result("Kasir Reconciliation - No Data (404)", True, "Correctly returns 404 for non-existent date")
            else:
                self.log_result("Kasir Reconciliation - No Data (404)", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Kasir Reconciliation - No Data (404)", False, f"Error: {str(e)}")
        
        # Test with invalid date format
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/kasir",
                params={"report_date": "invalid-date"},
                headers=headers,
                timeout=30
            )
            # Should handle gracefully (either 400 or 404)
            if response.status_code in [400, 404]:
                self.log_result("Kasir Reconciliation - Invalid Date", True, f"Correctly handles invalid date format ({response.status_code})")
            else:
                self.log_result("Kasir Reconciliation - Invalid Date", False, f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Kasir Reconciliation - Invalid Date", False, f"Error: {str(e)}")
        
        # Test loket reconciliation with non-existent date
        try:
            response = requests.get(
                f"{self.base_url}/reports/reconciliation/loket",
                params={"report_date": "2020-01-01"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 404:
                self.log_result("Loket Reconciliation - No Data (404)", True, "Correctly returns 404 for non-existent date")
            else:
                self.log_result("Loket Reconciliation - No Data (404)", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Loket Reconciliation - No Data (404)", False, f"Error: {str(e)}")
        
        # Test verification summary with invalid date range
        try:
            response = requests.get(
                f"{self.base_url}/reports/verification/summary",
                params={
                    "start_date": "2025-01-01",
                    "end_date": "2020-01-01"  # End before start
                },
                headers=headers,
                timeout=30
            )
            # Should handle gracefully
            if response.status_code in [200, 400]:
                self.log_result("Verification Summary - Invalid Range", True, f"Handles invalid date range ({response.status_code})")
            else:
                self.log_result("Verification Summary - Invalid Range", False, f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Verification Summary - Invalid Range", False, f"Error: {str(e)}")

    # ============= FASE 1 NEW ENDPOINTS TESTING =============
    
    def test_technical_progress_endpoints(self):
        """Test Technical Progress endpoints (3 endpoints)"""
        print("\n=== TESTING TECHNICAL PROGRESS ENDPOINTS ===")
        
        # Get an order ID for testing
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/orders", headers=headers, timeout=30)
            if response.status_code == 200:
                orders = response.json()
                if not orders:
                    self.log_result("Technical Progress Setup", False, "No orders available for testing")
                    return
                order_id = orders[0]['id']
            else:
                self.log_result("Technical Progress Setup", False, "Could not retrieve orders")
                return
        except Exception as e:
            self.log_result("Technical Progress Setup", False, f"Error getting orders: {str(e)}")
            return
        
        # Test 1: POST /api/technical-progress - Create technical progress
        try:
            response = requests.post(
                f"{self.base_url}/technical-progress",
                json={"order_id": order_id},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'steps' in data and len(data['steps']) == 5:
                    self.log_result("POST Technical Progress", True, f"Created progress with 5 steps for order {order_id}")
                    self.test_data['technical_progress_order'] = order_id
                else:
                    self.log_result("POST Technical Progress", False, "Missing steps or incorrect step count")
            else:
                self.log_result("POST Technical Progress", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST Technical Progress", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/technical-progress/{order_id} - Get progress
        try:
            response = requests.get(
                f"{self.base_url}/technical-progress/{order_id}",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['order_id', 'steps', 'overall_progress']
                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    self.log_result("GET Technical Progress", True, f"Retrieved progress: {data['overall_progress']}% complete")
                else:
                    self.log_result("GET Technical Progress", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET Technical Progress", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Technical Progress", False, f"Error: {str(e)}")
        
        # Test 3: PUT /api/technical-progress/{order_id}/step - Update step status
        try:
            response = requests.put(
                f"{self.base_url}/technical-progress/{order_id}/step",
                json={
                    "step_name": "Survey Lokasi",
                    "status": "completed",
                    "notes": "Survey completed successfully"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'overall_progress' in data and data['overall_progress'] > 0:
                    self.log_result("PUT Technical Progress Step", True, f"Updated step, progress now: {data['overall_progress']}%")
                else:
                    self.log_result("PUT Technical Progress Step", False, "Progress not updated correctly")
            else:
                self.log_result("PUT Technical Progress Step", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PUT Technical Progress Step", False, f"Error: {str(e)}")

    def test_ppob_shift_report_endpoints(self):
        """Test PPOB Shift Report endpoints (3 endpoints)"""
        print("\n=== TESTING PPOB SHIFT REPORT ENDPOINTS ===")
        
        # Get business ID for testing
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/businesses", headers=headers, timeout=30)
            if response.status_code == 200:
                businesses = response.json()
                if not businesses:
                    self.log_result("PPOB Shift Setup", False, "No businesses available for testing")
                    return
                business_id = businesses[0]['id']
            else:
                self.log_result("PPOB Shift Setup", False, "Could not retrieve businesses")
                return
        except Exception as e:
            self.log_result("PPOB Shift Setup", False, f"Error getting businesses: {str(e)}")
            return
        
        # Test 1: POST /api/reports/ppob-shift - Create shift report
        shift_data = {
            "business_id": business_id,
            "report_date": "2024-12-15",
            "shift": "pagi",
            "petugas_name": "Ahmad Kasir",
            "products": [
                {
                    "product_name": "Token PLN",
                    "quantity": 25,
                    "total_amount": 2500000,
                    "fee_amount": 25000,
                    "commission_amount": 12500
                },
                {
                    "product_name": "Pulsa Telkomsel",
                    "quantity": 15,
                    "total_amount": 750000,
                    "fee_amount": 15000,
                    "commission_amount": 7500
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/reports/ppob-shift",
                json=shift_data,
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'business_id', 'shift', 'total_amount', 'total_fee', 'total_commission']
                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    self.log_result("POST PPOB Shift Report", True, f"Created shift report: {data['total_amount']} total, {data['total_fee']} fee")
                    self.test_data['ppob_shift_report_id'] = data['id']
                else:
                    self.log_result("POST PPOB Shift Report", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("POST PPOB Shift Report", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST PPOB Shift Report", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/reports/ppob-shift - Get shift reports
        try:
            response = requests.get(
                f"{self.base_url}/reports/ppob-shift",
                params={"business_id": business_id, "limit": 10},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'reports' in data and isinstance(data['reports'], list):
                    self.log_result("GET PPOB Shift Reports", True, f"Retrieved {len(data['reports'])} shift reports")
                else:
                    self.log_result("GET PPOB Shift Reports", False, "Invalid response format")
            else:
                self.log_result("GET PPOB Shift Reports", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET PPOB Shift Reports", False, f"Error: {str(e)}")
        
        # Test 3: POST /api/reports/ppob-shift/auto-generate - Auto-generate from transactions
        try:
            response = requests.post(
                f"{self.base_url}/reports/ppob-shift/auto-generate",
                json={
                    "business_id": business_id,
                    "report_date": "2024-12-15",
                    "shift": "siang"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'products' in data and 'total_amount' in data:
                    self.log_result("POST PPOB Auto-Generate", True, f"Auto-generated report: {len(data['products'])} products, {data['total_amount']} total")
                else:
                    self.log_result("POST PPOB Auto-Generate", False, "Missing required fields in response")
            else:
                self.log_result("POST PPOB Auto-Generate", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST PPOB Auto-Generate", False, f"Error: {str(e)}")

    def test_executive_summary_endpoint(self):
        """Test Executive Summary endpoint (1 endpoint)"""
        print("\n=== TESTING EXECUTIVE SUMMARY ENDPOINT ===")
        
        # Test with Owner (should work)
        headers = self.get_headers('owner')
        try:
            response = requests.get(
                f"{self.base_url}/reports/executive-summary",
                params={
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['period', 'overall_summary', 'business_units', 'top_performers', 'alerts', 'insights', 'recommendations']
                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    business_units = data.get('business_units', [])
                    self.log_result("GET Executive Summary - Owner", True, f"Retrieved summary: {len(business_units)} business units, {len(data.get('alerts', []))} alerts")
                    self.test_data['executive_summary'] = data
                else:
                    self.log_result("GET Executive Summary - Owner", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET Executive Summary - Owner", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Executive Summary - Owner", False, f"Error: {str(e)}")
        
        # Test with Manager (should work)
        headers = self.get_headers('manager')
        try:
            response = requests.get(
                f"{self.base_url}/reports/executive-summary",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("GET Executive Summary - Manager", True, "Manager can access executive summary")
            else:
                self.log_result("GET Executive Summary - Manager", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Executive Summary - Manager", False, f"Error: {str(e)}")
        
        # Test with Finance (should work)
        headers = self.get_headers('finance')
        try:
            response = requests.get(
                f"{self.base_url}/reports/executive-summary",
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("GET Executive Summary - Finance", True, "Finance can access executive summary")
            else:
                self.log_result("GET Executive Summary - Finance", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Executive Summary - Finance", False, f"Error: {str(e)}")
        
        # Test with Loket (should fail with 403)
        headers = self.get_headers('loket1')
        try:
            response = requests.get(
                f"{self.base_url}/reports/executive-summary",
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("GET Executive Summary - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("GET Executive Summary - Loket (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("GET Executive Summary - Loket (403)", False, f"Error: {str(e)}")

    def test_export_endpoint(self):
        """Test Export endpoint (1 endpoint)"""
        print("\n=== TESTING EXPORT ENDPOINT ===")
        
        headers = self.get_headers('owner')
        
        # Test 1: Export executive summary to PDF
        try:
            response = requests.post(
                f"{self.base_url}/reports/export",
                json={
                    "report_type": "executive_summary",
                    "format": "pdf",
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'download_url' in data or 'file_content' in data:
                    self.log_result("Export Executive Summary PDF", True, "Successfully exported to PDF")
                else:
                    self.log_result("Export Executive Summary PDF", False, "Missing download URL or file content")
            else:
                self.log_result("Export Executive Summary PDF", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Export Executive Summary PDF", False, f"Error: {str(e)}")
        
        # Test 2: Export executive summary to Excel
        try:
            response = requests.post(
                f"{self.base_url}/reports/export",
                json={
                    "report_type": "executive_summary",
                    "format": "excel",
                    "start_date": "2024-12-01",
                    "end_date": "2024-12-15"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'download_url' in data or 'file_content' in data:
                    self.log_result("Export Executive Summary Excel", True, "Successfully exported to Excel")
                else:
                    self.log_result("Export Executive Summary Excel", False, "Missing download URL or file content")
            else:
                self.log_result("Export Executive Summary Excel", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Export Executive Summary Excel", False, f"Error: {str(e)}")
        
        # Test 3: Export PPOB shift report to PDF (if we have a report ID)
        if 'ppob_shift_report_id' in self.test_data:
            try:
                response = requests.post(
                    f"{self.base_url}/reports/export",
                    json={
                        "report_type": "ppob_shift",
                        "format": "pdf",
                        "report_id": self.test_data['ppob_shift_report_id']
                    },
                    headers=headers,
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'download_url' in data or 'file_content' in data:
                        self.log_result("Export PPOB Shift PDF", True, "Successfully exported PPOB shift to PDF")
                    else:
                        self.log_result("Export PPOB Shift PDF", False, "Missing download URL or file content")
                else:
                    self.log_result("Export PPOB Shift PDF", False, f"Failed: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("Export PPOB Shift PDF", False, f"Error: {str(e)}")
        
        # Test permission control - Kasir should fail
        headers = self.get_headers('kasir1')
        try:
            response = requests.post(
                f"{self.base_url}/reports/export",
                json={
                    "report_type": "executive_summary",
                    "format": "pdf"
                },
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("Export Permission - Kasir (403)", True, "Kasir correctly denied export access (403)")
            else:
                self.log_result("Export Permission - Kasir (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Export Permission - Kasir (403)", False, f"Error: {str(e)}")

    def test_smart_alerts_endpoints(self):
        """Test Smart Alerts endpoints (3 endpoints)"""
        print("\n=== TESTING SMART ALERTS ENDPOINTS ===")
        
        # Test 1: GET /api/alerts - Get alerts with filters
        headers = self.get_headers('owner')
        try:
            response = requests.get(
                f"{self.base_url}/alerts",
                params={"severity": "critical", "is_resolved": "false"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['alerts', 'count', 'unresolved_count']
                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    self.log_result("GET Alerts", True, f"Retrieved {data['count']} alerts, {data['unresolved_count']} unresolved")
                else:
                    self.log_result("GET Alerts", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET Alerts", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Alerts", False, f"Error: {str(e)}")
        
        # Test 2: POST /api/alerts/check - Trigger alert generation
        try:
            response = requests.post(
                f"{self.base_url}/alerts/check",
                json={},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if 'alerts_generated' in data and 'alerts' in data:
                    self.log_result("POST Alerts Check", True, f"Generated {data['alerts_generated']} new alerts")
                    # Store alert ID for resolve test
                    if data['alerts']:
                        self.test_data['alert_id'] = data['alerts'][0]['id']
                else:
                    self.log_result("POST Alerts Check", False, "Missing required fields in response")
            else:
                self.log_result("POST Alerts Check", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST Alerts Check", False, f"Error: {str(e)}")
        
        # Test permission for alerts check - Only Owner/Manager should work
        headers = self.get_headers('manager')
        try:
            response = requests.post(
                f"{self.base_url}/alerts/check",
                json={},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("POST Alerts Check - Manager", True, "Manager can trigger alert checks")
            else:
                self.log_result("POST Alerts Check - Manager", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST Alerts Check - Manager", False, f"Error: {str(e)}")
        
        # Test permission denial for non-authorized users
        headers = self.get_headers('kasir1')
        try:
            response = requests.post(
                f"{self.base_url}/alerts/check",
                json={},
                headers=headers,
                timeout=30
            )
            if response.status_code == 403:
                self.log_result("POST Alerts Check - Kasir (403)", True, "Kasir correctly denied alert check access (403)")
            else:
                self.log_result("POST Alerts Check - Kasir (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("POST Alerts Check - Kasir (403)", False, f"Error: {str(e)}")
        
        # Test 3: PUT /api/alerts/{alert_id}/resolve - Resolve alert
        if 'alert_id' in self.test_data:
            headers = self.get_headers('owner')
            try:
                response = requests.put(
                    f"{self.base_url}/alerts/{self.test_data['alert_id']}/resolve",
                    json={"notes": "Issue resolved by testing"},
                    headers=headers,
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    if 'message' in data:
                        self.log_result("PUT Resolve Alert", True, "Successfully resolved alert with notes")
                    else:
                        self.log_result("PUT Resolve Alert", False, "Missing success message")
                else:
                    self.log_result("PUT Resolve Alert", False, f"Failed: {response.status_code}", response.text)
            except Exception as e:
                self.log_result("PUT Resolve Alert", False, f"Error: {str(e)}")
        else:
            self.log_result("PUT Resolve Alert", False, "No alert ID available for testing")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting GELIS Backend API Testing Suite - FASE 1 NEW ENDPOINTS")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run authentication first
        self.test_authentication()
        
        # FASE 1 NEW ENDPOINTS TESTING (15 endpoints)
        print("\n🎯 TESTING FASE 1 NEW ENDPOINTS (15 endpoints)")
        print("=" * 60)
        
        # 1. Technical Progress Endpoints (3 endpoints)
        self.test_technical_progress_endpoints()
        
        # 2. PPOB Shift Report Endpoints (3 endpoints)
        self.test_ppob_shift_report_endpoints()
        
        # 3. Executive Summary Endpoint (1 endpoint)
        self.test_executive_summary_endpoint()
        
        # 4. Export Endpoint (1 endpoint)
        self.test_export_endpoint()
        
        # 5. Smart Alerts Endpoints (3 endpoints)
        self.test_smart_alerts_endpoints()
        
        # PREVIOUS TESTS (for regression testing)
        print("\n📋 REGRESSION TESTING - PREVIOUS ENDPOINTS")
        print("=" * 60)
        
        self.test_reports_get_endpoints()
        self.test_edit_loket_report_permissions()
        self.test_edit_kasir_report_permissions()
        self.test_delete_report_permissions()
        self.test_teknisi_orders_endpoint()
        self.test_teknisi_update_status()
        self.test_teknisi_update_progress()
        self.test_auto_generate_reports()
        
        # RECONCILIATION & VERIFICATION TESTS
        self.test_verification_summary_endpoint()
        self.test_kasir_reconciliation_endpoint()
        self.test_loket_reconciliation_endpoint()
        self.test_reconciliation_edge_cases()
        
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