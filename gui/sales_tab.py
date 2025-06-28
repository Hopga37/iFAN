#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sales management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import uuid
from decimal import Decimal

from models import Sale, SaleItem, Customer
from config import BUSINESS_RULES

class SalesTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup sales tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Quick Sale tab
        self.setup_quick_sale_tab()
        
        # Sales History tab
        self.setup_sales_history_tab()
        
        # Customers tab
        self.setup_customers_tab()
        
        # Installment tab
        self.setup_installment_tab()
    
    def setup_quick_sale_tab(self):
        """Setup quick sale tab"""
        quick_sale_frame = ttk.Frame(self.notebook)
        self.notebook.add(quick_sale_frame, text="Bán Hàng Nhanh")
        
        # Main layout with two columns
        left_frame = ttk.Frame(quick_sale_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
        
        right_frame = ttk.Frame(quick_sale_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 10), pady=10)
        
        # Left side - Product search and selection
        search_frame = ttk.LabelFrame(left_frame, text="Tìm kiếm sản phẩm", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Barcode/IMEI search
        ttk.Label(search_frame, text="Quét mã vạch / IMEI:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_var = tk.StringVar()
        self.barcode_var.trace('w', self.on_barcode_scan)
        barcode_entry = ttk.Entry(search_frame, textvariable=self.barcode_var, width=40)
        barcode_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        barcode_entry.bind('<Return>', self.add_product_to_cart)
        
        # Product search
        ttk.Label(search_frame, text="Tìm sản phẩm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.on_product_search)
        product_search_entry = ttk.Entry(search_frame, textvariable=self.product_search_var, width=40)
        product_search_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Available products list
        products_frame = ttk.LabelFrame(left_frame, text="Sản phẩm có sẵn", padding=10)
        products_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Products treeview
        self.available_products_tree = ttk.Treeview(products_frame,
                                                   columns=('id', 'name', 'imei', 'price', 'stock'),
                                                   show='headings', height=10)
        
        self.available_products_tree.heading('id', text='ID')
        self.available_products_tree.heading('name', text='Sản phẩm')
        self.available_products_tree.heading('imei', text='IMEI')
        self.available_products_tree.heading('price', text='Giá bán')
        self.available_products_tree.heading('stock', text='Tồn kho')
        
        self.available_products_tree.column('id', width=50)
        self.available_products_tree.column('name', width=250)
        self.available_products_tree.column('imei', width=150)
        self.available_products_tree.column('price', width=100)
        self.available_products_tree.column('stock', width=80)
        
        self.available_products_tree.pack(fill=tk.BOTH, expand=True)
        self.available_products_tree.bind('<Double-1>', self.add_selected_product_to_cart)
        
        # Add to cart button
        ttk.Button(products_frame, text="➕ Thêm vào giỏ hàng", 
                  command=self.add_selected_product_to_cart).pack(pady=5)
        
        # Right side - Cart and checkout
        cart_frame = ttk.LabelFrame(right_frame, text="Giỏ hàng", padding=10)
        cart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Cart items
        self.cart_tree = ttk.Treeview(cart_frame,
                                     columns=('product', 'imei', 'qty', 'price', 'total'),
                                     show='headings', height=8)
        
        self.cart_tree.heading('product', text='Sản phẩm')
        self.cart_tree.heading('imei', text='IMEI')
        self.cart_tree.heading('qty', text='SL')
        self.cart_tree.heading('price', text='Đơn giá')
        self.cart_tree.heading('total', text='Thành tiền')
        
        self.cart_tree.column('product', width=200)
        self.cart_tree.column('imei', width=120)
        self.cart_tree.column('qty', width=40)
        self.cart_tree.column('price', width=80)
        self.cart_tree.column('total', width=100)
        
        self.cart_tree.pack(fill=tk.BOTH, expand=True)
        
        # Cart controls
        cart_controls = ttk.Frame(cart_frame)
        cart_controls.pack(fill=tk.X, pady=5)
        
        ttk.Button(cart_controls, text="🗑️ Xóa", 
                  command=self.remove_from_cart).pack(side=tk.LEFT, padx=2)
        ttk.Button(cart_controls, text="🗑️ Xóa tất cả", 
                  command=self.clear_cart).pack(side=tk.LEFT, padx=2)
        
        # Checkout frame
        checkout_frame = ttk.LabelFrame(right_frame, text="Thanh toán", padding=10)
        checkout_frame.pack(fill=tk.X)
        
        # Customer selection
        ttk.Label(checkout_frame, text="Khách hàng:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(checkout_frame, textvariable=self.customer_var, width=25)
        customer_combo.grid(row=0, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Load customers
        self.load_customers_combo(customer_combo)
        
        ttk.Button(checkout_frame, text="➕", 
                  command=self.add_customer).grid(row=0, column=2, pady=2, padx=(5, 0))
        
        # Totals
        ttk.Label(checkout_frame, text="Tạm tính:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.subtotal_label = ttk.Label(checkout_frame, text="0 VNĐ")
        self.subtotal_label.grid(row=1, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(checkout_frame, text="Giảm giá:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.discount_var = tk.StringVar(value="0")
        discount_entry = ttk.Entry(checkout_frame, textvariable=self.discount_var, width=15)
        discount_entry.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        discount_entry.bind('<KeyRelease>', self.calculate_total)
        
        ttk.Label(checkout_frame, text="Thuế VAT:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.tax_label = ttk.Label(checkout_frame, text="0 VNĐ")
        self.tax_label.grid(row=3, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(checkout_frame, text="Tổng cộng:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.total_label = ttk.Label(checkout_frame, text="0 VNĐ", 
                                    style="Success.TLabel", font=('Arial', 10, 'bold'))
        self.total_label.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Payment method
        ttk.Label(checkout_frame, text="Thanh toán:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.payment_method_var = tk.StringVar(value="cash")
        payment_combo = ttk.Combobox(checkout_frame, textvariable=self.payment_method_var,
                                    values=["cash", "card", "transfer", "mixed"], width=22, state="readonly")
        payment_combo.grid(row=5, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Paid amount
        ttk.Label(checkout_frame, text="Tiền nhận:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.paid_amount_var = tk.StringVar()
        paid_entry = ttk.Entry(checkout_frame, textvariable=self.paid_amount_var, width=15)
        paid_entry.grid(row=6, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        paid_entry.bind('<KeyRelease>', self.calculate_change)
        
        # Change
        ttk.Label(checkout_frame, text="Tiền thối:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.change_label = ttk.Label(checkout_frame, text="0 VNĐ")
        self.change_label.grid(row=7, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        # Checkout buttons
        btn_frame = ttk.Frame(checkout_frame)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        ttk.Button(btn_frame, text="💰 Thanh toán", 
                  command=self.process_sale).pack(side=tk.TOP, fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="📋 Tạm lưu", 
                  command=self.save_draft).pack(side=tk.TOP, fill=tk.X, pady=2)
        
        # Initialize cart items list
        self.cart_items = []
        
        # Focus on barcode entry
        barcode_entry.focus_set()
    
    def setup_sales_history_tab(self):
        """Setup sales history tab"""
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="Lịch Sử Bán Hàng")
        
        # Top controls
        top_frame = ttk.Frame(history_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Date filter
        date_frame = ttk.LabelFrame(top_frame, text="Lọc theo ngày", padding=10)
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="Từ ngày:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.from_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=12)
        from_date_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(date_frame, text="Đến ngày:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=12)
        to_date_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(date_frame, text="🔍 Lọc", 
                  command=self.filter_sales).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Search
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm", padding=10)
        search_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(search_frame, text="Số hóa đơn / Khách hàng:").pack(anchor=tk.W)
        self.sales_search_var = tk.StringVar()
        self.sales_search_var.trace('w', self.on_sales_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.sales_search_var, width=30)
        search_entry.pack(pady=5)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="👁️ Xem chi tiết", 
                  command=self.view_sale_details).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🖨️ In hóa đơn", 
                  command=self.print_invoice).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="↩️ Hoàn trả", 
                  command=self.process_return).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_sales).pack(pady=2, fill=tk.X)
        
        # Sales treeview
        tree_frame = ttk.Frame(history_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.sales_tree = ttk.Treeview(tree_frame,
                                      columns=('id', 'invoice', 'date', 'customer', 'staff',
                                             'total', 'paid', 'method', 'status'),
                                      show='headings',
                                      yscrollcommand=v_scrollbar.set,
                                      xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.sales_tree.yview)
        h_scrollbar.config(command=self.sales_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'invoice': ('Số HĐ', 120),
            'date': ('Ngày bán', 120),
            'customer': ('Khách hàng', 150),
            'staff': ('Nhân viên', 120),
            'total': ('Tổng tiền', 100),
            'paid': ('Đã thanh toán', 120),
            'method': ('Hình thức', 100),
            'status': ('Trạng thái', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.sales_tree.heading(col, text=heading)
            self.sales_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.sales_tree.bind('<Double-1>', lambda e: self.view_sale_details())
    
    def setup_customers_tab(self):
        """Setup customers management tab"""
        customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(customers_frame, text="Khách Hàng")
        
        # Top controls
        top_frame = ttk.Frame(customers_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Search
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm khách hàng", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="Tên / SĐT:").pack(side=tk.LEFT, padx=(0, 5))
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace('w', self.on_customer_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var, width=40)
        search_entry.pack(side=tk.LEFT)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="➕ Thêm KH", 
                  command=self.add_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_customer).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="👁️ Xem lịch sử", 
                  command=self.view_customer_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="💰 Công nợ", 
                  command=self.view_customer_debt).pack(side=tk.LEFT, padx=2)
        
        # Customers treeview
        tree_frame = ttk.Frame(customers_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.customers_tree = ttk.Treeview(tree_frame,
                                          columns=('id', 'name', 'phone', 'email', 'address', 
                                                 'total_purchases', 'debt'),
                                          show='headings')
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'name': ('Tên khách hàng', 200),
            'phone': ('Số điện thoại', 120),
            'email': ('Email', 150),
            'address': ('Địa chỉ', 200),
            'total_purchases': ('Tổng mua', 100),
            'debt': ('Công nợ', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.customers_tree.heading(col, text=heading)
            self.customers_tree.column(col, width=width, minwidth=50)
        
        self.customers_tree.pack(fill=tk.BOTH, expand=True)
        self.customers_tree.bind('<Double-1>', lambda e: self.edit_customer())
    
    def setup_installment_tab(self):
        """Setup installment sales tab"""
        installment_frame = ttk.Frame(self.notebook)
        self.notebook.add(installment_frame, text="Trả Góp")
        
        # Top controls
        top_frame = ttk.Frame(installment_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        ttk.Button(top_frame, text="➕ Tạo hợp đồng trả góp", 
                  command=self.create_installment_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="💰 Thu góp", 
                  command=self.collect_installment).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="📋 Xem chi tiết", 
                  command=self.view_installment_details).pack(side=tk.LEFT, padx=5)
        
        # Installment contracts treeview
        tree_frame = ttk.Frame(installment_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.installment_tree = ttk.Treeview(tree_frame,
                                           columns=('id', 'contract_no', 'customer', 'product',
                                                  'total_amount', 'monthly_payment', 'remaining',
                                                  'next_payment', 'status'),
                                           show='headings')
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'contract_no': ('Số HĐ', 120),
            'customer': ('Khách hàng', 150),
            'product': ('Sản phẩm', 200),
            'total_amount': ('Tổng tiền', 100),
            'monthly_payment': ('Trả hàng tháng', 120),
            'remaining': ('Còn lại', 100),
            'next_payment': ('Kỳ tới', 100),
            'status': ('Trạng thái', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.installment_tree.heading(col, text=heading)
            self.installment_tree.column(col, width=width, minwidth=50)
        
        self.installment_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Load all data"""
        self.refresh_available_products()
        self.refresh_sales()
        self.refresh_customers()
        self.refresh_installments()
    
    def refresh_available_products(self):
        """Refresh available products list"""
        # Clear existing items
        for item in self.available_products_tree.get_children():
            self.available_products_tree.delete(item)
        
        # Load available inventory
        query = """
        SELECT i.*, p.name, p.brand, p.model, p.selling_price
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.status = 'available' AND p.is_active = 1
        ORDER BY p.name
        """
        
        items = self.db_manager.fetch_all(query)
        
        for item in items:
            product_name = item['name']
            if item['brand']:
                product_name += f" ({item['brand']})"
            
            # Get stock count for this product
            stock_query = """
            SELECT COUNT(*) as count FROM inventory 
            WHERE product_id = ? AND status = 'available'
            """
            stock_result = self.db_manager.fetch_one(stock_query, (item['product_id'],))
            stock_count = stock_result['count'] if stock_result else 0
            
            self.available_products_tree.insert('', 'end', values=(
                item['id'],
                product_name,
                item['imei'] or '',
                f"{(item['selling_price'] or item['selling_price'] or 0):,.0f}",
                stock_count
            ))
    
    def refresh_sales(self):
        """Refresh sales history"""
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Load sales
        query = """
        SELECT s.*, c.name as customer_name, st.full_name as staff_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN staff st ON s.staff_id = st.id
        ORDER BY s.sale_date DESC
        LIMIT 500
        """
        
        sales = self.db_manager.fetch_all(query)
        
        for sale in sales:
            sale_date = datetime.fromisoformat(sale['sale_date']).strftime('%d/%m/%Y %H:%M')
            
            self.sales_tree.insert('', 'end', values=(
                sale['id'],
                sale['invoice_number'],
                sale_date,
                sale['customer_name'] or 'Khách lẻ',
                sale['staff_name'] or '',
                f"{sale['total_amount']:,.0f}",
                f"{sale['paid_amount']:,.0f}",
                sale['payment_method'],
                sale['payment_status']
            ))
    
    def refresh_customers(self):
        """Refresh customers list"""
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Load customers with purchase totals and debts
        query = """
        SELECT c.*,
               COALESCE(SUM(s.total_amount), 0) as total_purchases,
               COALESCE(SUM(d.amount), 0) as total_debt
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        LEFT JOIN debts d ON c.id = d.debtor_id AND d.debtor_type = 'customer' AND d.status = 'outstanding'
        GROUP BY c.id
        ORDER BY c.name
        """
        
        customers = self.db_manager.fetch_all(query)
        
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer['id'],
                customer['name'],
                customer['phone'] or '',
                customer['email'] or '',
                customer['address'] or '',
                f"{customer['total_purchases']:,.0f}",
                f"{customer['total_debt']:,.0f}" if customer['total_debt'] > 0 else "0"
            ))
    
    def refresh_installments(self):
        """Refresh installment contracts"""
        # Clear existing items
        for item in self.installment_tree.get_children():
            self.installment_tree.delete(item)
        
        # Load installment sales
        query = """
        SELECT s.*, c.name as customer_name,
               GROUP_CONCAT(p.name, ', ') as products
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN sale_items si ON s.id = si.sale_id
        JOIN products p ON si.product_id = p.id
        WHERE s.is_installment = 1
        GROUP BY s.id
        ORDER BY s.sale_date DESC
        """
        
        installments = self.db_manager.fetch_all(query)
        
        for installment in installments:
            remaining = installment['total_amount'] - installment['paid_amount']
            next_payment_date = "N/A"  # This would need more complex calculation
            
            self.installment_tree.insert('', 'end', values=(
                installment['id'],
                installment['invoice_number'],
                installment['customer_name'],
                installment['products'][:50] + "..." if len(installment['products']) > 50 else installment['products'],
                f"{installment['total_amount']:,.0f}",
                f"{installment['monthly_payment']:,.0f}",
                f"{remaining:,.0f}",
                next_payment_date,
                installment['payment_status']
            ))
    
    def load_customers_combo(self, combo):
        """Load customers into combobox"""
        customers = self.db_manager.fetch_all("SELECT id, name, phone FROM customers ORDER BY name")
        combo['values'] = [""] + [f"{c['id']} - {c['name']} ({c['phone']})" for c in customers if c['phone']]
    
    def on_barcode_scan(self, *args):
        """Handle barcode scan"""
        barcode = self.barcode_var.get()
        if len(barcode) >= 10:  # Minimum barcode length
            self.search_product_by_barcode(barcode)
    
    def search_product_by_barcode(self, barcode):
        """Search product by barcode or IMEI"""
        # Search by barcode
        product = self.db_manager.fetch_one(
            """SELECT i.*, p.name, p.brand, p.model, p.selling_price
               FROM inventory i
               JOIN products p ON i.product_id = p.id
               WHERE (p.barcode = ? OR i.imei = ?) AND i.status = 'available'
               LIMIT 1""",
            (barcode, barcode)
        )
        
        if product:
            # Highlight the product in available products tree
            for item in self.available_products_tree.get_children():
                values = self.available_products_tree.item(item)['values']
                if str(values[0]) == str(product['id']) or values[2] == barcode:
                    self.available_products_tree.selection_set(item)
                    self.available_products_tree.see(item)
                    break
    
    def on_product_search(self, *args):
        """Handle product search"""
        search_term = self.product_search_var.get().lower()
        
        if not search_term:
            self.refresh_available_products()
            return
        
        # Clear existing items
        for item in self.available_products_tree.get_children():
            self.available_products_tree.delete(item)
        
        # Search products
        query = """
        SELECT i.*, p.name, p.brand, p.model, p.selling_price
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE i.status = 'available' AND p.is_active = 1 AND (
            LOWER(p.name) LIKE ? OR
            LOWER(p.brand) LIKE ? OR
            LOWER(p.model) LIKE ? OR
            i.imei LIKE ?
        )
        ORDER BY p.name
        """
        
        search_pattern = f"%{search_term}%"
        items = self.db_manager.fetch_all(query, (search_pattern, search_pattern, 
                                                search_pattern, search_pattern))
        
        for item in items:
            product_name = item['name']
            if item['brand']:
                product_name += f" ({item['brand']})"
            
            self.available_products_tree.insert('', 'end', values=(
                item['id'],
                product_name,
                item['imei'] or '',
                f"{(item['selling_price'] or 0):,.0f}",
                "1"  # Available quantity for this specific item
            ))
    
    def add_product_to_cart(self, event=None):
        """Add product to cart by barcode/IMEI"""
        barcode = self.barcode_var.get().strip()
        if not barcode:
            return
        
        # Find product by barcode/IMEI
        item = self.db_manager.fetch_one(
            """SELECT i.*, p.name, p.brand, p.model, p.selling_price
               FROM inventory i
               JOIN products p ON i.product_id = p.id
               WHERE (p.barcode = ? OR i.imei = ?) AND i.status = 'available'
               LIMIT 1""",
            (barcode, barcode)
        )
        
        if item:
            self.add_item_to_cart(item)
            self.barcode_var.set("")  # Clear barcode entry
        else:
            messagebox.showwarning("Không tìm thấy", f"Không tìm thấy sản phẩm với mã: {barcode}")
    
    def add_selected_product_to_cart(self, event=None):
        """Add selected product to cart"""
        selection = self.available_products_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm!")
            return
        
        item_values = self.available_products_tree.item(selection[0])['values']
        inventory_id = item_values[0]
        
        # Get full item details
        item = self.db_manager.fetch_one(
            """SELECT i.*, p.name, p.brand, p.model, p.selling_price
               FROM inventory i
               JOIN products p ON i.product_id = p.id
               WHERE i.id = ?""",
            (inventory_id,)
        )
        
        if item:
            self.add_item_to_cart(item)
    
    def add_item_to_cart(self, item):
        """Add item to cart"""
        # Check if item already in cart (for IMEI tracked items)
        if item['imei']:
            for cart_item in self.cart_items:
                if cart_item.get('imei') == item['imei']:
                    messagebox.showwarning("Cảnh báo", "Sản phẩm này đã có trong giỏ hàng!")
                    return
        
        # Create cart item
        cart_item = {
            'inventory_id': item['id'],
            'product_id': item['product_id'],
            'name': item['name'],
            'brand': item['brand'],
            'imei': item['imei'],
            'price': item['selling_price'] or 0,
            'quantity': 1
        }
        
        # Add to cart
        self.cart_items.append(cart_item)
        self.update_cart_display()
        self.calculate_total()
    
    def update_cart_display(self):
        """Update cart treeview"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for cart_item in self.cart_items:
            product_name = cart_item['name']
            if cart_item['brand']:
                product_name += f" ({cart_item['brand']})"
            
            total = cart_item['price'] * cart_item['quantity']
            
            self.cart_tree.insert('', 'end', values=(
                product_name,
                cart_item['imei'] or '',
                cart_item['quantity'],
                f"{cart_item['price']:,.0f}",
                f"{total:,.0f}"
            ))
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return
        
        # Get selected index
        selected_index = self.cart_tree.index(selection[0])
        
        # Remove from cart items
        if 0 <= selected_index < len(self.cart_items):
            self.cart_items.pop(selected_index)
            self.update_cart_display()
            self.calculate_total()
    
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items and messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa tất cả sản phẩm?"):
            self.cart_items.clear()
            self.update_cart_display()
            self.calculate_total()
    
    def calculate_total(self, event=None):
        """Calculate total amount"""
        if not self.cart_items:
            self.subtotal_label.config(text="0 VNĐ")
            self.tax_label.config(text="0 VNĐ")
            self.total_label.config(text="0 VNĐ")
            return
        
        # Calculate subtotal
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
        
        # Calculate discount
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
        
        # Calculate tax
        tax = (subtotal - discount) * BUSINESS_RULES['VAT_RATE']
        
        # Calculate total
        total = subtotal - discount + tax
        
        # Update labels
        self.subtotal_label.config(text=f"{subtotal:,.0f} VNĐ")
        self.tax_label.config(text=f"{tax:,.0f} VNĐ")
        self.total_label.config(text=f"{total:,.0f} VNĐ")
        
        # Update paid amount if not manually entered
        if not self.paid_amount_var.get():
            self.paid_amount_var.set(f"{total:.0f}")
        
        self.calculate_change()
    
    def calculate_change(self, event=None):
        """Calculate change amount"""
        try:
            total_text = self.total_label.cget("text").replace(" VNĐ", "").replace(",", "")
            total = float(total_text) if total_text != "0" else 0
            
            paid = float(self.paid_amount_var.get() or 0)
            change = paid - total
            
            self.change_label.config(text=f"{change:,.0f} VNĐ")
        except ValueError:
            self.change_label.config(text="0 VNĐ")
    
    def process_sale(self):
        """Process the sale"""
        if not self.cart_items:
            messagebox.showwarning("Cảnh báo", "Giỏ hàng trống!")
            return
        
        try:
            # Get customer ID
            customer_id = None
            if self.customer_var.get():
                customer_id = int(self.customer_var.get().split(' - ')[0])
            
            # Calculate totals
            subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
            discount = float(self.discount_var.get() or 0)
            tax = (subtotal - discount) * BUSINESS_RULES['VAT_RATE']
            total = subtotal - discount + tax
            paid = float(self.paid_amount_var.get() or 0)
            
            # Validate payment
            if paid < total:
                if not messagebox.askyesno("Xác nhận", 
                    f"Khách hàng chưa thanh toán đủ (thiếu {total-paid:,.0f} VNĐ). Vẫn tiếp tục?"):
                    return
            
            # Create sale record
            invoice_number = f"HD{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            sale_data = {
                'invoice_number': invoice_number,
                'customer_id': customer_id,
                'staff_id': self.current_user['id'],
                'sale_date': datetime.now().isoformat(),
                'subtotal': subtotal,
                'discount_amount': discount,
                'tax_amount': tax,
                'total_amount': total,
                'paid_amount': paid,
                'payment_method': self.payment_method_var.get(),
                'payment_status': 'paid' if paid >= total else 'partial',
                'sale_type': 'retail',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert sale
            columns = ', '.join(sale_data.keys())
            placeholders = ', '.join(['?' for _ in sale_data])
            query = f"INSERT INTO sales ({columns}) VALUES ({placeholders})"
            
            cursor = self.db_manager.execute_query(query, list(sale_data.values()))
            sale_id = cursor.lastrowid
            
            # Insert sale items and update inventory
            for cart_item in self.cart_items:
                # Insert sale item
                sale_item_data = {
                    'sale_id': sale_id,
                    'inventory_id': cart_item['inventory_id'],
                    'product_id': cart_item['product_id'],
                    'imei': cart_item['imei'],
                    'quantity': cart_item['quantity'],
                    'unit_price': cart_item['price'],
                    'discount_amount': 0,
                    'total_price': cart_item['price'] * cart_item['quantity'],
                    'warranty_months': BUSINESS_RULES['DEFAULT_WARRANTY_MONTHS'],
                    'created_at': datetime.now().isoformat()
                }
                
                columns = ', '.join(sale_item_data.keys())
                placeholders = ', '.join(['?' for _ in sale_item_data])
                query = f"INSERT INTO sale_items ({columns}) VALUES ({placeholders})"
                self.db_manager.execute_query(query, list(sale_item_data.values()))
                
                # Update inventory status
                self.db_manager.execute_query(
                    "UPDATE inventory SET status = 'sold', updated_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), cart_item['inventory_id'])
                )
                
                # Create warranty record if applicable
                if cart_item['imei']:
                    warranty_data = {
                        'warranty_number': f"BH{datetime.now().strftime('%Y%m%d%H%M%S')}{cart_item['inventory_id']}",
                        'imei': cart_item['imei'],
                        'product_id': cart_item['product_id'],
                        'customer_id': customer_id,
                        'sale_id': sale_id,
                        'warranty_type': 'product',
                        'start_date': date.today().isoformat(),
                        'end_date': (date.today().replace(
                            year=date.today().year + (date.today().month + BUSINESS_RULES['DEFAULT_WARRANTY_MONTHS'] - 1) // 12,
                            month=(date.today().month + BUSINESS_RULES['DEFAULT_WARRANTY_MONTHS'] - 1) % 12 + 1
                        )).isoformat(),
                        'status': 'active',
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    from utils.qr_utils import generate_qr_code
                    qr_code = generate_qr_code(f"WARRANTY:{warranty_data['warranty_number']}")
                    warranty_data['qr_code'] = qr_code
                    
                    columns = ', '.join(warranty_data.keys())
                    placeholders = ', '.join(['?' for _ in warranty_data])
                    query = f"INSERT INTO warranties ({columns}) VALUES ({placeholders})"
                    self.db_manager.execute_query(query, list(warranty_data.values()))
            
            # Create transaction record
            transaction_data = {
                'transaction_type': 'income',
                'amount': paid,
                'description': f'Bán hàng - {invoice_number}',
                'reference_id': sale_id,
                'reference_type': 'sale',
                'payment_method': self.payment_method_var.get(),
                'staff_id': self.current_user['id'],
                'transaction_date': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            columns = ', '.join(transaction_data.keys())
            placeholders = ', '.join(['?' for _ in transaction_data])
            query = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
            self.db_manager.execute_query(query, list(transaction_data.values()))
            
            # Create debt record if not fully paid
            if paid < total:
                debt_data = {
                    'debtor_type': 'customer',
                    'debtor_id': customer_id,
                    'amount': total - paid,
                    'description': f'Nợ từ hóa đơn {invoice_number}',
                    'reference_id': sale_id,
                    'reference_type': 'sale',
                    'due_date': (date.today().replace(day=date.today().day + 30)).isoformat(),
                    'status': 'outstanding',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                columns = ', '.join(debt_data.keys())
                placeholders = ', '.join(['?' for _ in debt_data])
                query = f"INSERT INTO debts ({columns}) VALUES ({placeholders})"
                self.db_manager.execute_query(query, list(debt_data.values()))
            
            messagebox.showinfo("Thành công", f"Đã tạo hóa đơn {invoice_number}!")
            
            # Print receipt
            if messagebox.askyesno("In hóa đơn", "Bạn có muốn in hóa đơn không?"):
                self.print_receipt(sale_id)
            
            # Clear cart and refresh
            self.cart_items.clear()
            self.update_cart_display()
            self.calculate_total()
            self.refresh_available_products()
            self.refresh_sales()
            
            # Reset form
            self.customer_var.set("")
            self.discount_var.set("0")
            self.paid_amount_var.set("")
            self.barcode_var.set("")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý bán hàng: {e}")
    
    def print_receipt(self, sale_id):
        """Print sales receipt"""
        try:
            from utils.print_utils import print_sales_receipt
            print_sales_receipt(self.db_manager, sale_id)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in hóa đơn: {e}")
    
    def save_draft(self):
        """Save sale as draft"""
        # This would implement saving the current cart as a draft
        messagebox.showinfo("Thông báo", "Chức năng tạm lưu sẽ được phát triển!")
    
    def on_sales_search(self, *args):
        """Handle sales search"""
        search_term = self.sales_search_var.get().lower()
        
        if not search_term:
            self.refresh_sales()
            return
        
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Search sales
        query = """
        SELECT s.*, c.name as customer_name, st.full_name as staff_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN staff st ON s.staff_id = st.id
        WHERE LOWER(s.invoice_number) LIKE ? OR LOWER(c.name) LIKE ?
        ORDER BY s.sale_date DESC
        LIMIT 100
        """
        
        search_pattern = f"%{search_term}%"
        sales = self.db_manager.fetch_all(query, (search_pattern, search_pattern))
        
        for sale in sales:
            sale_date = datetime.fromisoformat(sale['sale_date']).strftime('%d/%m/%Y %H:%M')
            
            self.sales_tree.insert('', 'end', values=(
                sale['id'],
                sale['invoice_number'],
                sale_date,
                sale['customer_name'] or 'Khách lẻ',
                sale['staff_name'] or '',
                f"{sale['total_amount']:,.0f}",
                f"{sale['paid_amount']:,.0f}",
                sale['payment_method'],
                sale['payment_status']
            ))
    
    def filter_sales(self):
        """Filter sales by date range"""
        from_date = self.from_date_var.get()
        to_date = self.to_date_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ khoảng thời gian!")
            return
        
        # Clear existing items
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Filter sales
        query = """
        SELECT s.*, c.name as customer_name, st.full_name as staff_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        LEFT JOIN staff st ON s.staff_id = st.id
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
        ORDER BY s.sale_date DESC
        """
        
        sales = self.db_manager.fetch_all(query, (from_date, to_date))
        
        for sale in sales:
            sale_date = datetime.fromisoformat(sale['sale_date']).strftime('%d/%m/%Y %H:%M')
            
            self.sales_tree.insert('', 'end', values=(
                sale['id'],
                sale['invoice_number'],
                sale_date,
                sale['customer_name'] or 'Khách lẻ',
                sale['staff_name'] or '',
                f"{sale['total_amount']:,.0f}",
                f"{sale['paid_amount']:,.0f}",
                sale['payment_method'],
                sale['payment_status']
            ))
    
    def view_sale_details(self):
        """View sale details"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn!")
            return
        
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        
        # Show sale details dialog
        self.show_sale_details_dialog(sale_id)
    
    def show_sale_details_dialog(self, sale_id):
        """Show sale details dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Chi tiết hóa đơn")
        dialog.geometry("800x600")
        dialog.transient(self.frame)
        
        # Load sale data
        sale = self.db_manager.fetch_one(
            """SELECT s.*, c.name as customer_name, c.phone as customer_phone,
                      st.full_name as staff_name
               FROM sales s
               LEFT JOIN customers c ON s.customer_id = c.id
               LEFT JOIN staff st ON s.staff_id = st.id
               WHERE s.id = ?""",
            (sale_id,)
        )
        
        if not sale:
            messagebox.showerror("Lỗi", "Không tìm thấy hóa đơn!")
            dialog.destroy()
            return
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Sale information
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin hóa đơn", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_data = [
            ("Số hóa đơn:", sale['invoice_number']),
            ("Ngày bán:", datetime.fromisoformat(sale['sale_date']).strftime('%d/%m/%Y %H:%M')),
            ("Khách hàng:", sale['customer_name'] or 'Khách lẻ'),
            ("SĐT:", sale['customer_phone'] or ''),
            ("Nhân viên:", sale['staff_name'] or ''),
            ("Tổng tiền:", f"{sale['total_amount']:,.0f} VNĐ"),
            ("Đã thanh toán:", f"{sale['paid_amount']:,.0f} VNĐ"),
            ("Phương thức:", sale['payment_method']),
            ("Trạng thái:", sale['payment_status'])
        ]
        
        for i, (label, value) in enumerate(info_data):
            row, col = divmod(i, 2)
            ttk.Label(info_frame, text=label).grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Sale items
        items_frame = ttk.LabelFrame(main_frame, text="Chi tiết sản phẩm", padding=10)
        items_frame.pack(fill=tk.BOTH, expand=True)
        
        items_tree = ttk.Treeview(items_frame,
                                 columns=('product', 'imei', 'qty', 'price', 'total'),
                                 show='headings')
        
        items_tree.heading('product', text='Sản phẩm')
        items_tree.heading('imei', text='IMEI')
        items_tree.heading('qty', text='SL')
        items_tree.heading('price', text='Đơn giá')
        items_tree.heading('total', text='Thành tiền')
        
        items_tree.column('product', width=300)
        items_tree.column('imei', width=150)
        items_tree.column('qty', width=50)
        items_tree.column('price', width=100)
        items_tree.column('total', width=100)
        
        # Load sale items
        sale_items = self.db_manager.fetch_all(
            """SELECT si.*, p.name, p.brand, p.model
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               WHERE si.sale_id = ?""",
            (sale_id,)
        )
        
        for item in sale_items:
            product_name = item['name']
            if item['brand']:
                product_name += f" ({item['brand']})"
            
            items_tree.insert('', 'end', values=(
                product_name,
                item['imei'] or '',
                item['quantity'],
                f"{item['unit_price']:,.0f}",
                f"{item['total_price']:,.0f}"
            ))
        
        items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ In hóa đơn", 
                  command=lambda: self.print_receipt(sale_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Đóng", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def print_invoice(self):
        """Print selected invoice"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn!")
            return
        
        item = self.sales_tree.item(selection[0])
        sale_id = item['values'][0]
        self.print_receipt(sale_id)
    
    def process_return(self):
        """Process return/refund"""
        selection = self.sales_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng hoàn trả sẽ được phát triển!")
    
    def on_customer_search(self, *args):
        """Handle customer search"""
        search_term = self.customer_search_var.get().lower()
        
        if not search_term:
            self.refresh_customers()
            return
        
        # Clear existing items
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # Search customers
        query = """
        SELECT c.*,
               COALESCE(SUM(s.total_amount), 0) as total_purchases,
               COALESCE(SUM(d.amount), 0) as total_debt
        FROM customers c
        LEFT JOIN sales s ON c.id = s.customer_id
        LEFT JOIN debts d ON c.id = d.debtor_id AND d.debtor_type = 'customer' AND d.status = 'outstanding'
        WHERE LOWER(c.name) LIKE ? OR c.phone LIKE ?
        GROUP BY c.id
        ORDER BY c.name
        """
        
        search_pattern = f"%{search_term}%"
        customers = self.db_manager.fetch_all(query, (search_pattern, search_pattern))
        
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer['id'],
                customer['name'],
                customer['phone'] or '',
                customer['email'] or '',
                customer['address'] or '',
                f"{customer['total_purchases']:,.0f}",
                f"{customer['total_debt']:,.0f}" if customer['total_debt'] > 0 else "0"
            ))
    
    def add_customer(self):
        """Add new customer"""
        self.show_customer_dialog()
    
    def edit_customer(self):
        """Edit selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_id = item['values'][0]
        self.show_customer_dialog(customer_id)
    
    def show_customer_dialog(self, customer_id=None):
        """Show add/edit customer dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thêm khách hàng" if customer_id is None else "Sửa thông tin khách hàng")
        dialog.geometry("500x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing customer data if editing
        customer_data = {}
        if customer_id:
            customer = self.db_manager.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
            if customer:
                customer_data = dict(customer)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Name
        ttk.Label(main_frame, text="Tên khách hàng *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=customer_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Phone
        ttk.Label(main_frame, text="Số điện thoại *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        phone_var = tk.StringVar(value=customer_data.get('phone', ''))
        phone_entry = ttk.Entry(main_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar(value=customer_data.get('email', ''))
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Address
        ttk.Label(main_frame, text="Địa chỉ:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        address_text = tk.Text(main_frame, width=40, height=3)
        address_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        if customer_data.get('address'):
            address_text.insert('1.0', customer_data['address'])
        row += 1
        
        # ID Number
        ttk.Label(main_frame, text="CMND/CCCD:").grid(row=row, column=0, sticky=tk.W, pady=5)
        id_number_var = tk.StringVar(value=customer_data.get('id_number', ''))
        id_number_entry = ttk.Entry(main_frame, textvariable=id_number_var, width=40)
        id_number_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Birth date
        ttk.Label(main_frame, text="Ngày sinh:").grid(row=row, column=0, sticky=tk.W, pady=5)
        birth_date_var = tk.StringVar(value=customer_data.get('birth_date', ''))
        birth_date_entry = ttk.Entry(main_frame, textvariable=birth_date_var, width=40)
        birth_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Debt limit
        ttk.Label(main_frame, text="Hạn mức nợ:").grid(row=row, column=0, sticky=tk.W, pady=5)
        debt_limit_var = tk.StringVar(value=str(customer_data.get('debt_limit', 0)))
        debt_limit_entry = ttk.Entry(main_frame, textvariable=debt_limit_var, width=40)
        debt_limit_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(main_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(main_frame, width=40, height=4)
        notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        if customer_data.get('notes'):
            notes_text.insert('1.0', customer_data['notes'])
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_customer():
            if not name_var.get().strip() or not phone_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tên và số điện thoại!")
                return
            
            try:
                debt_limit = float(debt_limit_var.get() or 0)
            except ValueError:
                messagebox.showerror("Lỗi", "Hạn mức nợ không hợp lệ!")
                return
            
            data = {
                'name': name_var.get().strip(),
                'phone': phone_var.get().strip(),
                'email': email_var.get().strip(),
                'address': address_text.get('1.0', tk.END).strip(),
                'id_number': id_number_var.get().strip(),
                'birth_date': birth_date_var.get() if birth_date_var.get() else None,
                'debt_limit': debt_limit,
                'notes': notes_text.get('1.0', tk.END).strip(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if customer_id:
                    # Update existing customer
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                    query = f"UPDATE customers SET {set_clause} WHERE id = ?"
                    params = list(data.values()) + [customer_id]
                else:
                    # Insert new customer
                    data['created_at'] = datetime.now().isoformat()
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    query = f"INSERT INTO customers ({columns}) VALUES ({placeholders})"
                    params = list(data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật khách hàng!" if customer_id else "Đã thêm khách hàng!")
                dialog.destroy()
                self.refresh_customers()
                
                # Reload customer combo in quick sale tab
                try:
                    customer_combo = None
                    for widget in self.frame.winfo_children():
                        if isinstance(widget, ttk.Frame):
                            for subwidget in widget.winfo_children():
                                if isinstance(subwidget, ttk.Notebook):
                                    # Find the customer combobox and reload it
                                    pass
                except:
                    pass
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu khách hàng: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
    
    def view_customer_history(self):
        """View customer purchase history"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng xem lịch sử mua hàng sẽ được phát triển!")
    
    def view_customer_debt(self):
        """View customer debt details"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng quản lý công nợ sẽ được phát triển!")
    
    def create_installment_contract(self):
        """Create new installment contract"""
        messagebox.showinfo("Thông báo", "Chức năng tạo hợp đồng trả góp sẽ được phát triển!")
    
    def collect_installment(self):
        """Collect installment payment"""
        messagebox.showinfo("Thông báo", "Chức năng thu góp sẽ được phát triển!")
    
    def view_installment_details(self):
        """View installment contract details"""
        messagebox.showinfo("Thông báo", "Chức năng xem chi tiết trả góp sẽ được phát triển!")
