#!/usr/bin/env python3
"""
GELIS Auto-Sync Accounting System Testing Suite
Tests the new AUTO-SYNC ACCOUNTING functionality including:
- Auto-create transactions on order creation/update
- Financial dashboard real-time sync
- Permission controls
- Edge cases
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os
import time

# Get backend URL from frontend .env
BACKEND_URL = "https://finance-modules-2.preview.emergentagent.com/api"

class AutoSyncAccountingTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.tokens = {}
        self.test_results = []
        self.users = {
            'owner': {'username': 'owner', 'password': 'owner123'},
            'finance': {'username': 'finance', 'password': 'finance123'},
            'loket': {'username': 'loket1', 'password': 'loket123'}
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
    
    def get_business_id(self):
        """Get a business ID for testing"""
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/businesses", headers=headers, timeout=30)
            if response.status_code == 200:
                businesses = response.json()
                if businesses:
                    return businesses[0]['id']
            return None
        except:
            return None
    
    def test_authentication(self):
        """Test authentication for required users"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        for user_type in self.users.keys():
            self.login_user(user_type)
    
    def test_auto_create_transaction_on_order_creation(self):
        """Test auto-create transaction when order is created with payment"""
        print("\n=== TESTING AUTO-CREATE TRANSACTION ON ORDER CREATION ===")
        
        business_id = self.get_business_id()
        if not business_id:
            self.log_result("Order Creation Setup", False, "Could not get business ID")
            return
        
        headers = self.get_headers('owner')
        
        # Get initial transaction count
        try:
            response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
            initial_count = len(response.json()) if response.status_code == 200 else 0
        except:
            initial_count = 0
        
        # Create order with payment (2M out of 5M)
        order_data = {
            "business_id": business_id,
            "customer_name": "John Doe",
            "customer_phone": "081234567890",
            "customer_email": "john@example.com",
            "service_type": "PLN",
            "order_details": {
                "product": "Token PLN 100k",
                "quantity": 1,
                "unit_price": 5000000,
                "progress": 0
            },
            "total_amount": 5000000,
            "paid_amount": 2000000,  # Partial payment
            "payment_method": "cash",
            "notes": "Test order for auto-sync accounting",
            "requires_technician": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/orders",
                json=order_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                self.test_data['test_order_id'] = order['id']
                
                # Verify payment status is set correctly
                if order.get('payment_status') == 'partial':
                    self.log_result("Order Creation - Payment Status", True, "Payment status correctly set to 'partial'")
                else:
                    self.log_result("Order Creation - Payment Status", False, f"Expected 'partial', got '{order.get('payment_status')}'")
                
                # Check if transaction was auto-created
                time.sleep(1)  # Small delay to ensure transaction is created
                response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
                if response.status_code == 200:
                    transactions = response.json()
                    new_count = len(transactions)
                    
                    if new_count > initial_count:
                        # Find the transaction for this order
                        order_transaction = None
                        for txn in transactions:
                            if txn.get('order_id') == order['id']:
                                order_transaction = txn
                                break
                        
                        if order_transaction:
                            # Verify transaction details
                            if (order_transaction.get('transaction_type') == 'income' and
                                order_transaction.get('category') == 'Order Payment' and
                                order_transaction.get('amount') == 2000000):
                                self.log_result("Auto-Create Transaction on Order Creation", True, 
                                              f"Transaction auto-created: {order_transaction['transaction_code']} - Rp 2,000,000")
                            else:
                                self.log_result("Auto-Create Transaction on Order Creation", False, 
                                              f"Transaction created but details incorrect: {order_transaction}")
                        else:
                            self.log_result("Auto-Create Transaction on Order Creation", False, 
                                          "Transaction count increased but no transaction found for order")
                    else:
                        self.log_result("Auto-Create Transaction on Order Creation", False, 
                                      f"Transaction count did not increase (was {initial_count}, now {new_count})")
                else:
                    self.log_result("Auto-Create Transaction on Order Creation", False, 
                                  f"Could not retrieve transactions: {response.status_code}")
            else:
                self.log_result("Auto-Create Transaction on Order Creation", False, 
                              f"Order creation failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Auto-Create Transaction on Order Creation", False, f"Error: {str(e)}")
    
    def test_auto_create_transaction_on_order_update(self):
        """Test auto-create transaction when order is updated with additional payment"""
        print("\n=== TESTING AUTO-CREATE TRANSACTION ON ORDER UPDATE ===")
        
        if 'test_order_id' not in self.test_data:
            self.log_result("Order Update Setup", False, "No test order available")
            return
        
        headers = self.get_headers('owner')
        order_id = self.test_data['test_order_id']
        
        # Get initial transaction count for this order
        try:
            response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
            if response.status_code == 200:
                transactions = response.json()
                initial_order_transactions = [t for t in transactions if t.get('order_id') == order_id]
                initial_count = len(initial_order_transactions)
            else:
                initial_count = 0
        except:
            initial_count = 0
        
        # Update order with full payment (5M total, already paid 2M, so add 3M)
        try:
            response = requests.put(
                f"{self.base_url}/orders/{order_id}",
                params={
                    "paid_amount": 5000000,  # Full payment now
                    "payment_status": "paid"
                },
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if auto_transaction_created flag is returned
                if result.get('auto_transaction_created'):
                    self.log_result("Order Update - Auto Transaction Flag", True, "Auto transaction creation flag returned")
                else:
                    self.log_result("Order Update - Auto Transaction Flag", False, "Auto transaction creation flag not returned")
                
                # Verify new transaction was created
                time.sleep(1)  # Small delay
                response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
                if response.status_code == 200:
                    transactions = response.json()
                    order_transactions = [t for t in transactions if t.get('order_id') == order_id]
                    new_count = len(order_transactions)
                    
                    if new_count > initial_count:
                        # Find the new transaction (should be 3M)
                        new_transaction = None
                        for txn in order_transactions:
                            if txn.get('amount') == 3000000:  # The additional payment
                                new_transaction = txn
                                break
                        
                        if new_transaction:
                            self.log_result("Auto-Create Transaction on Order Update", True, 
                                          f"Additional transaction auto-created: {new_transaction['transaction_code']} - Rp 3,000,000")
                            
                            # Verify total transactions for this order
                            total_amount = sum(t['amount'] for t in order_transactions)
                            if total_amount == 5000000:
                                self.log_result("Order Update - Total Verification", True, 
                                              f"Total transactions match order amount: Rp 5,000,000")
                            else:
                                self.log_result("Order Update - Total Verification", False, 
                                              f"Total transactions ({total_amount}) don't match order amount (5,000,000)")
                        else:
                            self.log_result("Auto-Create Transaction on Order Update", False, 
                                          "Transaction count increased but no 3M transaction found")
                    else:
                        self.log_result("Auto-Create Transaction on Order Update", False, 
                                      f"Transaction count did not increase (was {initial_count}, now {new_count})")
                else:
                    self.log_result("Auto-Create Transaction on Order Update", False, 
                                  f"Could not retrieve transactions: {response.status_code}")
            else:
                self.log_result("Auto-Create Transaction on Order Update", False, 
                              f"Order update failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Auto-Create Transaction on Order Update", False, f"Error: {str(e)}")
    
    def test_financial_dashboard_endpoint(self):
        """Test financial dashboard endpoint with real-time data"""
        print("\n=== TESTING FINANCIAL DASHBOARD ENDPOINT ===")
        
        headers = self.get_headers('owner')
        business_id = self.get_business_id()
        
        # Test basic dashboard access
        try:
            response = requests.get(f"{self.base_url}/financial/dashboard", headers=headers, timeout=30)
            
            if response.status_code == 200:
                dashboard = response.json()
                
                # Verify required fields exist
                required_fields = ['financial_summary', 'orders_summary', 'transaction_count']
                missing_fields = [field for field in required_fields if field not in dashboard]
                
                if not missing_fields:
                    self.log_result("Financial Dashboard - Structure", True, "All required fields present")
                    
                    # Verify financial_summary fields
                    financial_summary = dashboard['financial_summary']
                    required_financial_fields = ['total_income', 'total_expense', 'net_profit', 'profit_margin']
                    missing_financial = [field for field in required_financial_fields if field not in financial_summary]
                    
                    if not missing_financial:
                        self.log_result("Financial Dashboard - Financial Summary", True, 
                                      f"Income: {financial_summary['total_income']}, Expense: {financial_summary['total_expense']}, Net: {financial_summary['net_profit']}")
                    else:
                        self.log_result("Financial Dashboard - Financial Summary", False, 
                                      f"Missing fields: {missing_financial}")
                    
                    # Verify orders_summary fields
                    orders_summary = dashboard['orders_summary']
                    required_order_fields = ['total_orders', 'total_order_amount', 'paid_orders', 'pending_orders']
                    missing_order = [field for field in required_order_fields if field not in orders_summary]
                    
                    if not missing_order:
                        self.log_result("Financial Dashboard - Orders Summary", True, 
                                      f"Total Orders: {orders_summary['total_orders']}, Paid: {orders_summary['paid_orders']}")
                    else:
                        self.log_result("Financial Dashboard - Orders Summary", False, 
                                      f"Missing fields: {missing_order}")
                    
                    # Store dashboard data for real-time sync test
                    self.test_data['initial_dashboard'] = dashboard
                    
                else:
                    self.log_result("Financial Dashboard - Structure", False, f"Missing fields: {missing_fields}")
            else:
                self.log_result("Financial Dashboard - Access", False, f"Failed: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Financial Dashboard - Access", False, f"Error: {str(e)}")
        
        # Test with business_id filter
        if business_id:
            try:
                response = requests.get(
                    f"{self.base_url}/financial/dashboard",
                    params={"business_id": business_id},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.log_result("Financial Dashboard - Business Filter", True, "Business ID filter working")
                else:
                    self.log_result("Financial Dashboard - Business Filter", False, f"Failed: {response.status_code}")
            except Exception as e:
                self.log_result("Financial Dashboard - Business Filter", False, f"Error: {str(e)}")
        
        # Test with date range filter
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.base_url}/financial/dashboard",
                params={
                    "start_date": yesterday,
                    "end_date": today
                },
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_result("Financial Dashboard - Date Filter", True, "Date range filter working")
            else:
                self.log_result("Financial Dashboard - Date Filter", False, f"Failed: {response.status_code}")
        except Exception as e:
            self.log_result("Financial Dashboard - Date Filter", False, f"Error: {str(e)}")
    
    def test_real_time_sync_verification(self):
        """Test real-time sync by creating order and verifying dashboard updates"""
        print("\n=== TESTING REAL-TIME SYNC VERIFICATION ===")
        
        if 'initial_dashboard' not in self.test_data:
            self.log_result("Real-time Sync Setup", False, "No initial dashboard data available")
            return
        
        headers = self.get_headers('owner')
        business_id = self.get_business_id()
        
        initial_dashboard = self.test_data['initial_dashboard']
        initial_income = initial_dashboard['financial_summary']['total_income']
        initial_transaction_count = initial_dashboard['transaction_count']['total']
        
        # Create new order with payment
        order_data = {
            "business_id": business_id,
            "customer_name": "Jane Smith",
            "customer_phone": "081234567891",
            "customer_email": "jane@example.com",
            "service_type": "PDAM",
            "order_details": {
                "product": "PDAM Tagihan",
                "quantity": 1,
                "unit_price": 1500000,
                "progress": 0
            },
            "total_amount": 1500000,
            "paid_amount": 1500000,  # Full payment
            "payment_method": "transfer",
            "notes": "Test order for real-time sync verification",
            "requires_technician": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/orders",
                json=order_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                order = response.json()
                
                # Wait a moment for sync
                time.sleep(2)
                
                # Get updated dashboard
                response = requests.get(f"{self.base_url}/financial/dashboard", headers=headers, timeout=30)
                
                if response.status_code == 200:
                    updated_dashboard = response.json()
                    updated_income = updated_dashboard['financial_summary']['total_income']
                    updated_transaction_count = updated_dashboard['transaction_count']['total']
                    
                    # Verify income increased by exact amount
                    income_increase = updated_income - initial_income
                    if income_increase == 1500000:
                        self.log_result("Real-time Sync - Income Update", True, 
                                      f"Income increased by exactly Rp 1,500,000 (from {initial_income} to {updated_income})")
                    else:
                        self.log_result("Real-time Sync - Income Update", False, 
                                      f"Income increase mismatch: expected 1,500,000, got {income_increase}")
                    
                    # Verify transaction count increased by 1
                    count_increase = updated_transaction_count - initial_transaction_count
                    if count_increase == 1:
                        self.log_result("Real-time Sync - Transaction Count", True, 
                                      f"Transaction count increased by 1 (from {initial_transaction_count} to {updated_transaction_count})")
                    else:
                        self.log_result("Real-time Sync - Transaction Count", False, 
                                      f"Transaction count increase mismatch: expected 1, got {count_increase}")
                else:
                    self.log_result("Real-time Sync - Dashboard Retrieval", False, 
                                  f"Could not get updated dashboard: {response.status_code}")
            else:
                self.log_result("Real-time Sync - Order Creation", False, 
                              f"Could not create test order: {response.status_code}")
                
        except Exception as e:
            self.log_result("Real-time Sync - Verification", False, f"Error: {str(e)}")
    
    def test_permission_control(self):
        """Test financial dashboard permissions with different user roles"""
        print("\n=== TESTING PERMISSION CONTROL ===")
        
        # Test with owner (should work)
        headers = self.get_headers('owner')
        try:
            response = requests.get(f"{self.base_url}/financial/dashboard", headers=headers, timeout=30)
            if response.status_code == 200:
                self.log_result("Permission Control - Owner", True, "Owner can access financial dashboard")
            else:
                self.log_result("Permission Control - Owner", False, f"Owner access failed: {response.status_code}")
        except Exception as e:
            self.log_result("Permission Control - Owner", False, f"Error: {str(e)}")
        
        # Test with finance role (should work)
        headers = self.get_headers('finance')
        try:
            response = requests.get(f"{self.base_url}/financial/dashboard", headers=headers, timeout=30)
            if response.status_code == 200:
                self.log_result("Permission Control - Finance", True, "Finance role can access financial dashboard")
            else:
                self.log_result("Permission Control - Finance", False, f"Finance access failed: {response.status_code}")
        except Exception as e:
            self.log_result("Permission Control - Finance", False, f"Error: {str(e)}")
        
        # Test with loket role (should fail with 403)
        headers = self.get_headers('loket')
        try:
            response = requests.get(f"{self.base_url}/financial/dashboard", headers=headers, timeout=30)
            if response.status_code == 403:
                self.log_result("Permission Control - Loket (403)", True, "Loket correctly denied access (403)")
            else:
                self.log_result("Permission Control - Loket (403)", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Permission Control - Loket (403)", False, f"Error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases for auto-sync accounting"""
        print("\n=== TESTING EDGE CASES ===")
        
        headers = self.get_headers('owner')
        business_id = self.get_business_id()
        
        # Edge Case 1: Order with paid_amount = 0 (no transaction should be created)
        try:
            response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
            initial_count = len(response.json()) if response.status_code == 200 else 0
            
            order_data = {
                "business_id": business_id,
                "customer_name": "Zero Payment Test",
                "customer_phone": "081234567892",
                "customer_email": "zero@example.com",
                "service_type": "PPOB",
                "order_details": {
                    "product": "Pulsa 50k",
                    "quantity": 1,
                    "unit_price": 50000,
                    "progress": 0
                },
                "total_amount": 50000,
                "paid_amount": 0,  # No payment
                "payment_method": "cash",
                "notes": "Test order with zero payment"
            }
            
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                order = response.json()
                
                # Verify payment status is unpaid
                if order.get('payment_status') == 'unpaid':
                    self.log_result("Edge Case - Zero Payment Status", True, "Payment status correctly set to 'unpaid'")
                else:
                    self.log_result("Edge Case - Zero Payment Status", False, f"Expected 'unpaid', got '{order.get('payment_status')}'")
                
                # Verify no transaction was created
                time.sleep(1)
                response = requests.get(f"{self.base_url}/transactions", headers=headers, timeout=30)
                if response.status_code == 200:
                    new_count = len(response.json())
                    if new_count == initial_count:
                        self.log_result("Edge Case - Zero Payment No Transaction", True, "No transaction created for zero payment")
                    else:
                        self.log_result("Edge Case - Zero Payment No Transaction", False, "Transaction was created for zero payment")
            else:
                self.log_result("Edge Case - Zero Payment Order", False, f"Order creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Zero Payment", False, f"Error: {str(e)}")
        
        # Edge Case 2: Order with paid_amount = total_amount (payment_status should be "paid")
        try:
            order_data = {
                "business_id": business_id,
                "customer_name": "Full Payment Test",
                "customer_phone": "081234567893",
                "customer_email": "full@example.com",
                "service_type": "PLN",
                "order_details": {
                    "product": "Token PLN 200k",
                    "quantity": 1,
                    "unit_price": 200000,
                    "progress": 0
                },
                "total_amount": 200000,
                "paid_amount": 200000,  # Full payment
                "payment_method": "transfer",
                "notes": "Test order with full payment"
            }
            
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                order = response.json()
                
                if order.get('payment_status') == 'paid':
                    self.log_result("Edge Case - Full Payment Status", True, "Payment status correctly set to 'paid'")
                else:
                    self.log_result("Edge Case - Full Payment Status", False, f"Expected 'paid', got '{order.get('payment_status')}'")
            else:
                self.log_result("Edge Case - Full Payment Order", False, f"Order creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Full Payment", False, f"Error: {str(e)}")
        
        # Edge Case 3: Order with 0 < paid_amount < total_amount (payment_status should be "partial")
        try:
            order_data = {
                "business_id": business_id,
                "customer_name": "Partial Payment Test",
                "customer_phone": "081234567894",
                "customer_email": "partial@example.com",
                "service_type": "PDAM",
                "order_details": {
                    "product": "PDAM Tagihan",
                    "quantity": 1,
                    "unit_price": 300000,
                    "progress": 0
                },
                "total_amount": 300000,
                "paid_amount": 150000,  # Partial payment (50%)
                "payment_method": "cash",
                "notes": "Test order with partial payment"
            }
            
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                order = response.json()
                
                if order.get('payment_status') == 'partial':
                    self.log_result("Edge Case - Partial Payment Status", True, "Payment status correctly set to 'partial'")
                else:
                    self.log_result("Edge Case - Partial Payment Status", False, f"Expected 'partial', got '{order.get('payment_status')}'")
            else:
                self.log_result("Edge Case - Partial Payment Order", False, f"Order creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_result("Edge Case - Partial Payment", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all auto-sync accounting tests"""
        print("🚀 Starting GELIS Auto-Sync Accounting System Testing Suite")
        print(f"Backend URL: {self.base_url}")
        print("=" * 70)
        
        # Run tests in order
        self.test_authentication()
        self.test_auto_create_transaction_on_order_creation()
        self.test_auto_create_transaction_on_order_update()
        self.test_financial_dashboard_endpoint()
        self.test_real_time_sync_verification()
        self.test_permission_control()
        self.test_edge_cases()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 AUTO-SYNC ACCOUNTING TEST SUMMARY")
        print("=" * 70)
        
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
    tester = AutoSyncAccountingTester()
    tester.run_all_tests()