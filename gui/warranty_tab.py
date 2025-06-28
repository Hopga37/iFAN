#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warranty management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import uuid

from models import Warranty, Customer
from utils.qr_utils import generate_qr_code
from config import BUSINESS_RULES

class WarrantyTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup warranty tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Warranty List tab
        self.setup_warranty_list_tab()
        
        # Warranty Lookup tab
        self.setup_warranty_lookup_tab()
        
        # Warranty Claims tab
        self.setup_warranty_claims_tab()
        
        # Expired Warranties tab
        self.setup_expired_warranties_tab()
    
    def setup_warranty_list_tab(self):
        """Setup warranty list tab"""
        warranty_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(warranty_list_frame, text="Danh Sách Bảo Hành")
        
        # Top controls
        top_frame = ttk.Frame(warranty_list_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm bảo hành", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="IMEI / Số bảo hành / Khách hàng:").pack(anchor=tk.W)
        self.warranty_search_var = tk.StringVar()
        self.warranty_search_var.trace('w', self.on_warranty_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.warranty_search_var, width=40)
        search_entry.pack(pady=5, fill=tk.X)
        
        # Status filter
        status_frame = ttk.LabelFrame(top_frame, text="Lọc trạng thái", padding=10)
        status_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_filter_var = tk.StringVar(value="all")
        status_values = [
            ("all", "Tất cả"),
            ("active", "Đang bảo hành"),
            ("expired", "Hết hạn"),
            ("claimed", "Đã bảo hành"),
            ("voided", "Hủy bỏ")
        ]
        
        for value, text in status_values:
            ttk.Radiobutton(status_frame, text=text, variable=self.status_filter_var,
                           value=value, command=self.filter_warranties).pack(anchor=tk.W)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="➕ Tạo bảo hành", 
                  command=self.create_warranty).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="👁️ Xem chi tiết", 
                  command=self.view_warranty_details).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🖨️ In phiếu BH", 
                  command=self.print_warranty_card).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="📋 Cập nhật trạng thái", 
                  command=self.update_warranty_status).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_warranties).pack(pady=2, fill=tk.X)
        
        # Warranties treeview
        tree_frame = ttk.Frame(warranty_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.warranties_tree = ttk.Treeview(tree_frame,
                                           columns=('id', 'warranty_number', 'imei', 'customer', 'product',
                                                  'start_date', 'end_date', 'status', 'type', 'remaining_days'),
                                           show='headings',
                                           yscrollcommand=v_scrollbar.set,
                                           xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.warranties_tree.yview)
        h_scrollbar.config(command=self.warranties_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'warranty_number': ('Số bảo hành', 120),
            'imei': ('IMEI', 150),
            'customer': ('Khách hàng', 150),
            'product': ('Sản phẩm', 200),
            'start_date': ('Ngày bắt đầu', 100),
            'end_date': ('Ngày hết hạn', 100),
            'status': ('Trạng thái', 100),
            'type': ('Loại BH', 100),
            'remaining_days': ('Còn lại (ngày)', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.warranties_tree.heading(col, text=heading)
            self.warranties_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.warranties_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.warranties_tree.bind('<Double-1>', lambda e: self.view_warranty_details())
    
    def setup_warranty_lookup_tab(self):
        """Setup warranty lookup tab"""
        lookup_frame = ttk.Frame(self.notebook)
        self.notebook.add(lookup_frame, text="Tra Cứu Bảo Hành")
        
        # Search section
        search_section = ttk.LabelFrame(lookup_frame, text="Tra cứu bảo hành", padding=20)
        search_section.pack(fill=tk.X, padx=20, pady=20)
        
        # IMEI/QR Code lookup
        ttk.Label(search_section, text="Quét QR Code hoặc nhập IMEI / Số bảo hành:", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        lookup_frame_inner = ttk.Frame(search_section)
        lookup_frame_inner.pack(fill=tk.X)
        
        self.lookup_var = tk.StringVar()
        lookup_entry = ttk.Entry(lookup_frame_inner, textvariable=self.lookup_var, width=30, font=('Arial', 14))
        lookup_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(lookup_frame_inner, text="🔍 Tra cứu", 
                  command=self.lookup_warranty).pack(side=tk.LEFT, padx=5)
        ttk.Button(lookup_frame_inner, text="📷 Quét QR", 
                  command=self.scan_warranty_qr).pack(side=tk.LEFT, padx=5)
        
        # Results section
        self.warranty_results_frame = ttk.LabelFrame(lookup_frame, text="Kết quả tra cứu", padding=20)
        self.warranty_results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Initially hide results
        self.warranty_results_frame.pack_forget()
        
        # Focus on lookup entry
        lookup_entry.focus_set()
    
    def setup_warranty_claims_tab(self):
        """Setup warranty claims tab"""
        claims_frame = ttk.Frame(self.notebook)
        self.notebook.add(claims_frame, text="Yêu Cầu Bảo Hành")
        
        # Top controls
        top_frame = ttk.Frame(claims_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        ttk.Button(top_frame, text="➕ Tạo yêu cầu BH", 
                  command=self.create_warranty_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="✏️ Xử lý yêu cầu", 
                  command=self.process_warranty_claim).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="👁️ Xem chi tiết", 
                  command=self.view_claim_details).pack(side=tk.LEFT, padx=5)
        
        # Claims treeview
        tree_frame = ttk.Frame(claims_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.claims_tree = ttk.Treeview(tree_frame,
                                       columns=('id', 'claim_date', 'warranty_number', 'imei', 
                                              'customer', 'issue', 'status', 'resolution'),
                                       show='headings')
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'claim_date': ('Ngày yêu cầu', 120),
            'warranty_number': ('Số bảo hành', 120),
            'imei': ('IMEI', 150),
            'customer': ('Khách hàng', 150),
            'issue': ('Vấn đề', 200),
            'status': ('Trạng thái', 100),
            'resolution': ('Giải quyết', 150)
        }
        
        for col, (heading, width) in columns.items():
            self.claims_tree.heading(col, text=heading)
            self.claims_tree.column(col, width=width, minwidth=50)
        
        self.claims_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_expired_warranties_tab(self):
        """Setup expired warranties tab"""
        expired_frame = ttk.Frame(self.notebook)
        self.notebook.add(expired_frame, text="BH Hết Hạn")
        
        # Info frame
        info_frame = ttk.LabelFrame(expired_frame, text="Bảo hành sắp hết hạn / đã hết hạn", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text="Danh sách các sản phẩm bảo hành sắp hết hạn trong 30 ngày tới hoặc đã hết hạn.", 
                 font=('Arial', 10)).pack(anchor=tk.W)
        
        # Filter frame
        filter_frame = ttk.Frame(info_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        self.expiry_filter_var = tk.StringVar(value="expiring")
        ttk.Radiobutton(filter_frame, text="Sắp hết hạn (30 ngày)", 
                       variable=self.expiry_filter_var, value="expiring",
                       command=self.filter_expired_warranties).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(filter_frame, text="Đã hết hạn", 
                       variable=self.expiry_filter_var, value="expired",
                       command=self.filter_expired_warranties).pack(side=tk.LEFT, padx=10)
        
        # Expired warranties treeview
        tree_frame = ttk.Frame(expired_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.expired_tree = ttk.Treeview(tree_frame,
                                        columns=('warranty_number', 'imei', 'customer', 'product',
                                               'end_date', 'days_remaining', 'contact'),
                                        show='headings')
        
        # Column headings
        columns = {
            'warranty_number': ('Số bảo hành', 120),
            'imei': ('IMEI', 150),
            'customer': ('Khách hàng', 150),
            'product': ('Sản phẩm', 200),
            'end_date': ('Hết hạn', 100),
            'days_remaining': ('Còn lại', 80),
            'contact': ('Liên hệ', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.expired_tree.heading(col, text=heading)
            self.expired_tree.column(col, width=width, minwidth=50)
        
        self.expired_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load expired warranties
        self.filter_expired_warranties()
    
    def load_data(self):
        """Load all data"""
        self.refresh_warranties()
        self.load_warranty_claims()
    
    def refresh_warranties(self):
        """Refresh warranties list"""
        # Clear existing items
        for item in self.warranties_tree.get_children():
            self.warranties_tree.delete(item)
        
        # Load warranties
        query = """
        SELECT w.*, c.name as customer_name, p.name as product_name
        FROM warranties w
        LEFT JOIN customers c ON w.customer_id = c.id
        LEFT JOIN products p ON w.product_id = p.id
        ORDER BY w.created_at DESC
        """
        
        warranties = self.db_manager.fetch_all(query)
        
        for warranty in warranties:
            # Calculate remaining days
            try:
                end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
                remaining_days = (end_date - date.today()).days
                remaining_text = f"{remaining_days} ngày" if remaining_days > 0 else "Hết hạn"
            except:
                remaining_text = "N/A"
            
            # Status translation
            status_map = {
                'active': 'Đang bảo hành',
                'expired': 'Hết hạn',
                'claimed': 'Đã bảo hành',
                'voided': 'Hủy bỏ'
            }
            
            status_text = status_map.get(warranty['status'], warranty['status'])
            
            # Type translation
            type_map = {
                'product': 'Sản phẩm',
                'repair': 'Sau sửa chữa'
            }
            
            type_text = type_map.get(warranty['warranty_type'], warranty['warranty_type'])
            
            self.warranties_tree.insert('', 'end', values=(
                warranty['id'],
                warranty['warranty_number'],
                warranty['imei'] or '',
                warranty['customer_name'] or '',
                warranty['product_name'] or '',
                warranty['start_date'],
                warranty['end_date'],
                status_text,
                type_text,
                remaining_text
            ))
    
    def on_warranty_search(self, *args):
        """Handle warranty search"""
        search_term = self.warranty_search_var.get().lower()
        
        if not search_term:
            self.refresh_warranties()
            return
        
        # Clear existing items
        for item in self.warranties_tree.get_children():
            self.warranties_tree.delete(item)
        
        # Search warranties
        query = """
        SELECT w.*, c.name as customer_name, p.name as product_name
        FROM warranties w
        LEFT JOIN customers c ON w.customer_id = c.id
        LEFT JOIN products p ON w.product_id = p.id
        WHERE LOWER(w.warranty_number) LIKE ? OR
              LOWER(w.imei) LIKE ? OR
              LOWER(c.name) LIKE ?
        ORDER BY w.created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        warranties = self.db_manager.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        
        for warranty in warranties:
            # Calculate remaining days
            try:
                end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
                remaining_days = (end_date - date.today()).days
                remaining_text = f"{remaining_days} ngày" if remaining_days > 0 else "Hết hạn"
            except:
                remaining_text = "N/A"
            
            status_map = {
                'active': 'Đang bảo hành',
                'expired': 'Hết hạn',
                'claimed': 'Đã bảo hành',
                'voided': 'Hủy bỏ'
            }
            
            status_text = status_map.get(warranty['status'], warranty['status'])
            
            type_map = {
                'product': 'Sản phẩm',
                'repair': 'Sau sửa chữa'
            }
            
            type_text = type_map.get(warranty['warranty_type'], warranty['warranty_type'])
            
            self.warranties_tree.insert('', 'end', values=(
                warranty['id'],
                warranty['warranty_number'],
                warranty['imei'] or '',
                warranty['customer_name'] or '',
                warranty['product_name'] or '',
                warranty['start_date'],
                warranty['end_date'],
                status_text,
                type_text,
                remaining_text
            ))
    
    def filter_warranties(self):
        """Filter warranties by status"""
        status_filter = self.status_filter_var.get()
        
        # Clear existing items
        for item in self.warranties_tree.get_children():
            self.warranties_tree.delete(item)
        
        # Build query based on filter
        if status_filter == "all":
            query = """
            SELECT w.*, c.name as customer_name, p.name as product_name
            FROM warranties w
            LEFT JOIN customers c ON w.customer_id = c.id
            LEFT JOIN products p ON w.product_id = p.id
            ORDER BY w.created_at DESC
            """
            params = ()
        else:
            # Handle special cases
            if status_filter == "active":
                query = """
                SELECT w.*, c.name as customer_name, p.name as product_name
                FROM warranties w
                LEFT JOIN customers c ON w.customer_id = c.id
                LEFT JOIN products p ON w.product_id = p.id
                WHERE w.status = 'active' AND DATE(w.end_date) >= DATE('now')
                ORDER BY w.created_at DESC
                """
                params = ()
            elif status_filter == "expired":
                query = """
                SELECT w.*, c.name as customer_name, p.name as product_name
                FROM warranties w
                LEFT JOIN customers c ON w.customer_id = c.id
                LEFT JOIN products p ON w.product_id = p.id
                WHERE DATE(w.end_date) < DATE('now')
                ORDER BY w.created_at DESC
                """
                params = ()
            else:
                query = """
                SELECT w.*, c.name as customer_name, p.name as product_name
                FROM warranties w
                LEFT JOIN customers c ON w.customer_id = c.id
                LEFT JOIN products p ON w.product_id = p.id
                WHERE w.status = ?
                ORDER BY w.created_at DESC
                """
                params = (status_filter,)
        
        warranties = self.db_manager.fetch_all(query, params)
        
        for warranty in warranties:
            # Calculate remaining days
            try:
                end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
                remaining_days = (end_date - date.today()).days
                remaining_text = f"{remaining_days} ngày" if remaining_days > 0 else "Hết hạn"
            except:
                remaining_text = "N/A"
            
            status_map = {
                'active': 'Đang bảo hành',
                'expired': 'Hết hạn',
                'claimed': 'Đã bảo hành',
                'voided': 'Hủy bỏ'
            }
            
            status_text = status_map.get(warranty['status'], warranty['status'])
            
            type_map = {
                'product': 'Sản phẩm',
                'repair': 'Sau sửa chữa'
            }
            
            type_text = type_map.get(warranty['warranty_type'], warranty['warranty_type'])
            
            self.warranties_tree.insert('', 'end', values=(
                warranty['id'],
                warranty['warranty_number'],
                warranty['imei'] or '',
                warranty['customer_name'] or '',
                warranty['product_name'] or '',
                warranty['start_date'],
                warranty['end_date'],
                status_text,
                type_text,
                remaining_text
            ))
    
    def create_warranty(self):
        """Create new warranty"""
        self.show_warranty_dialog()
    
    def show_warranty_dialog(self, warranty_id=None):
        """Show add/edit warranty dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Tạo bảo hành" if warranty_id is None else "Sửa bảo hành")
        dialog.geometry("600x500")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing warranty data if editing
        warranty_data = {}
        if warranty_id:
            warranty = self.db_manager.fetch_one("SELECT * FROM warranties WHERE id = ?", (warranty_id,))
            if warranty:
                warranty_data = dict(warranty)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Warranty number
        ttk.Label(main_frame, text="Số bảo hành:").grid(row=row, column=0, sticky=tk.W, pady=5)
        warranty_number_var = tk.StringVar(value=warranty_data.get('warranty_number', ''))
        warranty_number_entry = ttk.Entry(main_frame, textvariable=warranty_number_var, width=30, state="readonly")
        warranty_number_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(main_frame, text="Tạo mã", 
                  command=lambda: warranty_number_var.set(f"BH{datetime.now().strftime('%Y%m%d%H%M%S')}")
                  ).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Customer
        ttk.Label(main_frame, text="Khách hàng *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(main_frame, textvariable=customer_var, width=40)
        
        # Load customers
        customers = self.db_manager.fetch_all("SELECT id, name, phone FROM customers ORDER BY name")
        customer_combo['values'] = [f"{c['id']} - {c['name']} ({c['phone']})" for c in customers if c['phone']]
        
        if warranty_data.get('customer_id'):
            for i, customer in enumerate(customers):
                if customer['id'] == warranty_data['customer_id']:
                    customer_combo.current(i)
                    break
        
        customer_combo.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Product
        ttk.Label(main_frame, text="Sản phẩm:").grid(row=row, column=0, sticky=tk.W, pady=5)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(main_frame, textvariable=product_var, width=40)
        
        # Load products
        products = self.db_manager.fetch_all("SELECT id, name, brand FROM products WHERE is_active = 1 ORDER BY name")
        product_combo['values'] = [f"{p['id']} - {p['name']} ({p['brand']})" for p in products]
        
        if warranty_data.get('product_id'):
            for i, product in enumerate(products):
                if product['id'] == warranty_data['product_id']:
                    product_combo.current(i)
                    break
        
        product_combo.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # IMEI
        ttk.Label(main_frame, text="IMEI *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        imei_var = tk.StringVar(value=warranty_data.get('imei', ''))
        imei_entry = ttk.Entry(main_frame, textvariable=imei_var, width=40)
        imei_entry.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Warranty type
        ttk.Label(main_frame, text="Loại bảo hành:").grid(row=row, column=0, sticky=tk.W, pady=5)
        warranty_type_var = tk.StringVar(value=warranty_data.get('warranty_type', 'product'))
        warranty_type_combo = ttk.Combobox(main_frame, textvariable=warranty_type_var, width=37,
                                          values=['product', 'repair'], state="readonly")
        warranty_type_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Start date
        ttk.Label(main_frame, text="Ngày bắt đầu *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        start_date_var = tk.StringVar(value=warranty_data.get('start_date', date.today().strftime('%Y-%m-%d')))
        start_date_entry = ttk.Entry(main_frame, textvariable=start_date_var, width=20)
        start_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(main_frame, text="Hôm nay", 
                  command=lambda: start_date_var.set(date.today().strftime('%Y-%m-%d'))
                  ).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # End date
        ttk.Label(main_frame, text="Ngày hết hạn *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        end_date_var = tk.StringVar(value=warranty_data.get('end_date', ''))
        end_date_entry = ttk.Entry(main_frame, textvariable=end_date_var, width=20)
        end_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        def calculate_end_date():
            try:
                start = datetime.strptime(start_date_var.get(), '%Y-%m-%d').date()
                end = start + timedelta(days=365)  # 1 year default
                end_date_var.set(end.strftime('%Y-%m-%d'))
            except:
                pass
        
        ttk.Button(main_frame, text="Tính tự động", 
                  command=calculate_end_date).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Status
        ttk.Label(main_frame, text="Trạng thái:").grid(row=row, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value=warranty_data.get('status', 'active'))
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, width=37,
                                   values=['active', 'expired', 'claimed', 'voided'], state="readonly")
        status_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(main_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(main_frame, width=40, height=4)
        notes_text.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        if warranty_data.get('notes'):
            notes_text.insert('1.0', warranty_data['notes'])
        row += 1
        
        # Generate initial warranty number if creating new
        if not warranty_id and not warranty_number_var.get():
            warranty_number_var.set(f"BH{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        def save_warranty():
            if not warranty_number_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng tạo số bảo hành!")
                return
            
            if not customer_var.get():
                messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng!")
                return
            
            if not imei_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập IMEI!")
                return
            
            if not start_date_var.get() or not end_date_var.get():
                messagebox.showerror("Lỗi", "Vui lòng nhập ngày bảo hành!")
                return
            
            try:
                # Get customer ID
                customer_id = int(customer_var.get().split(' - ')[0])
                
                # Get product ID
                product_id = None
                if product_var.get():
                    product_id = int(product_var.get().split(' - ')[0])
                
                # Generate QR code
                qr_code = generate_qr_code(f"WARRANTY:{warranty_number_var.get()}")
                
                # Prepare warranty data
                data = {
                    'warranty_number': warranty_number_var.get().strip(),
                    'imei': imei_var.get().strip(),
                    'product_id': product_id,
                    'customer_id': customer_id,
                    'warranty_type': warranty_type_var.get(),
                    'start_date': start_date_var.get(),
                    'end_date': end_date_var.get(),
                    'status': status_var.get(),
                    'qr_code': qr_code,
                    'notes': notes_text.get('1.0', tk.END).strip(),
                    'updated_at': datetime.now().isoformat()
                }
                
                if warranty_id:
                    # Update existing warranty
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                    query = f"UPDATE warranties SET {set_clause} WHERE id = ?"
                    params = list(data.values()) + [warranty_id]
                else:
                    # Insert new warranty
                    data['created_at'] = datetime.now().isoformat()
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    query = f"INSERT INTO warranties ({columns}) VALUES ({placeholders})"
                    params = list(data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật bảo hành!" if warranty_id else "Đã tạo bảo hành!")
                dialog.destroy()
                self.refresh_warranties()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu bảo hành: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_warranty).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def view_warranty_details(self):
        """View warranty details"""
        selection = self.warranties_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bảo hành!")
            return
        
        item = self.warranties_tree.item(selection[0])
        warranty_id = item['values'][0]
        self.show_warranty_details_dialog(warranty_id)
    
    def show_warranty_details_dialog(self, warranty_id):
        """Show warranty details dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Chi tiết bảo hành")
        dialog.geometry("700x600")
        dialog.transient(self.frame)
        
        # Load warranty data
        warranty = self.db_manager.fetch_one(
            """SELECT w.*, c.name as customer_name, c.phone as customer_phone,
                      c.address as customer_address, p.name as product_name, p.brand
               FROM warranties w
               LEFT JOIN customers c ON w.customer_id = c.id
               LEFT JOIN products p ON w.product_id = p.id
               WHERE w.id = ?""",
            (warranty_id,)
        )
        
        if not warranty:
            messagebox.showerror("Lỗi", "Không tìm thấy bảo hành!")
            dialog.destroy()
            return
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Warranty information
        info_frame = ttk.LabelFrame(main_frame, text="Thông tin bảo hành", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Calculate warranty status
        try:
            end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
            remaining_days = (end_date - date.today()).days
            if remaining_days > 0:
                warranty_status = f"Còn {remaining_days} ngày"
                status_color = "green" if remaining_days > 30 else "orange"
            else:
                warranty_status = "Đã hết hạn"
                status_color = "red"
        except:
            warranty_status = "N/A"
            status_color = "black"
        
        info_data = [
            ("Số bảo hành:", warranty['warranty_number']),
            ("IMEI:", warranty['imei'] or ''),
            ("Sản phẩm:", f"{warranty['product_name']} ({warranty['brand']})" if warranty['product_name'] else ''),
            ("Loại bảo hành:", "Sản phẩm" if warranty['warranty_type'] == 'product' else "Sau sửa chữa"),
            ("Ngày bắt đầu:", warranty['start_date']),
            ("Ngày hết hạn:", warranty['end_date']),
            ("Tình trạng:", warranty_status),
            ("Trạng thái:", warranty['status'])
        ]
        
        for i, (label, value) in enumerate(info_data):
            row, col = divmod(i, 2)
            ttk.Label(info_frame, text=label).grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            label_widget = ttk.Label(info_frame, text=str(value), font=('Arial', 10, 'bold'))
            if label == "Tình trạng:":
                label_widget.config(foreground=status_color)
            label_widget.grid(row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Customer information
        customer_info_frame = ttk.LabelFrame(main_frame, text="Thông tin khách hàng", padding=10)
        customer_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        customer_data = [
            ("Tên khách hàng:", warranty['customer_name'] or ''),
            ("Số điện thoại:", warranty['customer_phone'] or ''),
            ("Địa chỉ:", warranty['customer_address'] or '')
        ]
        
        for i, (label, value) in enumerate(customer_data):
            ttk.Label(customer_info_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(customer_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # QR Code section
        if warranty['qr_code']:
            qr_frame = ttk.LabelFrame(main_frame, text="QR Code tra cứu", padding=10)
            qr_frame.pack(fill=tk.X, pady=(0, 10))
            
            ttk.Label(qr_frame, text=f"Mã QR tra cứu: {warranty['warranty_number']}", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Notes
        if warranty['notes']:
            notes_frame = ttk.LabelFrame(main_frame, text="Ghi chú", padding=10)
            notes_frame.pack(fill=tk.X, pady=(0, 10))
            
            notes_text = tk.Text(notes_frame, width=60, height=4, wrap=tk.WORD, state=tk.DISABLED)
            notes_text.insert('1.0', warranty['notes'])
            notes_text.pack(fill=tk.X)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ In phiếu BH", 
                  command=lambda: self.print_warranty_card_by_id(warranty_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=lambda: [dialog.destroy(), self.show_warranty_dialog(warranty_id)]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Đóng", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def print_warranty_card(self):
        """Print warranty card for selected warranty"""
        selection = self.warranties_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bảo hành!")
            return
        
        item = self.warranties_tree.item(selection[0])
        warranty_id = item['values'][0]
        self.print_warranty_card_by_id(warranty_id)
    
    def print_warranty_card_by_id(self, warranty_id):
        """Print warranty card by ID"""
        try:
            from utils.print_utils import print_warranty_card
            print_warranty_card(self.db_manager, warranty_id)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in phiếu bảo hành: {e}")
    
    def update_warranty_status(self):
        """Update warranty status"""
        selection = self.warranties_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn bảo hành!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng cập nhật trạng thái bảo hành sẽ được phát triển!")
    
    def lookup_warranty(self):
        """Lookup warranty by IMEI/QR code"""
        lookup_value = self.lookup_var.get().strip()
        if not lookup_value:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập IMEI hoặc số bảo hành!")
            return
        
        # Extract warranty number from QR code if necessary
        warranty_identifier = lookup_value
        if lookup_value.startswith("WARRANTY:"):
            warranty_identifier = lookup_value.replace("WARRANTY:", "")
        
        # Find warranty
        warranty = self.db_manager.fetch_one(
            """SELECT w.*, c.name as customer_name, c.phone as customer_phone,
                      p.name as product_name, p.brand
               FROM warranties w
               LEFT JOIN customers c ON w.customer_id = c.id
               LEFT JOIN products p ON w.product_id = p.id
               WHERE w.warranty_number = ? OR w.imei = ?""",
            (warranty_identifier, warranty_identifier)
        )
        
        if not warranty:
            # Hide results frame
            self.warranty_results_frame.pack_forget()
            messagebox.showwarning("Không tìm thấy", f"Không tìm thấy bảo hành với mã: {warranty_identifier}")
            return
        
        # Show results
        self.show_warranty_lookup_results(warranty)
    
    def show_warranty_lookup_results(self, warranty):
        """Show warranty lookup results"""
        # Clear existing results
        for widget in self.warranty_results_frame.winfo_children():
            widget.destroy()
        
        # Show results frame
        self.warranty_results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Title
        ttk.Label(self.warranty_results_frame, text=f"Thông tin bảo hành - {warranty['warranty_number']}", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        # Calculate warranty status
        try:
            end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
            remaining_days = (end_date - date.today()).days
            if remaining_days > 0:
                warranty_status = f"Còn hiệu lực ({remaining_days} ngày)"
                status_color = "green" if remaining_days > 30 else "orange"
                status_icon = "✅"
            else:
                warranty_status = "Đã hết hạn"
                status_color = "red"
                status_icon = "❌"
        except:
            warranty_status = "Không xác định"
            status_color = "black"
            status_icon = "❓"
        
        # Status display
        status_frame = ttk.Frame(self.warranty_results_frame)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(status_frame, text="Tình trạng bảo hành:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        status_label = ttk.Label(status_frame, text=f"{status_icon} {warranty_status}", 
                                font=('Arial', 14, 'bold'))
        status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Product information
        info_frame = ttk.Frame(self.warranty_results_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_data = [
            ("Sản phẩm:", f"{warranty['product_name']} ({warranty['brand']})" if warranty['product_name'] else "N/A"),
            ("IMEI:", warranty['imei'] or 'N/A'),
            ("Khách hàng:", warranty['customer_name'] or 'N/A'),
            ("SĐT liên hệ:", warranty['customer_phone'] or 'N/A'),
            ("Ngày bắt đầu BH:", warranty['start_date']),
            ("Ngày hết hạn BH:", warranty['end_date']),
            ("Loại bảo hành:", "Sản phẩm" if warranty['warranty_type'] == 'product' else "Sau sửa chữa")
        ]
        
        for label, value in info_data:
            row_frame = ttk.Frame(info_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Instructions
        instructions_frame = ttk.Frame(self.warranty_results_frame)
        instructions_frame.pack(fill=tk.X, pady=(15, 0))
        
        if remaining_days > 0:
            ttk.Label(instructions_frame, text="📋 Hướng dẫn bảo hành:", 
                     font=('Arial', 11, 'bold')).pack(anchor=tk.W)
            instructions = [
                "• Mang sản phẩm và phiếu bảo hành đến cửa hàng",
                "• Bảo hành không áp dụng cho hư hỏng do người dùng",
                "• Thời gian bảo hành: 7-15 ngày làm việc",
                "• Liên hệ cửa hàng để biết thêm chi tiết"
            ]
            
            for instruction in instructions:
                ttk.Label(instructions_frame, text=instruction, font=('Arial', 10)).pack(anchor=tk.W, pady=1)
        else:
            ttk.Label(instructions_frame, text="❌ Sản phẩm đã hết thời gian bảo hành.", 
                     font=('Arial', 11, 'bold'), foreground='red').pack(anchor=tk.W)
    
    def scan_warranty_qr(self):
        """Scan warranty QR code"""
        messagebox.showinfo("Thông báo", "Chức năng quét QR code bảo hành sẽ được phát triển!")
    
    def load_warranty_claims(self):
        """Load warranty claims"""
        # This would load warranty claim requests
        # For now, we'll show a placeholder
        pass
    
    def create_warranty_claim(self):
        """Create warranty claim"""
        messagebox.showinfo("Thông báo", "Chức năng tạo yêu cầu bảo hành sẽ được phát triển!")
    
    def process_warranty_claim(self):
        """Process warranty claim"""
        messagebox.showinfo("Thông báo", "Chức năng xử lý yêu cầu bảo hành sẽ được phát triển!")
    
    def view_claim_details(self):
        """View warranty claim details"""
        messagebox.showinfo("Thông báo", "Chức năng xem chi tiết yêu cầu bảo hành sẽ được phát triển!")
    
    def filter_expired_warranties(self):
        """Filter expired/expiring warranties"""
        filter_type = self.expiry_filter_var.get()
        
        # Clear existing items
        for item in self.expired_tree.get_children():
            self.expired_tree.delete(item)
        
        if filter_type == "expiring":
            # Warranties expiring in 30 days
            query = """
            SELECT w.*, c.name as customer_name, c.phone as customer_phone,
                   p.name as product_name, p.brand
            FROM warranties w
            LEFT JOIN customers c ON w.customer_id = c.id
            LEFT JOIN products p ON w.product_id = p.id
            WHERE w.status = 'active' AND 
                  DATE(w.end_date) BETWEEN DATE('now') AND DATE('now', '+30 days')
            ORDER BY w.end_date ASC
            """
        else:
            # Expired warranties
            query = """
            SELECT w.*, c.name as customer_name, c.phone as customer_phone,
                   p.name as product_name, p.brand
            FROM warranties w
            LEFT JOIN customers c ON w.customer_id = c.id
            LEFT JOIN products p ON w.product_id = p.id
            WHERE DATE(w.end_date) < DATE('now')
            ORDER BY w.end_date DESC
            """
        
        warranties = self.db_manager.fetch_all(query)
        
        for warranty in warranties:
            # Calculate remaining days
            try:
                end_date = datetime.strptime(warranty['end_date'], '%Y-%m-%d').date()
                remaining_days = (end_date - date.today()).days
                if remaining_days >= 0:
                    remaining_text = f"{remaining_days} ngày"
                else:
                    remaining_text = f"Hết hạn {abs(remaining_days)} ngày"
            except:
                remaining_text = "N/A"
            
            product_name = ""
            if warranty['product_name']:
                product_name = f"{warranty['product_name']}"
                if warranty['brand']:
                    product_name += f" ({warranty['brand']})"
            
            self.expired_tree.insert('', 'end', values=(
                warranty['warranty_number'],
                warranty['imei'] or '',
                warranty['customer_name'] or '',
                product_name,
                warranty['end_date'],
                remaining_text,
                warranty['customer_phone'] or ''
            ))
