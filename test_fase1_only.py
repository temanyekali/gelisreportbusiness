#!/usr/bin/env python3
"""
GELIS Backend API Testing - FASE 1 NEW ENDPOINTS ONLY
Quick focused test of the 15 new endpoints
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Get backend URL from frontend .env
BACKEND_URL = "https://multibiz-hub-1.preview.emergentagent.com/api"

class Fase1Tester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.test_results = []
        
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
    
    def login(self):
        """Login as owner"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"identifier": "owner", "password": "owner123"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access_token']
                self.log_result("Login", True, "Successfully logged in as owner")
                return True
            else:
                self.log_result("Login", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Login", False, f"Login error: {str(e)}")
            return False
    
    def get_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_technical_progress_endpoints(self):
        """Test Technical Progress endpoints (3 endpoints)"""
        print("\n=== TESTING TECHNICAL PROGRESS ENDPOINTS ===")
        
        # Get an order ID for testing
        headers = self.get_headers()
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
        
        # Test 1: POST /api/technical-progress
        try:
            response = requests.post(
                f"{self.base_url}/technical-progress",
                json={"order_id": order_id},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("POST Technical Progress", True, "Created technical progress successfully")
            elif response.status_code == 400 and "sudah ada" in response.text:
                self.log_result("POST Technical Progress", True, "Technical progress already exists (expected)")
            else:
                self.log_result("POST Technical Progress", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST Technical Progress", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/technical-progress/{order_id}
        try:
            response = requests.get(f"{self.base_url}/technical-progress/{order_id}", headers=headers, timeout=30)
            if response.status_code == 200:
                self.log_result("GET Technical Progress", True, "Retrieved technical progress successfully")
            else:
                self.log_result("GET Technical Progress", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Technical Progress", False, f"Error: {str(e)}")
        
        # Test 3: PUT /api/technical-progress/{order_id}/step
        try:
            response = requests.put(
                f"{self.base_url}/technical-progress/{order_id}/step",
                json={"step_name": "Survey Teknis", "status": "completed", "notes": "Test update"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("PUT Technical Progress Step", True, "Updated step successfully")
            else:
                self.log_result("PUT Technical Progress Step", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PUT Technical Progress Step", False, f"Error: {str(e)}")

    def test_ppob_shift_endpoints(self):
        """Test PPOB Shift Report endpoints (3 endpoints)"""
        print("\n=== TESTING PPOB SHIFT REPORT ENDPOINTS ===")
        
        # Get business ID
        headers = self.get_headers()
        try:
            response = requests.get(f"{self.base_url}/businesses", headers=headers, timeout=30)
            if response.status_code == 200:
                businesses = response.json()
                if not businesses:
                    self.log_result("PPOB Setup", False, "No businesses available")
                    return
                business_id = businesses[0]['id']
            else:
                self.log_result("PPOB Setup", False, "Could not retrieve businesses")
                return
        except Exception as e:
            self.log_result("PPOB Setup", False, f"Error: {str(e)}")
            return
        
        # Test 1: POST /api/reports/ppob-shift
        shift_data = {
            "business_id": business_id,
            "report_date": "2024-12-15",
            "shift": 1,
            "petugas_name": "Ahmad Kasir",
            "product_breakdown": [
                {
                    "product_type": "Token PLN",
                    "transaction_count": 25,
                    "total_amount": 2500000,
                    "total_fee": 25000,
                    "total_commission": 12500
                }
            ]
        }
        
        try:
            response = requests.post(f"{self.base_url}/reports/ppob-shift", json=shift_data, headers=headers, timeout=30)
            if response.status_code == 200:
                self.log_result("POST PPOB Shift Report", True, "Created PPOB shift report successfully")
            else:
                self.log_result("POST PPOB Shift Report", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST PPOB Shift Report", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/reports/ppob-shift
        try:
            response = requests.get(f"{self.base_url}/reports/ppob-shift", headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET PPOB Shift Reports", True, f"Retrieved {data.get('count', 0)} reports")
            else:
                self.log_result("GET PPOB Shift Reports", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET PPOB Shift Reports", False, f"Error: {str(e)}")
        
        # Test 3: POST /api/reports/ppob-shift/auto-generate
        try:
            response = requests.post(
                f"{self.base_url}/reports/ppob-shift/auto-generate",
                params={"business_id": business_id, "report_date": "2024-12-15", "shift": 2},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                self.log_result("POST PPOB Auto-Generate", True, "Auto-generated PPOB report successfully")
            else:
                self.log_result("POST PPOB Auto-Generate", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST PPOB Auto-Generate", False, f"Error: {str(e)}")

    def test_executive_summary_endpoint(self):
        """Test Executive Summary endpoint"""
        print("\n=== TESTING EXECUTIVE SUMMARY ENDPOINT ===")
        
        headers = self.get_headers()
        try:
            response = requests.get(
                f"{self.base_url}/reports/executive-summary",
                params={"start_date": "2024-12-01", "end_date": "2024-12-15"},
                headers=headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['period_start', 'period_end', 'business_units', 'alerts', 'insights', 'recommendations']
                missing_fields = [f for f in required_fields if f not in data]
                if not missing_fields:
                    self.log_result("GET Executive Summary", True, f"Retrieved summary with {len(data.get('business_units', []))} business units")
                else:
                    self.log_result("GET Executive Summary", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("GET Executive Summary", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Executive Summary", False, f"Error: {str(e)}")

    def test_export_endpoint(self):
        """Test Export endpoint"""
        print("\n=== TESTING EXPORT ENDPOINT ===")
        
        headers = self.get_headers()
        
        # Test PDF export
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
                self.log_result("Export Executive Summary PDF", True, "Successfully exported to PDF")
            else:
                self.log_result("Export Executive Summary PDF", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Export Executive Summary PDF", False, f"Error: {str(e)}")

    def test_smart_alerts_endpoints(self):
        """Test Smart Alerts endpoints"""
        print("\n=== TESTING SMART ALERTS ENDPOINTS ===")
        
        headers = self.get_headers()
        
        # Test 1: GET /api/alerts
        try:
            response = requests.get(f"{self.base_url}/alerts", headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("GET Alerts", True, f"Retrieved {data.get('count', 0)} alerts")
            else:
                self.log_result("GET Alerts", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET Alerts", False, f"Error: {str(e)}")
        
        # Test 2: POST /api/alerts/check
        try:
            response = requests.post(f"{self.base_url}/alerts/check", json={}, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.log_result("POST Alerts Check", True, f"Generated {data.get('alerts_generated', 0)} alerts")
            else:
                self.log_result("POST Alerts Check", False, f"Failed: {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST Alerts Check", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all FASE 1 tests"""
        print("🚀 Starting GELIS FASE 1 NEW ENDPOINTS Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        if not self.login():
            print("❌ Cannot proceed without authentication")
            return
        
        # Test all 15 new endpoints
        self.test_technical_progress_endpoints()      # 3 endpoints
        self.test_ppob_shift_endpoints()             # 3 endpoints  
        self.test_executive_summary_endpoint()       # 1 endpoint
        self.test_export_endpoint()                  # 1 endpoint
        self.test_smart_alerts_endpoints()           # 3 endpoints (2 tested)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FASE 1 TEST SUMMARY")
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
    tester = Fase1Tester()
    tester.run_all_tests()