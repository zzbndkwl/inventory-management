import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Dashboard = ({ onNavigate, ongoingInvoices, setOngoingInvoices }) => {
  const [stats, setStats] = useState({});
  const [lowStockItems, setLowStockItems] = useState([]);

  useEffect(() => {
    fetchDashboardStats();
    fetchLowStockItems();
    fetchOngoingInvoices();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    }
  };

  const fetchLowStockItems = async () => {
    try {
      const response = await axios.get(`${API}/items/low-stock`);
      setLowStockItems(response.data);
    } catch (error) {
      console.error("Error fetching low stock items:", error);
    }
  };

  const fetchOngoingInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices/ongoing`);
      setOngoingInvoices(response.data);
    } catch (error) {
      console.error("Error fetching ongoing invoices:", error);
    }
  };

  const completeInvoice = async (invoiceId) => {
    try {
      await axios.put(`${API}/invoices/${invoiceId}/complete`);
      alert("Invoice completed successfully!");
      fetchDashboardStats();
      fetchOngoingInvoices();
    } catch (error) {
      console.error("Error completing invoice:", error);
      alert("Error completing invoice: " + (error.response?.data?.detail || error.message));
    }
  };

  const deleteInvoice = async (invoiceId) => {
    if (window.confirm("Are you sure you want to delete this invoice?")) {
      try {
        await axios.delete(`${API}/invoices/${invoiceId}`);
        alert("Invoice deleted successfully!");
        fetchOngoingInvoices();
      } catch (error) {
        console.error("Error deleting invoice:", error);
        alert("Error deleting invoice: " + (error.response?.data?.detail || error.message));
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Spare Parts Management</h1>
          <div className="flex gap-4">
            <button
              onClick={() => onNavigate('create-invoice')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Create Invoice
            </button>
            <button
              onClick={() => onNavigate('manage-items')}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Manage Items
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Total Items</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_items || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Today's Sales</p>
                <p className="text-2xl font-bold text-gray-900">{stats.today_invoices || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-yellow-500">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Today's Revenue</p>
                <p className="text-2xl font-bold text-gray-900">₹{(stats.today_revenue || 0).toFixed(2)}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Ongoing Bills</p>
                <p className="text-2xl font-bold text-gray-900">{stats.ongoing_invoices || 0}</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
            <div className="flex items-center">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Low Stock Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.low_stock_items || 0}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Ongoing Invoices */}
        {ongoingInvoices.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Ongoing Invoices</h2>
            <div className="space-y-4">
              {ongoingInvoices.map(invoice => (
                <div key={invoice.id} className="flex items-center justify-between p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{invoice.invoice_number}</p>
                    <p className="text-sm text-gray-600">{invoice.customer_name} - ₹{invoice.final_total.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">{invoice.items.length} items</p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => completeInvoice(invoice.id)}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                    >
                      Complete
                    </button>
                    <button
                      onClick={() => deleteInvoice(invoice.id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Low Stock Items Alert */}
        {lowStockItems.length > 0 && (
          <div className="bg-red-50 border-l-4 border-red-400 p-6 mb-8 rounded-lg">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Low Stock Alert</h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>The following items are running low on stock:</p>
                  <ul className="list-disc list-inside mt-1">
                    {lowStockItems.slice(0, 5).map(item => (
                      <li key={item.id}>{item.name} - {item.stock_quantity} remaining</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const CreateInvoice = ({ onNavigate, ongoingInvoices, setOngoingInvoices }) => {
  const [items, setItems] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredItems, setFilteredItems] = useState([]);
  const [invoiceItems, setInvoiceItems] = useState([]);
  const [priceVariants, setPriceVariants] = useState({});
  const [customerInfo, setCustomerInfo] = useState({
    name: "Walk-in Customer",
    phone: ""
  });
  const [paymentMode, setPaymentMode] = useState("Cash");
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    fetchItems();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = items.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.sub_category.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      // Group by SKU to show price variants
      const groupedBySku = {};
      filtered.forEach(item => {
        if (!groupedBySku[item.sku]) {
          groupedBySku[item.sku] = [];
        }
        groupedBySku[item.sku].push(item);
      });
      
      setFilteredItems(Object.values(groupedBySku).flat().slice(0, 20));
    } else {
      setFilteredItems([]);
    }
  }, [searchTerm, items]);

  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API}/items`);
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  const addItemToInvoice = (item) => {
    const existingItem = invoiceItems.find(i => i.id === item.id);
    if (existingItem) {
      setInvoiceItems(invoiceItems.map(i =>
        i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
      ));
    } else {
      setInvoiceItems([...invoiceItems, { ...item, quantity: 1, selected_price: item.selling_price }]);
    }
    setSearchTerm("");
    setFilteredItems([]);
  };

  const updateItemQuantity = (itemId, quantity) => {
    if (quantity <= 0) {
      setInvoiceItems(invoiceItems.filter(i => i.id !== itemId));
    } else {
      setInvoiceItems(invoiceItems.map(i =>
        i.id === itemId ? { ...i, quantity } : i
      ));
    }
  };

  const updateItemPrice = (itemId, price) => {
    setInvoiceItems(invoiceItems.map(i =>
      i.id === itemId ? { ...i, selected_price: parseFloat(price) } : i
    ));
  };

  const calculateTotals = () => {
    let subtotal = 0;

    invoiceItems.forEach(item => {
      const lineTotal = item.quantity * item.selected_price;
      subtotal += lineTotal;
    });

    return { subtotal, finalTotal: subtotal };
  };

  const createInvoice = async (saveAsOngoing = false) => {
    if (invoiceItems.length === 0) {
      alert("Please add at least one item to the invoice");
      return;
    }

    setIsCreating(true);
    try {
      const invoiceData = {
        customer_name: customerInfo.name,
        customer_phone: customerInfo.phone,
        items: invoiceItems.map(item => ({
          item_id: item.id,
          quantity: item.quantity,
          selected_price: item.selected_price
        })),
        payment_mode: paymentMode,
        status: saveAsOngoing ? "ongoing" : "completed"
      };

      const response = await axios.post(`${API}/invoices`, invoiceData);
      const message = saveAsOngoing ? 
        `Invoice ${response.data.invoice_number} saved as ongoing!` : 
        `Invoice ${response.data.invoice_number} created successfully!`;
      alert(message);
      
      // Reset form
      setInvoiceItems([]);
      setCustomerInfo({ name: "Walk-in Customer", phone: "" });
      setPaymentMode("Cash");
      
      // Update ongoing invoices if saved as ongoing
      if (saveAsOngoing) {
        setOngoingInvoices([...ongoingInvoices, response.data]);
      }
      
    } catch (error) {
      console.error("Error creating invoice:", error);
      alert("Error creating invoice: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsCreating(false);
    }
  };

  const totals = calculateTotals();

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Create Invoice</h1>
          <button
            onClick={() => onNavigate('dashboard')}
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
          >
            Back to Dashboard
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Item Selection */}
          <div className="lg:col-span-2 space-y-6">
            {/* Customer Information */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Customer Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Customer Name"
                  value={customerInfo.name}
                  onChange={(e) => setCustomerInfo({...customerInfo, name: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <input
                  type="text"
                  placeholder="Phone Number"
                  value={customerInfo.phone}
                  onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Item Search */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Add Items</h2>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search items by name, SKU, category, or sub-category..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                
                {filteredItems.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    {filteredItems.map(item => (
                      <div
                        key={item.id}
                        onClick={() => addItemToInvoice(item)}
                        className="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="font-medium text-gray-900">{item.name}</p>
                            <p className="text-sm text-gray-600">SKU: {item.sku} | Stock: {item.stock_quantity}</p>
                            {item.sub_category && (
                              <p className="text-xs text-gray-500">{item.category} > {item.sub_category}</p>
                            )}
                          </div>
                          <div className="text-right">
                            <p className="font-medium text-gray-900">₹{item.selling_price}</p>
                            {item.brand && <p className="text-sm text-gray-600">{item.brand}</p>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Invoice Items */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Invoice Items</h2>
              {invoiceItems.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No items added yet. Search and add items above.</p>
              ) : (
                <div className="space-y-4">
                  {invoiceItems.map(item => (
                    <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{item.name}</p>
                        <p className="text-sm text-gray-600">SKU: {item.sku}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => updateItemQuantity(item.id, item.quantity - 1)}
                            className="w-8 h-8 bg-red-100 text-red-600 rounded-full flex items-center justify-center hover:bg-red-200"
                          >
                            -
                          </button>
                          <span className="w-12 text-center">{item.quantity}</span>
                          <button
                            onClick={() => updateItemQuantity(item.id, item.quantity + 1)}
                            className="w-8 h-8 bg-green-100 text-green-600 rounded-full flex items-center justify-center hover:bg-green-200"
                          >
                            +
                          </button>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600">₹</span>
                          <input
                            type="number"
                            step="0.01"
                            value={item.selected_price}
                            onChange={(e) => updateItemPrice(item.id, e.target.value)}
                            className="w-20 px-2 py-1 border border-gray-300 rounded text-center"
                          />
                        </div>
                        <div className="text-right min-w-[80px]">
                          <p className="font-medium">₹{(item.quantity * item.selected_price).toFixed(2)}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Invoice Summary */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Invoice Summary</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between text-lg font-bold">
                  <span>Total:</span>
                  <span>₹{totals.finalTotal.toFixed(2)}</span>
                </div>
              </div>

              <div className="mt-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Payment Mode
                </label>
                <select
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Cash">Cash</option>
                  <option value="Card">Card</option>
                  <option value="UPI">UPI</option>
                  <option value="Credit">Credit</option>
                </select>
              </div>

              <div className="flex flex-col gap-3 mt-6">
                <button
                  onClick={() => createInvoice(false)}
                  disabled={isCreating || invoiceItems.length === 0}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  {isCreating ? "Creating..." : "Complete Invoice"}
                </button>
                
                <button
                  onClick={() => createInvoice(true)}
                  disabled={isCreating || invoiceItems.length === 0}
                  className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
                >
                  {isCreating ? "Saving..." : "Save as Ongoing"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ManageItems = ({ onNavigate }) => {
  const [items, setItems] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [newItem, setNewItem] = useState({
    sku: "",
    name: "",
    category: "",
    sub_category: "",
    brand: "",
    cost_price: "",
    selling_price: "",
    stock_quantity: "",
    min_stock: 5
  });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API}/items?search=${searchTerm}`);
      setItems(response.data);
    } catch (error) {
      console.error("Error fetching items:", error);
    }
  };

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      fetchItems();
    }, 300);

    return () => clearTimeout(delayedSearch);
  }, [searchTerm]);

  const handleAddItem = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/items`, {
        ...newItem,
        cost_price: parseFloat(newItem.cost_price),
        selling_price: parseFloat(newItem.selling_price),
        stock_quantity: parseInt(newItem.stock_quantity),
        min_stock: parseInt(newItem.min_stock)
      });
      setNewItem({
        sku: "",
        name: "",
        category: "",
        sub_category: "",
        brand: "",
        cost_price: "",
        selling_price: "",
        stock_quantity: "",
        min_stock: 5
      });
      setShowAddForm(false);
      fetchItems();
      alert("Item added successfully!");
    } catch (error) {
      console.error("Error adding item:", error);
      alert("Error adding item: " + (error.response?.data?.detail || error.message));
    }
  };

  const filteredItems = items.filter(item =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.sub_category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Manage Items</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowAddForm(true)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Add New Item
            </button>
            <button
              onClick={() => onNavigate('dashboard')}
              className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <input
            type="text"
            placeholder="Search items by name, SKU, category, or sub-category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Add Item Form Modal */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-2xl p-8 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Add New Item</h2>
              <form onSubmit={handleAddItem} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="SKU *"
                    value={newItem.sku}
                    onChange={(e) => setNewItem({...newItem, sku: e.target.value})}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Item Name *"
                    value={newItem.name}
                    onChange={(e) => setNewItem({...newItem, name: e.target.value})}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Category"
                    value={newItem.category}
                    onChange={(e) => setNewItem({...newItem, category: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Sub Category"
                    value={newItem.sub_category}
                    onChange={(e) => setNewItem({...newItem, sub_category: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Brand"
                    value={newItem.brand}
                    onChange={(e) => setNewItem({...newItem, brand: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Cost Price *"
                    value={newItem.cost_price}
                    onChange={(e) => setNewItem({...newItem, cost_price: e.target.value})}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Selling Price *"
                    value={newItem.selling_price}
                    onChange={(e) => setNewItem({...newItem, selling_price: e.target.value})}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    placeholder="Stock Quantity *"
                    value={newItem.stock_quantity}
                    onChange={(e) => setNewItem({...newItem, stock_quantity: e.target.value})}
                    required
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="number"
                    placeholder="Minimum Stock"
                    value={newItem.min_stock}
                    onChange={(e) => setNewItem({...newItem, min_stock: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div className="flex gap-4 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
                  >
                    Add Item
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Items Table */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SKU</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                  <th className="px-6 py-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredItems.map(item => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        {item.brand && <p className="text-sm text-gray-600">{item.brand}</p>}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{item.sku}</td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="text-sm text-gray-900">{item.category}</p>
                        {item.sub_category && (
                          <p className="text-xs text-gray-600">{item.sub_category}</p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm font-medium text-gray-900">₹{item.selling_price}</p>
                      <p className="text-xs text-gray-600">Cost: ₹{item.cost_price}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <span className={`text-sm font-medium ${item.stock_quantity <= item.min_stock ? 'text-red-600' : 'text-gray-900'}`}>
                          {item.stock_quantity}
                        </span>
                        {item.stock_quantity <= item.min_stock && (
                          <svg className="w-4 h-4 text-red-500 ml-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <p className="text-xs text-gray-600">Min: {item.min_stock}</p>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        item.stock_quantity > item.min_stock 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {item.stock_quantity > item.min_stock ? 'In Stock' : 'Low Stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [ongoingInvoices, setOngoingInvoices] = useState([]);

  const handleNavigate = (view) => {
    setCurrentView(view);
  };

  return (
    <div className="App">
      {currentView === 'dashboard' && (
        <Dashboard 
          onNavigate={handleNavigate} 
          ongoingInvoices={ongoingInvoices}
          setOngoingInvoices={setOngoingInvoices}
        />
      )}
      {currentView === 'create-invoice' && (
        <CreateInvoice 
          onNavigate={handleNavigate}
          ongoingInvoices={ongoingInvoices}
          setOngoingInvoices={setOngoingInvoices}
        />
      )}
      {currentView === 'manage-items' && <ManageItems onNavigate={handleNavigate} />}
    </div>
  );
};

export default App;