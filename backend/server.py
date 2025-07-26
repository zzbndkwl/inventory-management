from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Branch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str = ""
    phone: str = ""
    manager: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BranchCreate(BaseModel):
    name: str
    address: str = ""
    phone: str = ""
    manager: str = ""

class Item(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku: str
    name: str
    category: str = ""
    sub_category: str = ""
    brand: str = ""
    cost_price: float
    selling_price: float
    stock_quantity: int = 0
    min_stock: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ItemCreate(BaseModel):
    sku: str
    name: str
    category: str = ""
    sub_category: str = ""
    brand: str = ""
    cost_price: float
    selling_price: float
    stock_quantity: int = 0
    min_stock: int = 5

class ItemUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    brand: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[int] = None
    min_stock: Optional[int] = None

class InvoiceItem(BaseModel):
    item_id: str
    sku: str
    name: str
    quantity: int
    unit_price: float
    line_total: float

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str
    branch_id: str = "main"
    customer_name: str = "Walk-in Customer"
    customer_phone: str = ""
    items: List[InvoiceItem]
    subtotal: float
    final_total: float
    payment_mode: str = "Cash"
    status: str = "completed"  # "ongoing" or "completed"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"

class InvoiceCreate(BaseModel):
    branch_id: str = "main"
    customer_name: str = "Walk-in Customer"
    customer_phone: str = ""
    items: List[dict]  # {item_id, quantity, selected_price}
    payment_mode: str = "Cash"
    status: str = "completed"  # "ongoing" or "completed"

class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    items: Optional[List[dict]] = None  # {item_id, quantity, selected_price}
    payment_mode: Optional[str] = None

class StockTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str
    branch_id: str = "main"
    transaction_type: str  # "IN", "OUT", "ADJUSTMENT"
    quantity: int
    reference_type: str  # "INVOICE", "PURCHASE", "ADJUSTMENT"
    reference_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Branch Management Routes
@api_router.post("/branches", response_model=Branch)
async def create_branch(branch: BranchCreate):
    branch_dict = branch.dict()
    branch_obj = Branch(**branch_dict)
    await db.branches.insert_one(branch_obj.dict())
    return branch_obj

@api_router.get("/branches", response_model=List[Branch])
async def get_branches():
    branches = await db.branches.find().to_list(100)
    return [Branch(**branch) for branch in branches]

@api_router.get("/branches/{branch_id}", response_model=Branch)
async def get_branch(branch_id: str):
    branch = await db.branches.find_one({"id": branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return Branch(**branch)

@api_router.put("/branches/{branch_id}", response_model=Branch)
async def update_branch(branch_id: str, branch_update: BranchCreate):
    branch = await db.branches.find_one({"id": branch_id})
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    await db.branches.update_one({"id": branch_id}, {"$set": branch_update.dict()})
    updated_branch = await db.branches.find_one({"id": branch_id})
    return Branch(**updated_branch)

@api_router.delete("/branches/{branch_id}")
async def delete_branch(branch_id: str):
    result = await db.branches.delete_one({"id": branch_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"message": "Branch deleted successfully"}

# Item Management Routes
@api_router.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    # Allow multiple items with same SKU but different prices
    item_dict = item.dict()
    item_obj = Item(**item_dict)
    await db.items.insert_one(item_obj.dict())
    return item_obj

@api_router.get("/items", response_model=List[Item])
async def get_items(search: str = Query("", description="Search by SKU, name, or category")):
    if search:
        query = {
            "$or": [
                {"sku": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}},
                {"sub_category": {"$regex": search, "$options": "i"}},
                {"brand": {"$regex": search, "$options": "i"}}
            ]
        }
    else:
        query = {}
    
    items = await db.items.find(query).limit(100).to_list(100)
    return [Item(**item) for item in items]

@api_router.get("/items/by-sku/{sku}")
async def get_items_by_sku(sku: str):
    """Get all price variants for a specific SKU"""
    items = await db.items.find({"sku": sku}).to_list(100)
    return [Item(**item) for item in items]

@api_router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: str):
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**item)

@api_router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item_update: ItemUpdate):
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = {k: v for k, v in item_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.items.update_one({"id": item_id}, {"$set": update_data})
    updated_item = await db.items.find_one({"id": item_id})
    return Item(**updated_item)

@api_router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await db.items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# Invoice Management Routes
@api_router.post("/invoices", response_model=Invoice)
async def create_invoice(invoice_data: InvoiceCreate):
    # Generate invoice number with branch prefix
    branch_prefix = invoice_data.branch_id.upper()[:3]
    count = await db.invoices.count_documents({"branch_id": invoice_data.branch_id})
    invoice_number = f"{branch_prefix}-{count + 1:06d}"
    
    invoice_items = []
    subtotal = 0
    
    # Process each item
    for item_data in invoice_data.items:
        item = await db.items.find_one({"id": item_data["item_id"]})
        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_data['item_id']} not found")
        
        # Check stock availability
        if item["stock_quantity"] < item_data["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item['name']}. Available: {item['stock_quantity']}")
        
        # Use selected price if provided, otherwise use item's selling price
        unit_price = item_data.get("selected_price", item["selling_price"])
        quantity = item_data["quantity"]
        line_total = quantity * unit_price
        
        invoice_item = InvoiceItem(
            item_id=item["id"],
            sku=item["sku"],
            name=item["name"],
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total
        )
        
        invoice_items.append(invoice_item)
        subtotal += line_total
        
        # Update stock only if invoice is completed
        if invoice_data.status == "completed":
            new_stock = item["stock_quantity"] - quantity
            await db.items.update_one(
                {"id": item["id"]},
                {"$set": {"stock_quantity": new_stock, "updated_at": datetime.utcnow()}}
            )
            
            # Record stock transaction
            stock_transaction = StockTransaction(
                item_id=item["id"],
                branch_id=invoice_data.branch_id,
                transaction_type="OUT",
                quantity=quantity,
                reference_type="INVOICE",
                reference_id=invoice_number
            )
            await db.stock_transactions.insert_one(stock_transaction.dict())
    
    # Create invoice
    invoice = Invoice(
        invoice_number=invoice_number,
        branch_id=invoice_data.branch_id,
        customer_name=invoice_data.customer_name,
        customer_phone=invoice_data.customer_phone,
        items=invoice_items,
        subtotal=subtotal,
        final_total=subtotal,  # No GST calculations
        payment_mode=invoice_data.payment_mode,
        status=invoice_data.status
    )
    
    await db.invoices.insert_one(invoice.dict())
    return invoice

@api_router.get("/invoices", response_model=List[Invoice])
async def get_invoices(
    limit: int = Query(50, le=100), 
    status: str = Query("", description="Filter by status"),
    branch_id: str = Query("", description="Filter by branch")
):
    query = {}
    if status:
        query["status"] = status
    if branch_id:
        query["branch_id"] = branch_id
    
    invoices = await db.invoices.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [Invoice(**invoice) for invoice in invoices]

@api_router.get("/invoices/ongoing", response_model=List[Invoice])
async def get_ongoing_invoices(branch_id: str = Query("", description="Filter by branch")):
    """Get all ongoing invoices"""
    query = {"status": "ongoing"}
    if branch_id:
        query["branch_id"] = branch_id
    
    invoices = await db.invoices.find(query).sort("created_at", -1).to_list(100)
    return [Invoice(**invoice) for invoice in invoices]

@api_router.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return Invoice(**invoice)

@api_router.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_ongoing_invoice(invoice_id: str, invoice_update: InvoiceUpdate):
    """Update ongoing invoice details"""
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] != "ongoing":
        raise HTTPException(status_code=400, detail="Only ongoing invoices can be edited")
    
    update_data = {}
    
    # Update basic info
    if invoice_update.customer_name is not None:
        update_data["customer_name"] = invoice_update.customer_name
    if invoice_update.customer_phone is not None:
        update_data["customer_phone"] = invoice_update.customer_phone
    if invoice_update.payment_mode is not None:
        update_data["payment_mode"] = invoice_update.payment_mode
    
    # Update items if provided
    if invoice_update.items is not None:
        invoice_items = []
        subtotal = 0
        
        for item_data in invoice_update.items:
            item = await db.items.find_one({"id": item_data["item_id"]})
            if not item:
                raise HTTPException(status_code=404, detail=f"Item {item_data['item_id']} not found")
            
            # Check stock availability
            if item["stock_quantity"] < item_data["quantity"]:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {item['name']}. Available: {item['stock_quantity']}")
            
            unit_price = item_data.get("selected_price", item["selling_price"])
            quantity = item_data["quantity"]
            line_total = quantity * unit_price
            
            invoice_item = InvoiceItem(
                item_id=item["id"],
                sku=item["sku"],
                name=item["name"],
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total
            )
            
            invoice_items.append(invoice_item)
            subtotal += line_total
        
        update_data["items"] = [item.dict() for item in invoice_items]
        update_data["subtotal"] = subtotal
        update_data["final_total"] = subtotal
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.invoices.update_one({"id": invoice_id}, {"$set": update_data})
    updated_invoice = await db.invoices.find_one({"id": invoice_id})
    return Invoice(**updated_invoice)

@api_router.put("/invoices/{invoice_id}/complete")
async def complete_invoice(invoice_id: str):
    """Convert ongoing invoice to completed and update stock"""
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] != "ongoing":
        raise HTTPException(status_code=400, detail="Invoice is not ongoing")
    
    # Update stock for all items in the invoice
    for item_data in invoice["items"]:
        item = await db.items.find_one({"id": item_data["item_id"]})
        if item:
            new_stock = item["stock_quantity"] - item_data["quantity"]
            await db.items.update_one(
                {"id": item["id"]},
                {"$set": {"stock_quantity": new_stock, "updated_at": datetime.utcnow()}}
            )
            
            # Record stock transaction
            stock_transaction = StockTransaction(
                item_id=item["id"],
                branch_id=invoice.get("branch_id", "main"),
                transaction_type="OUT",
                quantity=item_data["quantity"],
                reference_type="INVOICE",
                reference_id=invoice["invoice_number"]
            )
            await db.stock_transactions.insert_one(stock_transaction.dict())
    
    # Update invoice status
    await db.invoices.update_one(
        {"id": invoice_id},
        {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Invoice completed successfully"}

@api_router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    """Delete ongoing invoice (only ongoing invoices can be deleted)"""
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice["status"] != "ongoing":
        raise HTTPException(status_code=400, detail="Only ongoing invoices can be deleted")
    
    result = await db.invoices.delete_one({"id": invoice_id})
    return {"message": "Invoice deleted successfully"}

# Reports Routes
@api_router.get("/reports/sales")
async def get_sales_report(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    branch_id: str = Query("", description="Filter by branch")
):
    """Get sales report for date range"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    query = {
        "status": "completed",
        "created_at": {"$gte": start_dt, "$lte": end_dt}
    }
    if branch_id:
        query["branch_id"] = branch_id
    
    invoices = await db.invoices.find(query).to_list(1000)
    
    total_sales = len(invoices)
    total_revenue = sum(invoice.get("final_total", 0) for invoice in invoices)
    
    # Group by date
    daily_sales = {}
    for invoice in invoices:
        date_key = invoice["created_at"].strftime("%Y-%m-%d")
        if date_key not in daily_sales:
            daily_sales[date_key] = {"count": 0, "revenue": 0}
        daily_sales[date_key]["count"] += 1
        daily_sales[date_key]["revenue"] += invoice.get("final_total", 0)
    
    return {
        "period": f"{start_date} to {end_date}",
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "average_sale": total_revenue / total_sales if total_sales > 0 else 0,
        "daily_breakdown": daily_sales
    }

@api_router.get("/reports/inventory")
async def get_inventory_report():
    """Get current inventory status report"""
    items = await db.items.find().to_list(1000)
    
    total_items = len(items)
    total_stock_value = sum(item["stock_quantity"] * item["cost_price"] for item in items)
    low_stock_items = [item for item in items if item["stock_quantity"] <= item["min_stock"]]
    
    # Category wise breakdown
    category_breakdown = {}
    for item in items:
        category = item.get("category", "Uncategorized")
        if category not in category_breakdown:
            category_breakdown[category] = {"count": 0, "stock_value": 0, "items": []}
        category_breakdown[category]["count"] += 1
        category_breakdown[category]["stock_value"] += item["stock_quantity"] * item["cost_price"]
        category_breakdown[category]["items"].append({
            "name": item["name"],
            "sku": item["sku"],
            "stock": item["stock_quantity"],
            "value": item["stock_quantity"] * item["cost_price"]
        })
    
    return {
        "total_items": total_items,
        "total_stock_value": total_stock_value,
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
        "category_breakdown": category_breakdown
    }

@api_router.get("/reports/top-selling")
async def get_top_selling_report(
    days: int = Query(30, description="Number of days to analyze"),
    branch_id: str = Query("", description="Filter by branch")
):
    """Get top selling items report"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = {
        "status": "completed",
        "created_at": {"$gte": start_date}
    }
    if branch_id:
        query["branch_id"] = branch_id
    
    invoices = await db.invoices.find(query).to_list(1000)
    
    # Aggregate item sales
    item_sales = {}
    for invoice in invoices:
        for item in invoice.get("items", []):
            item_id = item["item_id"]
            if item_id not in item_sales:
                item_sales[item_id] = {
                    "name": item["name"],
                    "sku": item["sku"],
                    "quantity_sold": 0,
                    "revenue": 0
                }
            item_sales[item_id]["quantity_sold"] += item["quantity"]
            item_sales[item_id]["revenue"] += item["line_total"]
    
    # Sort by quantity sold
    top_items = sorted(item_sales.values(), key=lambda x: x["quantity_sold"], reverse=True)
    
    return {
        "period_days": days,
        "total_unique_items_sold": len(item_sales),
        "top_selling_items": top_items[:20]  # Top 20
    }

@api_router.get("/reports/branch-comparison")
async def get_branch_comparison_report(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """Compare performance across branches"""
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    query = {
        "status": "completed",
        "created_at": {"$gte": start_dt, "$lte": end_dt}
    }
    
    invoices = await db.invoices.find(query).to_list(1000)
    branches = await db.branches.find().to_list(100)
    
    # Create branch lookup
    branch_lookup = {branch["id"]: branch["name"] for branch in branches}
    branch_lookup["main"] = "Main Branch"  # Default branch
    
    # Aggregate by branch
    branch_stats = {}
    for invoice in invoices:
        branch_id = invoice.get("branch_id", "main")
        branch_name = branch_lookup.get(branch_id, f"Branch {branch_id}")
        
        if branch_id not in branch_stats:
            branch_stats[branch_id] = {
                "name": branch_name,
                "sales_count": 0,
                "revenue": 0,
                "items_sold": 0
            }
        
        branch_stats[branch_id]["sales_count"] += 1
        branch_stats[branch_id]["revenue"] += invoice.get("final_total", 0)
        branch_stats[branch_id]["items_sold"] += sum(item["quantity"] for item in invoice.get("items", []))
    
    # Calculate averages
    for stats in branch_stats.values():
        stats["average_sale"] = stats["revenue"] / stats["sales_count"] if stats["sales_count"] > 0 else 0
    
    return {
        "period": f"{start_date} to {end_date}",
        "branch_performance": branch_stats
    }

# Thermal Receipt Generation
@api_router.get("/invoices/{invoice_id}/thermal-receipt")
async def get_thermal_receipt(invoice_id: str):
    invoice = await db.invoices.find_one({"id": invoice_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    invoice_obj = Invoice(**invoice)
    
    # Get branch name
    branch_name = "Main Branch"
    if invoice_obj.branch_id != "main":
        branch = await db.branches.find_one({"id": invoice_obj.branch_id})
        if branch:
            branch_name = branch["name"]
    
    # Generate thermal receipt format (48 characters wide)
    receipt_lines = []
    receipt_lines.append("=" * 48)
    receipt_lines.append("           SPARE PARTS STORE           ")
    receipt_lines.append(f"            {branch_name.center(20)}            ")
    receipt_lines.append("=" * 48)
    receipt_lines.append(f"Invoice: {invoice_obj.invoice_number}")
    receipt_lines.append(f"Date: {invoice_obj.created_at.strftime('%d/%m/%Y %H:%M')}")
    receipt_lines.append(f"Customer: {invoice_obj.customer_name}")
    if invoice_obj.customer_phone:
        receipt_lines.append(f"Phone: {invoice_obj.customer_phone}")
    receipt_lines.append("-" * 48)
    
    # Items
    receipt_lines.append("ITEM                QTY   RATE    AMOUNT")
    receipt_lines.append("-" * 48)
    
    for item in invoice_obj.items:
        name = item.name[:20]
        line = f"{name:<20} {item.quantity:>3} {item.unit_price:>6.2f} {item.line_total:>8.2f}"
        receipt_lines.append(line)
    
    receipt_lines.append("-" * 48)
    receipt_lines.append(f"{'TOTAL:':<32}{invoice_obj.final_total:>15.2f}")
    receipt_lines.append("=" * 48)
    receipt_lines.append(f"Payment Mode: {invoice_obj.payment_mode}")
    receipt_lines.append(f"Status: {invoice_obj.status.upper()}")
    receipt_lines.append("")
    receipt_lines.append("        Thank you for your business!")
    receipt_lines.append("=" * 48)
    
    return {"receipt": "\n".join(receipt_lines)}

# Dashboard and Reports
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(branch_id: str = Query("", description="Filter by branch")):
    # Build query for branch filtering
    branch_query = {}
    if branch_id:
        branch_query["branch_id"] = branch_id
    
    # Get basic statistics
    total_items = await db.items.count_documents({})
    total_invoices = await db.invoices.count_documents({"status": "completed", **branch_query})
    ongoing_invoices = await db.invoices.count_documents({"status": "ongoing", **branch_query})
    low_stock_items = await db.items.count_documents({"$expr": {"$lte": ["$stock_quantity", "$min_stock"]}})
    
    # Today's sales (only completed invoices)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = await db.invoices.find({
        "created_at": {"$gte": today_start},
        "status": "completed",
        **branch_query
    }).to_list(1000)
    today_revenue = sum(invoice.get("final_total", 0) for invoice in today_sales)
    
    return {
        "total_items": total_items,
        "total_invoices": total_invoices,
        "ongoing_invoices": ongoing_invoices,
        "low_stock_items": low_stock_items,
        "today_invoices": len(today_sales),
        "today_revenue": today_revenue
    }

@api_router.get("/items/low-stock")
async def get_low_stock_items():
    items = await db.items.find({"$expr": {"$lte": ["$stock_quantity", "$min_stock"]}}).to_list(100)
    return [Item(**item) for item in items]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()