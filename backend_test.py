#!/usr/bin/env python3
"""
Backend API Testing for Spare Parts Billing System - Updated Version
Tests updated functionality based on user corrections:
1. Revenue calculation fix (only completed invoices)
2. Item model simplification (no HSN/GST/unit, added sub_category, min_stock=5)
3. Remove GST calculations (subtotal = final_total)
4. Ongoing invoice management (save/complete/delete)
5. Multiple prices per SKU
6. Updated thermal receipt (no GST, shows status)
"""

import requests
import json
import sys
from datetime import datetime
from decimal import Decimal

# Backend URL from frontend/.env
BACKEND_URL = "https://4d655391-d956-45ac-844f-b0ea32ccb758.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_items = []
        self.test_invoices = []
        self.results = {
            "item_model_simplification": {"passed": 0, "failed": 0, "errors": []},
            "multiple_prices_per_sku": {"passed": 0, "failed": 0, "errors": []},
            "ongoing_invoice_management": {"passed": 0, "failed": 0, "errors": []},
            "gst_removal": {"passed": 0, "failed": 0, "errors": []},
            "revenue_calculation_fix": {"passed": 0, "failed": 0, "errors": []},
            "thermal_receipt_update": {"passed": 0, "failed": 0, "errors": []}
        }

    def log_result(self, category, test_name, success, error_msg=None):
        """Log test result"""
        if success:
            self.results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results[category]["failed"] += 1
            self.results[category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")

    def test_item_model_simplification(self):
        """Test Item Model Simplification - No HSN/GST/unit, added sub_category, min_stock=5"""
        print("\n🔧 Testing Item Model Simplification...")
        
        # Test 1: Create items with simplified model (no HSN, GST, unit)
        test_items_data = [
            {
                "sku": "BRAKE001",
                "name": "Brake Pad Set - Front",
                "category": "Brake System",
                "sub_category": "Front Brake",
                "brand": "Bosch",
                "cost_price": 1200.0,
                "selling_price": 1500.0,
                "stock_quantity": 50,
                "min_stock": 5  # Should default to 5
            },
            {
                "sku": "OIL001",
                "name": "Engine Oil 5W-30",
                "category": "Lubricants",
                "sub_category": "Engine Oil",
                "brand": "Castrol",
                "cost_price": 400.0,
                "selling_price": 500.0,
                "stock_quantity": 100
                # min_stock not provided - should default to 5
            },
            {
                "sku": "FILTER001",
                "name": "Air Filter",
                "category": "Filters",
                "sub_category": "Air Filters",
                "brand": "Mann",
                "cost_price": 250.0,
                "selling_price": 350.0,
                "stock_quantity": 25,
                "min_stock": 8  # Custom value
            }
        ]

        # Create items and verify simplified model
        for item_data in test_items_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/items", json=item_data)
                if response.status_code == 200:
                    item = response.json()
                    self.test_items.append(item)
                    
                    # Verify simplified model - should NOT have HSN, GST, unit
                    has_forbidden_fields = any(field in item for field in ['hsn_code', 'gst_rate', 'unit'])
                    has_sub_category = 'sub_category' in item
                    correct_min_stock = item.get('min_stock', 0) == item_data.get('min_stock', 5)
                    
                    if not has_forbidden_fields:
                        self.log_result("item_model_simplification", f"No forbidden fields in {item_data['sku']}", True)
                    else:
                        self.log_result("item_model_simplification", f"No forbidden fields in {item_data['sku']}", False, 
                                      "Item contains HSN/GST/unit fields")
                    
                    if has_sub_category:
                        self.log_result("item_model_simplification", f"Has sub_category field in {item_data['sku']}", True)
                    else:
                        self.log_result("item_model_simplification", f"Has sub_category field in {item_data['sku']}", False, 
                                      "Missing sub_category field")
                    
                    if correct_min_stock:
                        self.log_result("item_model_simplification", f"Correct min_stock in {item_data['sku']}", True)
                    else:
                        self.log_result("item_model_simplification", f"Correct min_stock in {item_data['sku']}", False, 
                                      f"Expected {item_data.get('min_stock', 5)}, got {item.get('min_stock')}")
                        
                    self.log_result("item_model_simplification", f"Create simplified item {item_data['sku']}", True)
                else:
                    self.log_result("item_model_simplification", f"Create simplified item {item_data['sku']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("item_model_simplification", f"Create simplified item {item_data['sku']}", False, str(e))

    def test_multiple_prices_per_sku(self):
        """Test Multiple Prices per SKU - Same SKU can have different prices"""
        print("\n💰 Testing Multiple Prices per SKU...")
        
        # Test 1: Create multiple items with same SKU but different prices
        same_sku_items = [
            {
                "sku": "SPARK001",
                "name": "Spark Plug - Standard",
                "category": "Ignition",
                "sub_category": "Spark Plugs",
                "brand": "NGK",
                "cost_price": 150.0,
                "selling_price": 200.0,
                "stock_quantity": 30
            },
            {
                "sku": "SPARK001",  # Same SKU
                "name": "Spark Plug - Premium",
                "category": "Ignition",
                "sub_category": "Spark Plugs",
                "brand": "NGK",
                "cost_price": 250.0,
                "selling_price": 350.0,  # Different price
                "stock_quantity": 20
            },
            {
                "sku": "SPARK001",  # Same SKU again
                "name": "Spark Plug - Platinum",
                "category": "Ignition",
                "sub_category": "Spark Plugs",
                "brand": "NGK",
                "cost_price": 400.0,
                "selling_price": 550.0,  # Different price
                "stock_quantity": 15
            }
        ]

        created_spark_items = []
        for item_data in same_sku_items:
            try:
                response = self.session.post(f"{BACKEND_URL}/items", json=item_data)
                if response.status_code == 200:
                    item = response.json()
                    created_spark_items.append(item)
                    self.test_items.append(item)
                    self.log_result("multiple_prices_per_sku", f"Create {item['name']}", True)
                else:
                    self.log_result("multiple_prices_per_sku", f"Create {item_data['name']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("multiple_prices_per_sku", f"Create {item_data['name']}", False, str(e))

        # Test 2: Get price variants by SKU
        if created_spark_items:
            try:
                response = self.session.get(f"{BACKEND_URL}/items/by-sku/SPARK001")
                if response.status_code == 200:
                    variants = response.json()
                    if len(variants) >= 3:
                        self.log_result("multiple_prices_per_sku", "Get price variants by SKU", True)
                        
                        # Verify different prices
                        prices = [item['selling_price'] for item in variants]
                        unique_prices = set(prices)
                        if len(unique_prices) >= 3:
                            self.log_result("multiple_prices_per_sku", "Multiple different prices for same SKU", True)
                        else:
                            self.log_result("multiple_prices_per_sku", "Multiple different prices for same SKU", False, 
                                          f"Expected 3+ unique prices, got {len(unique_prices)}")
                    else:
                        self.log_result("multiple_prices_per_sku", "Get price variants by SKU", False, 
                                      f"Expected 3+ variants, got {len(variants)}")
                else:
                    self.log_result("multiple_prices_per_sku", "Get price variants by SKU", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("multiple_prices_per_sku", "Get price variants by SKU", False, str(e))

    def test_ongoing_invoice_management(self):
        """Test Ongoing Invoice Management - Save/Complete/Delete workflow"""
        print("\n📋 Testing Ongoing Invoice Management...")
        
        if len(self.test_items) < 2:
            self.log_result("ongoing_invoice_management", "Ongoing invoice tests", False, "Need at least 2 test items")
            return

        # Test 1: Create ongoing invoice
        ongoing_invoice_data = {
            "customer_name": "John Doe",
            "customer_phone": "9876543210",
            "items": [
                {"item_id": self.test_items[0]["id"], "quantity": 2, "selected_price": self.test_items[0]["selling_price"]},
                {"item_id": self.test_items[1]["id"], "quantity": 1, "selected_price": self.test_items[1]["selling_price"]}
            ],
            "payment_mode": "Cash",
            "status": "ongoing"
        }

        ongoing_invoice = None
        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", json=ongoing_invoice_data)
            if response.status_code == 200:
                ongoing_invoice = response.json()
                self.test_invoices.append(ongoing_invoice)
                
                if ongoing_invoice["status"] == "ongoing":
                    self.log_result("ongoing_invoice_management", "Create ongoing invoice", True)
                else:
                    self.log_result("ongoing_invoice_management", "Create ongoing invoice", False, 
                                  f"Expected status 'ongoing', got '{ongoing_invoice['status']}'")
            else:
                self.log_result("ongoing_invoice_management", "Create ongoing invoice", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("ongoing_invoice_management", "Create ongoing invoice", False, str(e))

        # Test 2: Verify stock is NOT updated for ongoing invoice
        if ongoing_invoice:
            for item_data in ongoing_invoice_data["items"]:
                try:
                    response = self.session.get(f"{BACKEND_URL}/items/{item_data['item_id']}")
                    if response.status_code == 200:
                        current_item = response.json()
                        original_item = next(item for item in self.test_items if item['id'] == item_data['item_id'])
                        
                        if current_item['stock_quantity'] == original_item['stock_quantity']:
                            self.log_result("ongoing_invoice_management", f"Stock not updated for ongoing invoice - {original_item['sku']}", True)
                        else:
                            self.log_result("ongoing_invoice_management", f"Stock not updated for ongoing invoice - {original_item['sku']}", False, 
                                          "Stock was updated for ongoing invoice")
                except Exception as e:
                    self.log_result("ongoing_invoice_management", f"Check stock for ongoing invoice", False, str(e))

        # Test 3: Get ongoing invoices
        try:
            response = self.session.get(f"{BACKEND_URL}/invoices/ongoing")
            if response.status_code == 200:
                ongoing_invoices = response.json()
                if any(inv['id'] == ongoing_invoice['id'] for inv in ongoing_invoices):
                    self.log_result("ongoing_invoice_management", "Get ongoing invoices", True)
                else:
                    self.log_result("ongoing_invoice_management", "Get ongoing invoices", False, 
                                  "Created ongoing invoice not found in ongoing list")
            else:
                self.log_result("ongoing_invoice_management", "Get ongoing invoices", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("ongoing_invoice_management", "Get ongoing invoices", False, str(e))

        # Test 4: Complete ongoing invoice
        if ongoing_invoice:
            # Get stock levels before completion
            pre_completion_stocks = {}
            for item_data in ongoing_invoice_data["items"]:
                try:
                    response = self.session.get(f"{BACKEND_URL}/items/{item_data['item_id']}")
                    if response.status_code == 200:
                        item = response.json()
                        pre_completion_stocks[item_data['item_id']] = item['stock_quantity']
                except Exception as e:
                    pass

            try:
                response = self.session.put(f"{BACKEND_URL}/invoices/{ongoing_invoice['id']}/complete")
                if response.status_code == 200:
                    self.log_result("ongoing_invoice_management", "Complete ongoing invoice", True)
                    
                    # Verify stock is now updated
                    for item_data in ongoing_invoice_data["items"]:
                        try:
                            response = self.session.get(f"{BACKEND_URL}/items/{item_data['item_id']}")
                            if response.status_code == 200:
                                updated_item = response.json()
                                expected_stock = pre_completion_stocks[item_data['item_id']] - item_data['quantity']
                                
                                if updated_item['stock_quantity'] == expected_stock:
                                    original_item = next(item for item in self.test_items if item['id'] == item_data['item_id'])
                                    self.log_result("ongoing_invoice_management", f"Stock updated after completion - {original_item['sku']}", True)
                                else:
                                    self.log_result("ongoing_invoice_management", f"Stock updated after completion - {original_item['sku']}", False, 
                                                  f"Expected {expected_stock}, got {updated_item['stock_quantity']}")
                        except Exception as e:
                            self.log_result("ongoing_invoice_management", "Check stock after completion", False, str(e))
                            
                else:
                    self.log_result("ongoing_invoice_management", "Complete ongoing invoice", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("ongoing_invoice_management", "Complete ongoing invoice", False, str(e))

        # Test 5: Create another ongoing invoice and delete it
        delete_test_data = {
            "customer_name": "Test Delete",
            "items": [{"item_id": self.test_items[0]["id"], "quantity": 1}],
            "status": "ongoing"
        }

        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", json=delete_test_data)
            if response.status_code == 200:
                delete_invoice = response.json()
                
                # Try to delete ongoing invoice
                delete_response = self.session.delete(f"{BACKEND_URL}/invoices/{delete_invoice['id']}")
                if delete_response.status_code == 200:
                    self.log_result("ongoing_invoice_management", "Delete ongoing invoice", True)
                else:
                    self.log_result("ongoing_invoice_management", "Delete ongoing invoice", False, 
                                  f"Status: {delete_response.status_code}")
        except Exception as e:
            self.log_result("ongoing_invoice_management", "Delete ongoing invoice", False, str(e))

    def test_gst_removal(self):
        """Test GST Calculations Removal - subtotal should equal final_total"""
        print("\n🚫 Testing GST Removal...")
        
        if len(self.test_items) < 2:
            self.log_result("gst_removal", "GST removal tests", False, "Need at least 2 test items")
            return

        # Test 1: Create completed invoice and verify no GST calculations
        no_gst_invoice_data = {
            "customer_name": "No GST Customer",
            "customer_phone": "1234567890",
            "items": [
                {"item_id": self.test_items[0]["id"], "quantity": 3, "selected_price": self.test_items[0]["selling_price"]},
                {"item_id": self.test_items[1]["id"], "quantity": 2, "selected_price": self.test_items[1]["selling_price"]}
            ],
            "payment_mode": "Card",
            "status": "completed"
        }

        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", json=no_gst_invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                self.test_invoices.append(invoice)
                
                # Verify no GST fields
                has_gst_fields = any(field in invoice for field in ['total_gst', 'cgst', 'sgst', 'igst', 'gst_amount'])
                if not has_gst_fields:
                    self.log_result("gst_removal", "No GST fields in invoice", True)
                else:
                    self.log_result("gst_removal", "No GST fields in invoice", False, "Invoice contains GST fields")
                
                # Verify subtotal equals final_total
                if abs(invoice["subtotal"] - invoice["final_total"]) < 0.01:
                    self.log_result("gst_removal", "Subtotal equals final_total", True)
                else:
                    self.log_result("gst_removal", "Subtotal equals final_total", False, 
                                  f"Subtotal: {invoice['subtotal']}, Final Total: {invoice['final_total']}")
                
                # Verify manual calculation
                expected_subtotal = sum(item["line_total"] for item in invoice["items"])
                if abs(invoice["subtotal"] - expected_subtotal) < 0.01:
                    self.log_result("gst_removal", "Correct subtotal calculation", True)
                else:
                    self.log_result("gst_removal", "Correct subtotal calculation", False, 
                                  f"Expected: {expected_subtotal}, Got: {invoice['subtotal']}")
                    
            else:
                self.log_result("gst_removal", "Create invoice without GST", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("gst_removal", "Create invoice without GST", False, str(e))

    def test_revenue_calculation_fix(self):
        """Test Revenue Calculation Fix - Only completed invoices count towards revenue"""
        print("\n💹 Testing Revenue Calculation Fix...")
        
        # Get initial dashboard stats
        initial_stats = None
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
            if response.status_code == 200:
                initial_stats = response.json()
                self.log_result("revenue_calculation_fix", "Get initial dashboard stats", True)
            else:
                self.log_result("revenue_calculation_fix", "Get initial dashboard stats", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("revenue_calculation_fix", "Get initial dashboard stats", False, str(e))

        if not initial_stats:
            return

        # Create ongoing invoice (should not affect revenue)
        if len(self.test_items) >= 1:
            ongoing_revenue_test = {
                "customer_name": "Revenue Test Ongoing",
                "items": [{"item_id": self.test_items[0]["id"], "quantity": 1, "selected_price": 1000.0}],
                "status": "ongoing"
            }

            try:
                response = self.session.post(f"{BACKEND_URL}/invoices", json=ongoing_revenue_test)
                if response.status_code == 200:
                    ongoing_invoice = response.json()
                    
                    # Check stats after ongoing invoice
                    response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
                    if response.status_code == 200:
                        stats_after_ongoing = response.json()
                        
                        # Revenue should not change
                        if abs(stats_after_ongoing["today_revenue"] - initial_stats["today_revenue"]) < 0.01:
                            self.log_result("revenue_calculation_fix", "Ongoing invoice does not affect revenue", True)
                        else:
                            self.log_result("revenue_calculation_fix", "Ongoing invoice does not affect revenue", False, 
                                          f"Revenue changed from {initial_stats['today_revenue']} to {stats_after_ongoing['today_revenue']}")
                        
                        # Ongoing invoices count should increase
                        if stats_after_ongoing["ongoing_invoices"] > initial_stats["ongoing_invoices"]:
                            self.log_result("revenue_calculation_fix", "Ongoing invoices count increased", True)
                        else:
                            self.log_result("revenue_calculation_fix", "Ongoing invoices count increased", False, 
                                          "Ongoing invoices count did not increase")
                            
            except Exception as e:
                self.log_result("revenue_calculation_fix", "Test ongoing invoice revenue impact", False, str(e))

        # Create completed invoice (should affect revenue)
        if len(self.test_items) >= 1:
            completed_revenue_test = {
                "customer_name": "Revenue Test Completed",
                "items": [{"item_id": self.test_items[0]["id"], "quantity": 1, "selected_price": 500.0}],
                "status": "completed"
            }

            try:
                response = self.session.post(f"{BACKEND_URL}/invoices", json=completed_revenue_test)
                if response.status_code == 200:
                    completed_invoice = response.json()
                    self.test_invoices.append(completed_invoice)
                    
                    # Check stats after completed invoice
                    response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
                    if response.status_code == 200:
                        final_stats = response.json()
                        
                        # Revenue should increase by invoice amount
                        expected_revenue_increase = completed_invoice["final_total"]
                        actual_revenue_increase = final_stats["today_revenue"] - initial_stats["today_revenue"]
                        
                        if abs(actual_revenue_increase - expected_revenue_increase) < 0.01:
                            self.log_result("revenue_calculation_fix", "Completed invoice affects revenue correctly", True)
                        else:
                            self.log_result("revenue_calculation_fix", "Completed invoice affects revenue correctly", False, 
                                          f"Expected increase: {expected_revenue_increase}, Actual: {actual_revenue_increase}")
                        
                        # Total invoices count should increase
                        if final_stats["total_invoices"] > initial_stats["total_invoices"]:
                            self.log_result("revenue_calculation_fix", "Total invoices count increased", True)
                        else:
                            self.log_result("revenue_calculation_fix", "Total invoices count increased", False, 
                                          "Total invoices count did not increase")
                            
            except Exception as e:
                self.log_result("revenue_calculation_fix", "Test completed invoice revenue impact", False, str(e))

    def test_thermal_receipt_update(self):
        """Test Updated Thermal Receipt - No GST details, shows invoice status"""
        print("\n🧾 Testing Updated Thermal Receipt...")
        
        if not self.test_invoices:
            self.log_result("thermal_receipt_update", "Thermal receipt tests", False, "No test invoices available")
            return

        for invoice in self.test_invoices:
            try:
                response = self.session.get(f"{BACKEND_URL}/invoices/{invoice['id']}/thermal-receipt")
                if response.status_code == 200:
                    receipt_data = response.json()
                    receipt_text = receipt_data.get("receipt", "")
                    
                    # Verify receipt does NOT contain GST calculation details
                    # Check for GST-related calculation terms, not just the word GST in customer names
                    gst_calculation_terms = ['CGST:', 'SGST:', 'IGST:', 'GST Amount:', 'Tax Amount:', 'HSN Code:']
                    has_gst_calculations = any(term in receipt_text for term in gst_calculation_terms)
                    
                    if not has_gst_calculations:
                        self.log_result("thermal_receipt_update", f"No GST calculations in receipt {invoice['invoice_number']}", True)
                    else:
                        self.log_result("thermal_receipt_update", f"No GST calculations in receipt {invoice['invoice_number']}", False, 
                                      "Receipt contains GST calculation details")
                    
                    # Verify receipt shows invoice status
                    status_shown = f"Status: {invoice['status'].upper()}" in receipt_text
                    if status_shown:
                        self.log_result("thermal_receipt_update", f"Invoice status shown in receipt {invoice['invoice_number']}", True)
                    else:
                        self.log_result("thermal_receipt_update", f"Invoice status shown in receipt {invoice['invoice_number']}", False, 
                                      "Invoice status not found in receipt")
                    
                    # Verify essential elements still present
                    essential_checks = [
                        ("Invoice number", invoice["invoice_number"] in receipt_text),
                        ("Customer name", invoice["customer_name"] in receipt_text),
                        ("Store header", "SPARE PARTS STORE" in receipt_text),
                        ("Items section", "ITEM" in receipt_text and "QTY" in receipt_text),
                        ("Total section", "TOTAL:" in receipt_text),
                        ("Thank you message", "thank you" in receipt_text.lower()),
                        ("Receipt width", all(len(line) <= 48 for line in receipt_text.split('\n')))
                    ]
                    
                    for check_name, check_result in essential_checks:
                        if check_result:
                            self.log_result("thermal_receipt_update", f"{check_name} in {invoice['invoice_number']}", True)
                        else:
                            self.log_result("thermal_receipt_update", f"{check_name} in {invoice['invoice_number']}", False, 
                                          f"{check_name} not found or invalid")
                            
                else:
                    self.log_result("thermal_receipt_update", f"Generate receipt for {invoice['invoice_number']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("thermal_receipt_update", f"Generate receipt for {invoice['invoice_number']}", False, str(e))

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete test items
        for item in self.test_items:
            try:
                response = self.session.delete(f"{BACKEND_URL}/items/{item['id']}")
                if response.status_code == 200:
                    print(f"✅ Deleted item {item['sku']}")
                else:
                    print(f"⚠️ Failed to delete item {item['sku']}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error deleting item {item['sku']}: {e}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("🔍 BACKEND API TEST SUMMARY - UPDATED FEATURES")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper().replace('_', ' ')}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print("-" * 60)
        print(f"OVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 ALL BACKEND TESTS PASSED!")
            return True
        else:
            print("⚠️ SOME TESTS FAILED - CHECK ERRORS ABOVE")
            return False

    def run_all_tests(self):
        """Run all backend tests for updated features"""
        print("🚀 Starting Backend API Tests for Updated Features...")
        print(f"Backend URL: {BACKEND_URL}")
        
        try:
            # Test basic connectivity
            response = self.session.get(f"{BACKEND_URL}/items")
            print(f"✅ Backend connectivity: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend connectivity failed: {e}")
            return False
        
        # Run all test suites for updated features
        self.test_item_model_simplification()
        self.test_multiple_prices_per_sku()
        self.test_ongoing_invoice_management()
        self.test_gst_removal()
        self.test_revenue_calculation_fix()
        self.test_thermal_receipt_update()
        
        # Print summary
        success = self.print_summary()
        
        # Cleanup
        self.cleanup_test_data()
        
        return success

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)