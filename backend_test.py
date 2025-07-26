#!/usr/bin/env python3
"""
Backend API Testing for Spare Parts Billing System
Tests all high-priority backend functionality including CRUD operations,
inventory search, invoice creation, GST calculations, and thermal receipts.
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
            "item_crud": {"passed": 0, "failed": 0, "errors": []},
            "inventory_search": {"passed": 0, "failed": 0, "errors": []},
            "invoice_creation": {"passed": 0, "failed": 0, "errors": []},
            "gst_calculations": {"passed": 0, "failed": 0, "errors": []},
            "thermal_receipt": {"passed": 0, "failed": 0, "errors": []},
            "dashboard_stats": {"passed": 0, "failed": 0, "errors": []}
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

    def test_item_crud_operations(self):
        """Test Item Master CRUD Operations"""
        print("\n🔧 Testing Item Master CRUD Operations...")
        
        # Test 1: Create items with different categories and GST rates
        test_items_data = [
            {
                "sku": "BRAKE001",
                "name": "Brake Pad Set - Front",
                "category": "Brake System",
                "brand": "Bosch",
                "unit": "Set",
                "cost_price": 1200.0,
                "selling_price": 1500.0,
                "hsn_code": "87083010",
                "gst_rate": 28.0,
                "stock_quantity": 50,
                "min_stock": 10
            },
            {
                "sku": "OIL001",
                "name": "Engine Oil 5W-30",
                "category": "Lubricants",
                "brand": "Castrol",
                "unit": "Liter",
                "cost_price": 400.0,
                "selling_price": 500.0,
                "hsn_code": "27101981",
                "gst_rate": 18.0,
                "stock_quantity": 100,
                "min_stock": 20
            },
            {
                "sku": "FILTER001",
                "name": "Air Filter",
                "category": "Filters",
                "brand": "Mann",
                "unit": "Piece",
                "cost_price": 250.0,
                "selling_price": 350.0,
                "hsn_code": "84213910",
                "gst_rate": 18.0,
                "stock_quantity": 25,
                "min_stock": 5
            }
        ]

        # Create items
        for item_data in test_items_data:
            try:
                response = self.session.post(f"{BACKEND_URL}/items", json=item_data)
                if response.status_code == 200:
                    item = response.json()
                    self.test_items.append(item)
                    self.log_result("item_crud", f"Create item {item_data['sku']}", True)
                else:
                    self.log_result("item_crud", f"Create item {item_data['sku']}", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("item_crud", f"Create item {item_data['sku']}", False, str(e))

        # Test 2: Read all items
        try:
            response = self.session.get(f"{BACKEND_URL}/items")
            if response.status_code == 200:
                items = response.json()
                if len(items) >= len(test_items_data):
                    self.log_result("item_crud", "Read all items", True)
                else:
                    self.log_result("item_crud", "Read all items", False, 
                                  f"Expected at least {len(test_items_data)} items, got {len(items)}")
            else:
                self.log_result("item_crud", "Read all items", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("item_crud", "Read all items", False, str(e))

        # Test 3: Read individual items
        for item in self.test_items:
            try:
                response = self.session.get(f"{BACKEND_URL}/items/{item['id']}")
                if response.status_code == 200:
                    retrieved_item = response.json()
                    if retrieved_item['id'] == item['id']:
                        self.log_result("item_crud", f"Read item {item['sku']}", True)
                    else:
                        self.log_result("item_crud", f"Read item {item['sku']}", False, "ID mismatch")
                else:
                    self.log_result("item_crud", f"Read item {item['sku']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("item_crud", f"Read item {item['sku']}", False, str(e))

        # Test 4: Update item
        if self.test_items:
            item_to_update = self.test_items[0]
            update_data = {
                "selling_price": 1600.0,
                "stock_quantity": 45
            }
            try:
                response = self.session.put(f"{BACKEND_URL}/items/{item_to_update['id']}", json=update_data)
                if response.status_code == 200:
                    updated_item = response.json()
                    if updated_item['selling_price'] == 1600.0 and updated_item['stock_quantity'] == 45:
                        self.log_result("item_crud", f"Update item {item_to_update['sku']}", True)
                        # Update our local copy
                        item_to_update.update(updated_item)
                    else:
                        self.log_result("item_crud", f"Update item {item_to_update['sku']}", False, 
                                      "Update values not reflected")
                else:
                    self.log_result("item_crud", f"Update item {item_to_update['sku']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("item_crud", f"Update item {item_to_update['sku']}", False, str(e))

        # Test 5: Test duplicate SKU validation
        if self.test_items:
            duplicate_item = {
                "sku": self.test_items[0]["sku"],  # Use existing SKU
                "name": "Duplicate Test Item",
                "cost_price": 100.0,
                "selling_price": 150.0,
                "gst_rate": 18.0
            }
            try:
                response = self.session.post(f"{BACKEND_URL}/items", json=duplicate_item)
                if response.status_code == 400:
                    self.log_result("item_crud", "Duplicate SKU validation", True)
                else:
                    self.log_result("item_crud", "Duplicate SKU validation", False, 
                                  f"Expected 400, got {response.status_code}")
            except Exception as e:
                self.log_result("item_crud", "Duplicate SKU validation", False, str(e))

    def test_inventory_search(self):
        """Test Real-time Inventory Search"""
        print("\n🔍 Testing Real-time Inventory Search...")
        
        if not self.test_items:
            self.log_result("inventory_search", "Search tests", False, "No test items available")
            return

        # Test 1: Search by name
        try:
            response = self.session.get(f"{BACKEND_URL}/items?search=Brake")
            if response.status_code == 200:
                items = response.json()
                brake_items = [item for item in items if "Brake" in item["name"]]
                if brake_items:
                    self.log_result("inventory_search", "Search by name", True)
                else:
                    self.log_result("inventory_search", "Search by name", False, "No brake items found")
            else:
                self.log_result("inventory_search", "Search by name", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("inventory_search", "Search by name", False, str(e))

        # Test 2: Search by SKU
        try:
            response = self.session.get(f"{BACKEND_URL}/items?search=OIL001")
            if response.status_code == 200:
                items = response.json()
                oil_items = [item for item in items if item["sku"] == "OIL001"]
                if oil_items:
                    self.log_result("inventory_search", "Search by SKU", True)
                else:
                    self.log_result("inventory_search", "Search by SKU", False, "OIL001 not found")
            else:
                self.log_result("inventory_search", "Search by SKU", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("inventory_search", "Search by SKU", False, str(e))

        # Test 3: Search by category
        try:
            response = self.session.get(f"{BACKEND_URL}/items?search=Lubricants")
            if response.status_code == 200:
                items = response.json()
                lubricant_items = [item for item in items if "Lubricants" in item["category"]]
                if lubricant_items:
                    self.log_result("inventory_search", "Search by category", True)
                else:
                    self.log_result("inventory_search", "Search by category", False, "No lubricant items found")
            else:
                self.log_result("inventory_search", "Search by category", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("inventory_search", "Search by category", False, str(e))

        # Test 4: Search by brand
        try:
            response = self.session.get(f"{BACKEND_URL}/items?search=Bosch")
            if response.status_code == 200:
                items = response.json()
                bosch_items = [item for item in items if "Bosch" in item["brand"]]
                if bosch_items:
                    self.log_result("inventory_search", "Search by brand", True)
                else:
                    self.log_result("inventory_search", "Search by brand", False, "No Bosch items found")
            else:
                self.log_result("inventory_search", "Search by brand", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("inventory_search", "Search by brand", False, str(e))

    def test_invoice_creation_and_stock_updates(self):
        """Test Invoice Creation with Stock Updates"""
        print("\n📄 Testing Invoice Creation with Stock Updates...")
        
        if len(self.test_items) < 2:
            self.log_result("invoice_creation", "Invoice creation tests", False, "Need at least 2 test items")
            return

        # Get current stock levels
        initial_stocks = {}
        for item in self.test_items:
            try:
                response = self.session.get(f"{BACKEND_URL}/items/{item['id']}")
                if response.status_code == 200:
                    current_item = response.json()
                    initial_stocks[item['id']] = current_item['stock_quantity']
            except Exception as e:
                self.log_result("invoice_creation", f"Get initial stock for {item['sku']}", False, str(e))

        # Test 1: Create invoice with multiple items
        invoice_data = {
            "customer_name": "John Smith",
            "customer_phone": "9876543210",
            "customer_gstin": "27ABCDE1234F1Z5",
            "items": [
                {"item_id": self.test_items[0]["id"], "quantity": 2},
                {"item_id": self.test_items[1]["id"], "quantity": 3}
            ],
            "payment_mode": "Cash"
        }

        try:
            response = self.session.post(f"{BACKEND_URL}/invoices", json=invoice_data)
            if response.status_code == 200:
                invoice = response.json()
                self.test_invoices.append(invoice)
                self.log_result("invoice_creation", "Create multi-item invoice", True)
                
                # Verify stock updates
                for item_data in invoice_data["items"]:
                    item_id = item_data["item_id"]
                    quantity_sold = item_data["quantity"]
                    expected_stock = initial_stocks[item_id] - quantity_sold
                    
                    try:
                        response = self.session.get(f"{BACKEND_URL}/items/{item_id}")
                        if response.status_code == 200:
                            updated_item = response.json()
                            if updated_item['stock_quantity'] == expected_stock:
                                item_sku = next(item['sku'] for item in self.test_items if item['id'] == item_id)
                                self.log_result("invoice_creation", f"Stock update for {item_sku}", True)
                            else:
                                self.log_result("invoice_creation", f"Stock update for {item_sku}", False, 
                                              f"Expected {expected_stock}, got {updated_item['stock_quantity']}")
                    except Exception as e:
                        self.log_result("invoice_creation", f"Verify stock update for {item_id}", False, str(e))
                        
            else:
                self.log_result("invoice_creation", "Create multi-item invoice", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("invoice_creation", "Create multi-item invoice", False, str(e))

        # Test 2: Test insufficient stock scenario
        if self.test_items:
            insufficient_stock_data = {
                "customer_name": "Test Customer",
                "items": [
                    {"item_id": self.test_items[0]["id"], "quantity": 1000}  # More than available stock
                ],
                "payment_mode": "Cash"
            }
            
            try:
                response = self.session.post(f"{BACKEND_URL}/invoices", json=insufficient_stock_data)
                if response.status_code == 400:
                    self.log_result("invoice_creation", "Insufficient stock validation", True)
                else:
                    self.log_result("invoice_creation", "Insufficient stock validation", False, 
                                  f"Expected 400, got {response.status_code}")
            except Exception as e:
                self.log_result("invoice_creation", "Insufficient stock validation", False, str(e))

    def test_gst_calculations(self):
        """Test GST Calculations"""
        print("\n💰 Testing GST Calculations...")
        
        if not self.test_invoices:
            self.log_result("gst_calculations", "GST calculation tests", False, "No test invoices available")
            return

        # Test GST calculations on the created invoice
        for invoice in self.test_invoices:
            try:
                # Manually calculate expected values
                expected_subtotal = 0
                expected_total_gst = 0
                
                for item in invoice["items"]:
                    line_total = item["quantity"] * item["unit_price"]
                    gst_amount = (line_total * item["gst_rate"]) / 100
                    expected_subtotal += line_total
                    expected_total_gst += gst_amount
                
                expected_gross_total = expected_subtotal + expected_total_gst
                expected_final_total = round(expected_gross_total)
                expected_round_off = expected_final_total - expected_gross_total
                
                # Verify calculations
                subtotal_correct = abs(invoice["subtotal"] - expected_subtotal) < 0.01
                gst_correct = abs(invoice["total_gst"] - expected_total_gst) < 0.01
                final_total_correct = abs(invoice["final_total"] - expected_final_total) < 0.01
                round_off_correct = abs(invoice["round_off"] - expected_round_off) < 0.01
                
                if subtotal_correct:
                    self.log_result("gst_calculations", f"Subtotal calculation for {invoice['invoice_number']}", True)
                else:
                    self.log_result("gst_calculations", f"Subtotal calculation for {invoice['invoice_number']}", False, 
                                  f"Expected {expected_subtotal}, got {invoice['subtotal']}")
                
                if gst_correct:
                    self.log_result("gst_calculations", f"GST calculation for {invoice['invoice_number']}", True)
                else:
                    self.log_result("gst_calculations", f"GST calculation for {invoice['invoice_number']}", False, 
                                  f"Expected {expected_total_gst}, got {invoice['total_gst']}")
                
                if final_total_correct:
                    self.log_result("gst_calculations", f"Final total for {invoice['invoice_number']}", True)
                else:
                    self.log_result("gst_calculations", f"Final total for {invoice['invoice_number']}", False, 
                                  f"Expected {expected_final_total}, got {invoice['final_total']}")
                
                if round_off_correct:
                    self.log_result("gst_calculations", f"Round-off for {invoice['invoice_number']}", True)
                else:
                    self.log_result("gst_calculations", f"Round-off for {invoice['invoice_number']}", False, 
                                  f"Expected {expected_round_off}, got {invoice['round_off']}")
                    
            except Exception as e:
                self.log_result("gst_calculations", f"GST calculations for {invoice['invoice_number']}", False, str(e))

    def test_thermal_receipt_generation(self):
        """Test Thermal Receipt Generation"""
        print("\n🧾 Testing Thermal Receipt Generation...")
        
        if not self.test_invoices:
            self.log_result("thermal_receipt", "Thermal receipt tests", False, "No test invoices available")
            return

        for invoice in self.test_invoices:
            try:
                response = self.session.get(f"{BACKEND_URL}/invoices/{invoice['id']}/thermal-receipt")
                if response.status_code == 200:
                    receipt_data = response.json()
                    receipt_text = receipt_data.get("receipt", "")
                    
                    # Verify receipt contains essential elements
                    checks = [
                        ("Invoice number", invoice["invoice_number"] in receipt_text),
                        ("Customer name", invoice["customer_name"] in receipt_text),
                        ("Store header", "SPARE PARTS STORE" in receipt_text),
                        ("Items section", "ITEM" in receipt_text and "QTY" in receipt_text),
                        ("Total section", "TOTAL:" in receipt_text),
                        ("Thank you message", "Thank you" in receipt_text),
                        ("Receipt width", all(len(line) <= 48 for line in receipt_text.split('\n')))
                    ]
                    
                    for check_name, check_result in checks:
                        if check_result:
                            self.log_result("thermal_receipt", f"{check_name} in {invoice['invoice_number']}", True)
                        else:
                            self.log_result("thermal_receipt", f"{check_name} in {invoice['invoice_number']}", False, 
                                          f"{check_name} not found or invalid")
                            
                else:
                    self.log_result("thermal_receipt", f"Generate receipt for {invoice['invoice_number']}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("thermal_receipt", f"Generate receipt for {invoice['invoice_number']}", False, str(e))

    def test_dashboard_statistics(self):
        """Test Dashboard Statistics API"""
        print("\n📊 Testing Dashboard Statistics...")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                
                # Verify all required fields are present
                required_fields = ["total_items", "total_invoices", "low_stock_items", "today_invoices", "today_revenue"]
                for field in required_fields:
                    if field in stats:
                        self.log_result("dashboard_stats", f"Stats field: {field}", True)
                    else:
                        self.log_result("dashboard_stats", f"Stats field: {field}", False, "Field missing")
                
                # Verify data types and reasonable values
                if isinstance(stats.get("total_items"), int) and stats["total_items"] >= 0:
                    self.log_result("dashboard_stats", "Total items data type", True)
                else:
                    self.log_result("dashboard_stats", "Total items data type", False, "Invalid data type or value")
                
                if isinstance(stats.get("today_revenue"), (int, float)) and stats["today_revenue"] >= 0:
                    self.log_result("dashboard_stats", "Today revenue data type", True)
                else:
                    self.log_result("dashboard_stats", "Today revenue data type", False, "Invalid data type or value")
                    
            else:
                self.log_result("dashboard_stats", "Get dashboard stats", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("dashboard_stats", "Get dashboard stats", False, str(e))

        # Test low stock items endpoint
        try:
            response = self.session.get(f"{BACKEND_URL}/items/low-stock")
            if response.status_code == 200:
                low_stock_items = response.json()
                self.log_result("dashboard_stats", "Get low stock items", True)
            else:
                self.log_result("dashboard_stats", "Get low stock items", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("dashboard_stats", "Get low stock items", False, str(e))

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
        print("🔍 BACKEND API TEST SUMMARY")
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
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests...")
        print(f"Backend URL: {BACKEND_URL}")
        
        try:
            # Test basic connectivity
            response = self.session.get(f"{BACKEND_URL}/items")
            print(f"✅ Backend connectivity: {response.status_code}")
        except Exception as e:
            print(f"❌ Backend connectivity failed: {e}")
            return False
        
        # Run all test suites
        self.test_item_crud_operations()
        self.test_inventory_search()
        self.test_invoice_creation_and_stock_updates()
        self.test_gst_calculations()
        self.test_thermal_receipt_generation()
        self.test_dashboard_statistics()
        
        # Print summary
        success = self.print_summary()
        
        # Cleanup
        self.cleanup_test_data()
        
        return success

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)