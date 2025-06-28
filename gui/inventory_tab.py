#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inventory management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import uuid

from models import Product, InventoryItem
from utils.barcode_utils import generate_barcode
from config import BUSINESS_RULES

class InventoryTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup inventory tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Products tab
        self.setup_products_tab()
        
        # Inventory tab
        self.setup_inventory_tab()
        
        # Categories tab
        self.setup_categories_tab()
    
    def setup_products_tab(self):
        """Setup products management tab"""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text="Sản Phẩm")
        
        # Top frame for controls
        top_frame = ttk.Frame(products_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Tìm kiếm:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace('w', self.on_product_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.product_search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="➕ Thêm Sản Phẩm", 
                  command=self.add_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Xóa", 
                  command=self.delete_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_products).pack(side=tk.LEFT, padx=(0, 5))
        
        # Products treeview
        tree_frame = ttk.Frame(products_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.products_tree = ttk.Treeview(tree_frame, 
                                         columns=('id', 'name', 'brand', 'model', 'category', 
                                                'cost_price', 'selling_price', 'stock', 'status'),
                                         show='headings',
                                         yscrollcommand=v_scrollbar.set,
                                         xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.products_tree.yview)
        h_scrollbar.config(command=self.products_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'name': ('Tên sản phẩm', 200),
            'brand': ('Thương hiệu', 100),
            'model': ('Mẫu mã', 100),
            'category': ('Danh mục', 120),
            'cost_price': ('Giá nhập', 100),
            'selling_price': ('Giá bán', 100),
            'stock': ('Tồn kho', 80),
            'status': ('Trạng thái', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.products_tree.heading(col, text=heading)
            self.products_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.products_tree.bind('<Double-1>', lambda e: self.edit_product())
    
    def setup_inventory_tab(self):
        """Setup inventory tracking tab"""
        inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_frame, text="Tồn Kho")
        
        # Top controls
        top_frame = ttk.Frame(inventory_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm theo IMEI/Serial", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="IMEI/Serial:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.inventory_search_var = tk.StringVar()
        self.inventory_search_var.trace('w', self.on_inventory_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.inventory_search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="➕ Nhập Kho", 
                  command=self.add_inventory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_inventory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🏷️ In Mã Vạch", 
                  command=self.print_barcode).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="⚠️ Cảnh Báo Hết Hàng", 
                  command=self.show_low_stock).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_inventory).pack(side=tk.LEFT, padx=(0, 5))
        
        # Inventory treeview
        tree_frame = ttk.Frame(inventory_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.inventory_tree = ttk.Treeview(tree_frame,
                                          columns=('id', 'product', 'imei', 'serial', 'condition',
                                                 'status', 'cost_price', 'selling_price', 'location'),
                                          show='headings',
                                          yscrollcommand=v_scrollbar.set,
                                          xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.inventory_tree.yview)
        h_scrollbar.config(command=self.inventory_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'product': ('Sản phẩm', 200),
            'imei': ('IMEI', 150),
            'serial': ('Serial', 120),
            'condition': ('Tình trạng', 100),
            'status': ('Trạng thái', 100),
            'cost_price': ('Giá nhập', 100),
            'selling_price': ('Giá bán', 100),
            'location': ('Vị trí', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.inventory_tree.heading(col, text=heading)
            self.inventory_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.inventory_tree.bind('<Double-1>', lambda e: self.edit_inventory())
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(categories_frame, text="Danh Mục")
        
        # Top controls
        top_frame = ttk.Frame(categories_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(top_frame, text="➕ Thêm Danh Mục", 
                  command=self.add_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="✏️ Sửa", 
                  command=self.edit_category).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(top_frame, text="🗑️ Xóa", 
                  command=self.delete_category).pack(side=tk.LEFT, padx=(0, 5))
        
        # Categories treeview
        self.categories_tree = ttk.Treeview(categories_frame,
                                           columns=('id', 'name', 'description', 'product_count'),
                                           show='headings')
        
        # Column headings
        self.categories_tree.heading('id', text='ID')
        self.categories_tree.heading('name', text='Tên danh mục')
        self.categories_tree.heading('description', text='Mô tả')
        self.categories_tree.heading('product_count', text='Số sản phẩm')
        
        # Column widths
        self.categories_tree.column('id', width=50)
        self.categories_tree.column('name', width=200)
        self.categories_tree.column('description', width=300)
        self.categories_tree.column('product_count', width=100)
        
        self.categories_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click
        self.categories_tree.bind('<Double-1>', lambda e: self.edit_category())
    
    def load_data(self):
        """Load all data"""
        self.refresh_products()
        self.refresh_inventory()
        self.refresh_categories()
    
    def refresh_products(self):
        """Refresh products list"""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Load products with stock information
        query = """
        SELECT p.*, c.name as category_name,
               COUNT(i.id) as stock_count,
               COUNT(CASE WHEN i.status = 'available' THEN 1 END) as available_count
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.is_active = 1
        GROUP BY p.id
        ORDER BY p.name
        """
        
        products = self.db_manager.fetch_all(query)
        
        for product in products:
            stock_text = f"{product['available_count']}/{product['stock_count']}"
            status = "Hoạt động" if product['is_active'] else "Tạm dừng"
            
            # Check low stock
            if product['available_count'] <= BUSINESS_RULES['LOW_STOCK_THRESHOLD']:
                status = "⚠️ Sắp hết hàng"
            
            self.products_tree.insert('', 'end', values=(
                product['id'],
                product['name'],
                product['brand'] or '',
                product['model'] or '',
                product['category_name'] or '',
                f"{product['cost_price']:,.0f}",
                f"{product['selling_price']:,.0f}",
                stock_text,
                status
            ))
    
    def refresh_inventory(self):
        """Refresh inventory list"""
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Load inventory with product information
        query = """
        SELECT i.*, p.name as product_name, p.brand, p.model
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        ORDER BY i.created_at DESC
        """
        
        inventory_items = self.db_manager.fetch_all(query)
        
        for item in inventory_items:
            product_display = f"{item['product_name']}"
            if item['brand']:
                product_display += f" ({item['brand']})"
            
            self.inventory_tree.insert('', 'end', values=(
                item['id'],
                product_display,
                item['imei'] or '',
                item['serial_number'] or '',
                item['condition'] or 'new',
                item['status'] or 'available',
                f"{(item['cost_price'] or 0):,.0f}",
                f"{(item['selling_price'] or 0):,.0f}",
                item['location'] or ''
            ))
    
    def refresh_categories(self):
        """Refresh categories list"""
        # Clear existing items
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Load categories with product count
        query = """
        SELECT c.*, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id AND p.is_active = 1
        GROUP BY c.id
        ORDER BY c.name
        """
        
        categories = self.db_manager.fetch_all(query)
        
        for category in categories:
            self.categories_tree.insert('', 'end', values=(
                category['id'],
                category['name'],
                category['description'] or '',
                category['product_count']
            ))
    
    def on_product_search(self, *args):
        """Handle product search"""
        search_term = self.product_search_var.get().lower()
        
        # If search is empty, show all products
        if not search_term:
            self.refresh_products()
            return
        
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Search products
        query = """
        SELECT p.*, c.name as category_name,
               COUNT(i.id) as stock_count,
               COUNT(CASE WHEN i.status = 'available' THEN 1 END) as available_count
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.is_active = 1 AND (
            LOWER(p.name) LIKE ? OR
            LOWER(p.brand) LIKE ? OR
            LOWER(p.model) LIKE ? OR
            p.barcode LIKE ? OR
            p.sku LIKE ?
        )
        GROUP BY p.id
        ORDER BY p.name
        """
        
        search_pattern = f"%{search_term}%"
        products = self.db_manager.fetch_all(query, (search_pattern, search_pattern, 
                                                    search_pattern, search_pattern, search_pattern))
        
        for product in products:
            stock_text = f"{product['available_count']}/{product['stock_count']}"
            status = "Hoạt động" if product['is_active'] else "Tạm dừng"
            
            if product['available_count'] <= BUSINESS_RULES['LOW_STOCK_THRESHOLD']:
                status = "⚠️ Sắp hết hàng"
            
            self.products_tree.insert('', 'end', values=(
                product['id'],
                product['name'],
                product['brand'] or '',
                product['model'] or '',
                product['category_name'] or '',
                f"{product['cost_price']:,.0f}",
                f"{product['selling_price']:,.0f}",
                stock_text,
                status
            ))
    
    def on_inventory_search(self, *args):
        """Handle inventory search by IMEI/Serial"""
        search_term = self.inventory_search_var.get().lower()
        
        if not search_term:
            self.refresh_inventory()
            return
        
        # Clear existing items
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Search inventory
        query = """
        SELECT i.*, p.name as product_name, p.brand, p.model
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        WHERE LOWER(i.imei) LIKE ? OR LOWER(i.serial_number) LIKE ?
        ORDER BY i.created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        inventory_items = self.db_manager.fetch_all(query, (search_pattern, search_pattern))
        
        for item in inventory_items:
            product_display = f"{item['product_name']}"
            if item['brand']:
                product_display += f" ({item['brand']})"
            
            self.inventory_tree.insert('', 'end', values=(
                item['id'],
                product_display,
                item['imei'] or '',
                item['serial_number'] or '',
                item['condition'] or 'new',
                item['status'] or 'available',
                f"{(item['cost_price'] or 0):,.0f}",
                f"{(item['selling_price'] or 0):,.0f}",
                item['location'] or ''
            ))
    
    def add_product(self):
        """Add new product"""
        self.show_product_dialog()
    
    def edit_product(self):
        """Edit selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần sửa!")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        self.show_product_dialog(product_id)
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần xóa!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sản phẩm này?"):
            item = self.products_tree.item(selection[0])
            product_id = item['values'][0]
            
            try:
                # Soft delete by setting is_active = 0
                self.db_manager.execute_query(
                    "UPDATE products SET is_active = 0 WHERE id = ?",
                    (product_id,)
                )
                messagebox.showinfo("Thành công", "Đã xóa sản phẩm!")
                self.refresh_products()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa sản phẩm: {e}")
    
    def show_product_dialog(self, product_id=None):
        """Show add/edit product dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thêm sản phẩm" if product_id is None else "Sửa sản phẩm")
        dialog.geometry("600x500")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry("+%d+%d" % (
            self.frame.winfo_rootx() + 50,
            self.frame.winfo_rooty() + 50
        ))
        
        # Load existing product data if editing
        product_data = {}
        if product_id:
            product = self.db_manager.fetch_one("SELECT * FROM products WHERE id = ?", (product_id,))
            if product:
                product_data = dict(product)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        row = 0
        
        # Name
        ttk.Label(main_frame, text="Tên sản phẩm *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=product_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Category
        ttk.Label(main_frame, text="Danh mục:").grid(row=row, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=category_var, width=37)
        
        # Load categories
        categories = self.db_manager.fetch_all("SELECT id, name FROM categories ORDER BY name")
        category_combo['values'] = [f"{cat['id']} - {cat['name']}" for cat in categories]
        
        if product_data.get('category_id'):
            for i, cat in enumerate(categories):
                if cat['id'] == product_data['category_id']:
                    category_combo.current(i)
                    break
        
        category_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Brand
        ttk.Label(main_frame, text="Thương hiệu:").grid(row=row, column=0, sticky=tk.W, pady=5)
        brand_var = tk.StringVar(value=product_data.get('brand', ''))
        brand_entry = ttk.Entry(main_frame, textvariable=brand_var, width=40)
        brand_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Model
        ttk.Label(main_frame, text="Mẫu mã:").grid(row=row, column=0, sticky=tk.W, pady=5)
        model_var = tk.StringVar(value=product_data.get('model', ''))
        model_entry = ttk.Entry(main_frame, textvariable=model_var, width=40)
        model_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # SKU
        ttk.Label(main_frame, text="Mã SKU:").grid(row=row, column=0, sticky=tk.W, pady=5)
        sku_var = tk.StringVar(value=product_data.get('sku', ''))
        sku_entry = ttk.Entry(main_frame, textvariable=sku_var, width=40)
        sku_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Barcode
        ttk.Label(main_frame, text="Mã vạch:").grid(row=row, column=0, sticky=tk.W, pady=5)
        barcode_var = tk.StringVar(value=product_data.get('barcode', ''))
        barcode_entry = ttk.Entry(main_frame, textvariable=barcode_var, width=30)
        barcode_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(main_frame, text="Tạo mã", 
                  command=lambda: barcode_var.set(str(uuid.uuid4().int)[:12])).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Cost price
        ttk.Label(main_frame, text="Giá nhập *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_price_var = tk.StringVar(value=str(product_data.get('cost_price', 0)))
        cost_price_entry = ttk.Entry(main_frame, textvariable=cost_price_var, width=40)
        cost_price_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Selling price
        ttk.Label(main_frame, text="Giá bán *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        selling_price_var = tk.StringVar(value=str(product_data.get('selling_price', 0)))
        selling_price_entry = ttk.Entry(main_frame, textvariable=selling_price_var, width=40)
        selling_price_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Warranty months
        ttk.Label(main_frame, text="Bảo hành (tháng):").grid(row=row, column=0, sticky=tk.W, pady=5)
        warranty_var = tk.StringVar(value=str(product_data.get('warranty_months', 12)))
        warranty_entry = ttk.Entry(main_frame, textvariable=warranty_var, width=40)
        warranty_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Track IMEI
        track_imei_var = tk.BooleanVar(value=product_data.get('track_imei', False))
        track_imei_check = ttk.Checkbutton(main_frame, text="Theo dõi IMEI", variable=track_imei_var)
        track_imei_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Description
        ttk.Label(main_frame, text="Mô tả:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(main_frame, width=40, height=5)
        description_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        if product_data.get('description'):
            description_text.insert('1.0', product_data['description'])
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        def save_product():
            if not name_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tên sản phẩm!")
                return
            
            try:
                cost_price = float(cost_price_var.get() or 0)
                selling_price = float(selling_price_var.get() or 0)
                warranty_months = int(warranty_var.get() or 12)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá trị không hợp lệ!")
                return
            
            # Get category ID
            category_id = None
            if category_var.get():
                category_id = int(category_var.get().split(' - ')[0])
            
            # Prepare data
            product_data = {
                'name': name_var.get().strip(),
                'category_id': category_id,
                'brand': brand_var.get().strip(),
                'model': model_var.get().strip(),
                'sku': sku_var.get().strip(),
                'barcode': barcode_var.get().strip(),
                'cost_price': cost_price,
                'selling_price': selling_price,
                'warranty_months': warranty_months,
                'track_imei': track_imei_var.get(),
                'description': description_text.get('1.0', tk.END).strip(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if product_id:
                    # Update existing product
                    set_clause = ', '.join([f"{key} = ?" for key in product_data.keys()])
                    query = f"UPDATE products SET {set_clause} WHERE id = ?"
                    params = list(product_data.values()) + [product_id]
                else:
                    # Insert new product
                    product_data['created_at'] = datetime.now().isoformat()
                    columns = ', '.join(product_data.keys())
                    placeholders = ', '.join(['?' for _ in product_data])
                    query = f"INSERT INTO products ({columns}) VALUES ({placeholders})"
                    params = list(product_data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật sản phẩm!" if product_id else "Đã thêm sản phẩm!")
                dialog.destroy()
                self.refresh_products()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu sản phẩm: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
    
    def add_inventory(self):
        """Add inventory item"""
        self.show_inventory_dialog()
    
    def edit_inventory(self):
        """Edit selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn mục cần sửa!")
            return
        
        item = self.inventory_tree.item(selection[0])
        inventory_id = item['values'][0]
        self.show_inventory_dialog(inventory_id)
    
    def show_inventory_dialog(self, inventory_id=None):
        """Show add/edit inventory dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Nhập kho" if inventory_id is None else "Sửa thông tin kho")
        dialog.geometry("500x600")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing inventory data if editing
        inventory_data = {}
        if inventory_id:
            inventory = self.db_manager.fetch_one("SELECT * FROM inventory WHERE id = ?", (inventory_id,))
            if inventory:
                inventory_data = dict(inventory)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Product selection
        ttk.Label(main_frame, text="Sản phẩm *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        product_var = tk.StringVar()
        product_combo = ttk.Combobox(main_frame, textvariable=product_var, width=40, state="readonly")
        
        # Load products
        products = self.db_manager.fetch_all(
            "SELECT id, name, brand, model FROM products WHERE is_active = 1 ORDER BY name"
        )
        product_combo['values'] = [f"{p['id']} - {p['name']} ({p['brand']} {p['model']})" 
                                  for p in products]
        
        if inventory_data.get('product_id'):
            for i, product in enumerate(products):
                if product['id'] == inventory_data['product_id']:
                    product_combo.current(i)
                    break
        
        product_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # IMEI
        ttk.Label(main_frame, text="IMEI:").grid(row=row, column=0, sticky=tk.W, pady=5)
        imei_var = tk.StringVar(value=inventory_data.get('imei', ''))
        imei_entry = ttk.Entry(main_frame, textvariable=imei_var, width=40)
        imei_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Serial Number
        ttk.Label(main_frame, text="Serial Number:").grid(row=row, column=0, sticky=tk.W, pady=5)
        serial_var = tk.StringVar(value=inventory_data.get('serial_number', ''))
        serial_entry = ttk.Entry(main_frame, textvariable=serial_var, width=40)
        serial_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Condition
        ttk.Label(main_frame, text="Tình trạng:").grid(row=row, column=0, sticky=tk.W, pady=5)
        condition_var = tk.StringVar(value=inventory_data.get('condition', 'new'))
        condition_combo = ttk.Combobox(main_frame, textvariable=condition_var, width=37, 
                                      values=['new', 'like_new', 'good', 'fair', 'poor'], state="readonly")
        condition_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Status
        ttk.Label(main_frame, text="Trạng thái:").grid(row=row, column=0, sticky=tk.W, pady=5)
        status_var = tk.StringVar(value=inventory_data.get('status', 'available'))
        status_combo = ttk.Combobox(main_frame, textvariable=status_var, width=37,
                                   values=['available', 'sold', 'reserved', 'repair', 'damaged'],
                                   state="readonly")
        status_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Cost price
        ttk.Label(main_frame, text="Giá nhập:").grid(row=row, column=0, sticky=tk.W, pady=5)
        cost_price_var = tk.StringVar(value=str(inventory_data.get('cost_price', 0) or 0))
        cost_price_entry = ttk.Entry(main_frame, textvariable=cost_price_var, width=40)
        cost_price_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Selling price
        ttk.Label(main_frame, text="Giá bán:").grid(row=row, column=0, sticky=tk.W, pady=5)
        selling_price_var = tk.StringVar(value=str(inventory_data.get('selling_price', 0) or 0))
        selling_price_entry = ttk.Entry(main_frame, textvariable=selling_price_var, width=40)
        selling_price_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Location
        ttk.Label(main_frame, text="Vị trí:").grid(row=row, column=0, sticky=tk.W, pady=5)
        location_var = tk.StringVar(value=inventory_data.get('location', ''))
        location_entry = ttk.Entry(main_frame, textvariable=location_var, width=40)
        location_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Purchase date
        ttk.Label(main_frame, text="Ngày nhập:").grid(row=row, column=0, sticky=tk.W, pady=5)
        purchase_date_var = tk.StringVar(value=inventory_data.get('purchase_date', ''))
        purchase_date_entry = ttk.Entry(main_frame, textvariable=purchase_date_var, width=40)
        purchase_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Add date picker button
        def set_today():
            purchase_date_var.set(date.today().strftime('%Y-%m-%d'))
        
        ttk.Button(main_frame, text="Hôm nay", command=set_today).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Notes
        ttk.Label(main_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(main_frame, width=40, height=4)
        notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        if inventory_data.get('notes'):
            notes_text.insert('1.0', inventory_data['notes'])
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        def save_inventory():
            if not product_var.get():
                messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm!")
                return
            
            try:
                cost_price = float(cost_price_var.get() or 0)
                selling_price = float(selling_price_var.get() or 0)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá trị không hợp lệ!")
                return
            
            # Get product ID
            product_id = int(product_var.get().split(' - ')[0])
            
            # Prepare data
            data = {
                'product_id': product_id,
                'imei': imei_var.get().strip(),
                'serial_number': serial_var.get().strip(),
                'condition': condition_var.get(),
                'status': status_var.get(),
                'cost_price': cost_price if cost_price > 0 else None,
                'selling_price': selling_price if selling_price > 0 else None,
                'location': location_var.get().strip(),
                'purchase_date': purchase_date_var.get() if purchase_date_var.get() else None,
                'notes': notes_text.get('1.0', tk.END).strip(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if inventory_id:
                    # Update existing item
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                    query = f"UPDATE inventory SET {set_clause} WHERE id = ?"
                    params = list(data.values()) + [inventory_id]
                else:
                    # Insert new item
                    data['created_at'] = datetime.now().isoformat()
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    query = f"INSERT INTO inventory ({columns}) VALUES ({placeholders})"
                    params = list(data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật kho!" if inventory_id else "Đã nhập kho!")
                dialog.destroy()
                self.refresh_inventory()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Set today's date by default for new items
        if not inventory_id:
            set_today()
    
    def print_barcode(self):
        """Print barcode for selected inventory item"""
        selection = self.inventory_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sản phẩm cần in mã vạch!")
            return
        
        item = self.inventory_tree.item(selection[0])
        inventory_id = item['values'][0]
        imei = item['values'][2]
        
        if imei:
            try:
                from utils.barcode_utils import generate_and_print_barcode
                generate_and_print_barcode(imei, f"IMEI: {imei}")
                messagebox.showinfo("Thành công", "Đã tạo mã vạch!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo mã vạch: {e}")
        else:
            messagebox.showwarning("Cảnh báo", "Sản phẩm này không có IMEI!")
    
    def show_low_stock(self):
        """Show low stock alert"""
        query = """
        SELECT p.name, p.brand, p.model, 
               COUNT(CASE WHEN i.status = 'available' THEN 1 END) as available_count
        FROM products p
        LEFT JOIN inventory i ON p.id = i.product_id
        WHERE p.is_active = 1
        GROUP BY p.id
        HAVING available_count <= ?
        ORDER BY available_count ASC
        """
        
        low_stock_products = self.db_manager.fetch_all(query, (BUSINESS_RULES['LOW_STOCK_THRESHOLD'],))
        
        if not low_stock_products:
            messagebox.showinfo("Thông báo", "Không có sản phẩm nào sắp hết hàng!")
            return
        
        # Show low stock dialog
        dialog = tk.Toplevel(self.frame)
        dialog.title("⚠️ Cảnh báo sắp hết hàng")
        dialog.geometry("600x400")
        dialog.transient(self.frame)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Các sản phẩm sắp hết hàng:", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview for low stock items
        tree = ttk.Treeview(main_frame, columns=('product', 'stock'), show='headings')
        tree.heading('product', text='Sản phẩm')
        tree.heading('stock', text='Tồn kho')
        tree.column('product', width=400)
        tree.column('stock', width=100)
        
        for product in low_stock_products:
            product_name = product['name']
            if product['brand']:
                product_name += f" ({product['brand']})"
            
            tree.insert('', 'end', values=(
                product_name,
                product['available_count']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(main_frame, text="Đóng", command=dialog.destroy).pack(pady=10)
    
    def add_category(self):
        """Add new category"""
        self.show_category_dialog()
    
    def edit_category(self):
        """Edit selected category"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn danh mục cần sửa!")
            return
        
        item = self.categories_tree.item(selection[0])
        category_id = item['values'][0]
        self.show_category_dialog(category_id)
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.categories_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn danh mục cần xóa!")
            return
        
        item = self.categories_tree.item(selection[0])
        category_id = item['values'][0]
        product_count = item['values'][3]
        
        if product_count > 0:
            messagebox.showwarning("Cảnh báo", "Không thể xóa danh mục có sản phẩm!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa danh mục này?"):
            try:
                self.db_manager.execute_query("DELETE FROM categories WHERE id = ?", (category_id,))
                messagebox.showinfo("Thành công", "Đã xóa danh mục!")
                self.refresh_categories()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa danh mục: {e}")
    
    def show_category_dialog(self, category_id=None):
        """Show add/edit category dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thêm danh mục" if category_id is None else "Sửa danh mục")
        dialog.geometry("400x200")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing category data if editing
        category_data = {}
        if category_id:
            category = self.db_manager.fetch_one("SELECT * FROM categories WHERE id = ?", (category_id,))
            if category:
                category_data = dict(category)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="Tên danh mục *:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=category_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Description
        ttk.Label(main_frame, text="Mô tả:").grid(row=1, column=0, sticky=tk.NW, pady=5)
        description_text = tk.Text(main_frame, width=30, height=4)
        description_text.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        if category_data.get('description'):
            description_text.insert('1.0', category_data['description'])
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def save_category():
            if not name_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tên danh mục!")
                return
            
            data = {
                'name': name_var.get().strip(),
                'description': description_text.get('1.0', tk.END).strip(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                if category_id:
                    # Update existing category
                    self.db_manager.execute_query(
                        "UPDATE categories SET name = ?, description = ?, updated_at = ? WHERE id = ?",
                        (data['name'], data['description'], data['updated_at'], category_id)
                    )
                else:
                    # Insert new category
                    self.db_manager.execute_query(
                        "INSERT INTO categories (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (data['name'], data['description'], datetime.now().isoformat(), data['updated_at'])
                    )
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật danh mục!" if category_id else "Đã thêm danh mục!")
                dialog.destroy()
                self.refresh_categories()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu danh mục: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
