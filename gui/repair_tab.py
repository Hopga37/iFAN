#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repair management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import uuid

from models import Repair, Customer
from utils.qr_utils import generate_qr_code
from config import BUSINESS_RULES

class RepairTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup repair tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # New Repair tab
        self.setup_new_repair_tab()
        
        # Repair List tab
        self.setup_repair_list_tab()
        
        # Repair Status tab
        self.setup_repair_status_tab()
    
    def setup_new_repair_tab(self):
        """Setup new repair registration tab"""
        new_repair_frame = ttk.Frame(self.notebook)
        self.notebook.add(new_repair_frame, text="Tiếp Nhận Sửa Chữa")
        
        # Main form
        form_frame = ttk.LabelFrame(new_repair_frame, text="Thông tin sửa chữa", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create form in two columns
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left column - Basic info
        row = 0
        
        # Repair number
        ttk.Label(left_frame, text="Số biên nhận:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.repair_number_var = tk.StringVar()
        repair_number_entry = ttk.Entry(left_frame, textvariable=self.repair_number_var, width=25, state="readonly")
        repair_number_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(left_frame, text="Tạo mã", 
                  command=self.generate_repair_number).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Customer info
        ttk.Label(left_frame, text="Khách hàng *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(left_frame, textvariable=self.customer_var, width=35)
        customer_combo.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        self.load_customers_combo(customer_combo)
        
        ttk.Button(left_frame, text="➕", 
                  command=self.add_customer).grid(row=row, column=3, pady=5, padx=(5, 0))
        row += 1
        
        # Device info
        ttk.Label(left_frame, text="Thông tin thiết bị *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.device_info_var = tk.StringVar()
        device_info_entry = ttk.Entry(left_frame, textvariable=self.device_info_var, width=40)
        device_info_entry.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # IMEI
        ttk.Label(left_frame, text="IMEI:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.imei_var = tk.StringVar()
        imei_entry = ttk.Entry(left_frame, textvariable=self.imei_var, width=40)
        imei_entry.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Problem description
        ttk.Label(left_frame, text="Mô tả lỗi *:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.problem_text = tk.Text(left_frame, width=40, height=6)
        self.problem_text.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Estimated completion
        ttk.Label(left_frame, text="Dự kiến hoàn thành:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.estimated_completion_var = tk.StringVar()
        estimated_entry = ttk.Entry(left_frame, textvariable=self.estimated_completion_var, width=25)
        estimated_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(left_frame, text="Hôm nay + 3", 
                  command=self.set_estimated_date).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Right column - Cost and notes
        row = 0
        
        # Labor cost
        ttk.Label(right_frame, text="Tiền công:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.labor_cost_var = tk.StringVar(value="0")
        labor_cost_entry = ttk.Entry(right_frame, textvariable=self.labor_cost_var, width=20)
        labor_cost_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Parts cost
        ttk.Label(right_frame, text="Tiền linh kiện:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.parts_cost_var = tk.StringVar(value="0")
        parts_cost_entry = ttk.Entry(right_frame, textvariable=self.parts_cost_var, width=20)
        parts_cost_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Total cost (calculated)
        ttk.Label(right_frame, text="Tổng chi phí:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.total_cost_label = ttk.Label(right_frame, text="0 VNĐ", 
                                         style="Success.TLabel", font=('Arial', 10, 'bold'))
        self.total_cost_label.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Bind cost calculation
        labor_cost_entry.bind('<KeyRelease>', self.calculate_total_cost)
        parts_cost_entry.bind('<KeyRelease>', self.calculate_total_cost)
        
        # Warranty months
        ttk.Label(right_frame, text="Bảo hành (tháng):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.warranty_months_var = tk.StringVar(value="3")
        warranty_entry = ttk.Entry(right_frame, textvariable=self.warranty_months_var, width=20)
        warranty_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Pattern lock info
        ttk.Label(right_frame, text="Thông tin mở khóa:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.pattern_text = tk.Text(right_frame, width=30, height=4)
        self.pattern_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(right_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(right_frame, width=30, height=4)
        self.notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="💾 Lưu biên nhận", 
                  command=self.save_repair).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In biên nhận", 
                  command=self.print_repair_receipt).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa form", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Generate initial repair number
        self.generate_repair_number()
    
    def setup_repair_list_tab(self):
        """Setup repair list management tab"""
        repair_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(repair_list_frame, text="Danh Sách Sửa Chữa")
        
        # Top controls
        top_frame = ttk.Frame(repair_list_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="Số biên nhận / IMEI / KH:").pack(anchor=tk.W)
        self.repair_search_var = tk.StringVar()
        self.repair_search_var.trace('w', self.on_repair_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.repair_search_var, width=40)
        search_entry.pack(pady=5, fill=tk.X)
        
        # Status filter
        status_frame = ttk.LabelFrame(top_frame, text="Lọc trạng thái", padding=10)
        status_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_filter_var = tk.StringVar(value="all")
        status_values = [
            ("all", "Tất cả"),
            ("received", "Đã tiếp nhận"),
            ("diagnosing", "Đang chẩn đoán"),
            ("repairing", "Đang sửa chữa"),
            ("waiting_parts", "Chờ linh kiện"),
            ("completed", "Hoàn thành"),
            ("customer_notified", "Đã báo khách"),
            ("delivered", "Đã giao"),
            ("cancelled", "Hủy bỏ")
        ]
        
        for value, text in status_values:
            ttk.Radiobutton(status_frame, text=text, variable=self.status_filter_var,
                           value=value, command=self.filter_repairs).pack(anchor=tk.W)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="👁️ Xem chi tiết", 
                  command=self.view_repair_details).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_repair).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="📋 Cập nhật trạng thái", 
                  command=self.update_repair_status).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🖨️ In biên nhận", 
                  command=self.print_selected_receipt).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔔 Thông báo khách", 
                  command=self.notify_customer).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_repairs).pack(pady=2, fill=tk.X)
        
        # Repairs treeview
        tree_frame = ttk.Frame(repair_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.repairs_tree = ttk.Treeview(tree_frame,
                                        columns=('id', 'repair_number', 'date', 'customer', 'device',
                                               'imei', 'problem', 'status', 'total_cost', 'completion'),
                                        show='headings',
                                        yscrollcommand=v_scrollbar.set,
                                        xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.repairs_tree.yview)
        h_scrollbar.config(command=self.repairs_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'repair_number': ('Số biên nhận', 120),
            'date': ('Ngày tiếp nhận', 120),
            'customer': ('Khách hàng', 150),
            'device': ('Thiết bị', 150),
            'imei': ('IMEI', 150),
            'problem': ('Lỗi', 200),
            'status': ('Trạng thái', 120),
            'total_cost': ('Chi phí', 100),
            'completion': ('Hoàn thành', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.repairs_tree.heading(col, text=heading)
            self.repairs_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.repairs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.repairs_tree.bind('<Double-1>', lambda e: self.view_repair_details())
    
    def setup_repair_status_tab(self):
        """Setup repair status tracking tab"""
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="Tra Cứu Trạng Thái")
        
        # Search section
        search_section = ttk.LabelFrame(status_frame, text="Tra cứu theo QR Code / Số biên nhận", padding=20)
        search_section.pack(fill=tk.X, padx=20, pady=20)
        
        # QR Code lookup
        ttk.Label(search_section, text="Quét QR Code hoặc nhập số biên nhận:", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        lookup_frame = ttk.Frame(search_section)
        lookup_frame.pack(fill=tk.X)
        
        self.qr_lookup_var = tk.StringVar()
        qr_entry = ttk.Entry(lookup_frame, textvariable=self.qr_lookup_var, width=30, font=('Arial', 14))
        qr_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(lookup_frame, text="🔍 Tra cứu", 
                  command=self.lookup_repair_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(lookup_frame, text="📷 Quét QR", 
                  command=self.scan_qr_code).pack(side=tk.LEFT, padx=5)
        
        # Results section
        self.results_frame = ttk.LabelFrame(status_frame, text="Kết quả tra cứu", padding=20)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Initially hide results
        self.results_frame.pack_forget()
        
        # Focus on QR entry
        qr_entry.focus_set()
    
    def load_data(self):
        """Load all data"""
        self.refresh_repairs()
    
    def load_customers_combo(self, combo):
        """Load customers into combobox"""
        customers = self.db_manager.fetch_all("SELECT id, name, phone FROM customers ORDER BY name")
        combo['values'] = [""] + [f"{c['id']} - {c['name']} ({c['phone']})" for c in customers if c['phone']]
    
    def generate_repair_number(self):
        """Generate unique repair number"""
        repair_number = f"SC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.repair_number_var.set(repair_number)
    
    def set_estimated_date(self):
        """Set estimated completion date to today + 3 days"""
        from datetime import timedelta
        estimated_date = (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
        self.estimated_completion_var.set(estimated_date)
    
    def calculate_total_cost(self, event=None):
        """Calculate total repair cost"""
        try:
            labor_cost = float(self.labor_cost_var.get() or 0)
            parts_cost = float(self.parts_cost_var.get() or 0)
            total = labor_cost + parts_cost
            
            self.total_cost_label.config(text=f"{total:,.0f} VNĐ")
        except ValueError:
            self.total_cost_label.config(text="0 VNĐ")
    
    def add_customer(self):
        """Add new customer"""
        # Use the same customer dialog from sales tab
        self.show_customer_dialog()
    
    def show_customer_dialog(self):
        """Show add customer dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thêm khách hàng")
        dialog.geometry("500x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Name
        ttk.Label(main_frame, text="Tên khách hàng *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=40)
        name_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Phone
        ttk.Label(main_frame, text="Số điện thoại *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        phone_var = tk.StringVar()
        phone_entry = ttk.Entry(main_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Address
        ttk.Label(main_frame, text="Địa chỉ:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        address_text = tk.Text(main_frame, width=40, height=3)
        address_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_customer():
            if not name_var.get().strip() or not phone_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tên và số điện thoại!")
                return
            
            data = {
                'name': name_var.get().strip(),
                'phone': phone_var.get().strip(),
                'address': address_text.get('1.0', tk.END).strip(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            try:
                columns = ', '.join(data.keys())
                placeholders = ', '.join(['?' for _ in data])
                query = f"INSERT INTO customers ({columns}) VALUES ({placeholders})"
                self.db_manager.execute_query(query, list(data.values()))
                
                messagebox.showinfo("Thành công", "Đã thêm khách hàng!")
                dialog.destroy()
                
                # Reload customer combo
                for widget in self.frame.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for subwidget in widget.winfo_children():
                            if isinstance(subwidget, ttk.Notebook):
                                # Find and reload customer combo
                                pass
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu khách hàng: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
    
    def save_repair(self):
        """Save repair record"""
        # Validate required fields
        if not self.repair_number_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng tạo số biên nhận!")
            return
        
        if not self.customer_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng!")
            return
        
        if not self.device_info_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập thông tin thiết bị!")
            return
        
        if not self.problem_text.get('1.0', tk.END).strip():
            messagebox.showerror("Lỗi", "Vui lòng mô tả lỗi!")
            return
        
        try:
            # Get customer ID
            customer_id = int(self.customer_var.get().split(' - ')[0])
            
            # Get costs
            labor_cost = float(self.labor_cost_var.get() or 0)
            parts_cost = float(self.parts_cost_var.get() or 0)
            total_cost = labor_cost + parts_cost
            warranty_months = int(self.warranty_months_var.get() or 3)
            
            # Generate QR code
            qr_code = generate_qr_code(f"REPAIR:{self.repair_number_var.get()}")
            
            # Prepare repair data
            repair_data = {
                'repair_number': self.repair_number_var.get().strip(),
                'customer_id': customer_id,
                'staff_id': self.current_user['id'],
                'device_info': self.device_info_var.get().strip(),
                'imei': self.imei_var.get().strip(),
                'problem_description': self.problem_text.get('1.0', tk.END).strip(),
                'repair_status': 'received',
                'labor_cost': labor_cost,
                'parts_cost': parts_cost,
                'total_cost': total_cost,
                'estimated_completion': self.estimated_completion_var.get() if self.estimated_completion_var.get() else None,
                'warranty_months': warranty_months,
                'qr_code': qr_code,
                'pattern_lock_info': self.pattern_text.get('1.0', tk.END).strip(),
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert repair record
            columns = ', '.join(repair_data.keys())
            placeholders = ', '.join(['?' for _ in repair_data])
            query = f"INSERT INTO repairs ({columns}) VALUES ({placeholders})"
            cursor = self.db_manager.execute_query(query, list(repair_data.values()))
            repair_id = cursor.lastrowid
            
            # Create transaction record
            transaction_data = {
                'transaction_type': 'expense',
                'amount': 0,  # No payment yet
                'description': f'Tiếp nhận sửa chữa - {self.repair_number_var.get()}',
                'reference_id': repair_id,
                'reference_type': 'repair',
                'payment_method': 'cash',
                'staff_id': self.current_user['id'],
                'transaction_date': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            columns = ', '.join(transaction_data.keys())
            placeholders = ', '.join(['?' for _ in transaction_data])
            query = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
            self.db_manager.execute_query(query, list(transaction_data.values()))
            
            messagebox.showinfo("Thành công", f"Đã tạo biên nhận sửa chữa {self.repair_number_var.get()}!")
            
            # Ask to print receipt
            if messagebox.askyesno("In biên nhận", "Bạn có muốn in biên nhận không?"):
                self.print_repair_receipt_by_id(repair_id)
            
            # Clear form
            self.clear_form()
            
            # Refresh repairs list
            self.refresh_repairs()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu biên nhận: {e}")
    
    def print_repair_receipt(self):
        """Print repair receipt for current form"""
        repair_number = self.repair_number_var.get()
        if not repair_number:
            messagebox.showwarning("Cảnh báo", "Chưa có số biên nhận!")
            return
        
        # Find repair by number
        repair = self.db_manager.fetch_one(
            "SELECT id FROM repairs WHERE repair_number = ?",
            (repair_number,)
        )
        
        if repair:
            self.print_repair_receipt_by_id(repair['id'])
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng lưu biên nhận trước khi in!")
    
    def print_repair_receipt_by_id(self, repair_id):
        """Print repair receipt by ID"""
        try:
            from utils.print_utils import print_repair_receipt
            print_repair_receipt(self.db_manager, repair_id)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in biên nhận: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.generate_repair_number()
        self.customer_var.set("")
        self.device_info_var.set("")
        self.imei_var.set("")
        self.problem_text.delete('1.0', tk.END)
        self.estimated_completion_var.set("")
        self.labor_cost_var.set("0")
        self.parts_cost_var.set("0")
        self.warranty_months_var.set("3")
        self.pattern_text.delete('1.0', tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.calculate_total_cost()
    
    def refresh_repairs(self):
        """Refresh repairs list"""
        # Clear existing items
        for item in self.repairs_tree.get_children():
            self.repairs_tree.delete(item)
        
        # Load repairs
        query = """
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repairs r
        LEFT JOIN customers c ON r.customer_id = c.id
        ORDER BY r.created_at DESC
        """
        
        repairs = self.db_manager.fetch_all(query)
        
        for repair in repairs:
            repair_date = datetime.fromisoformat(repair['created_at']).strftime('%d/%m/%Y')
            completion_date = ""
            if repair['actual_completion']:
                completion_date = datetime.fromisoformat(repair['actual_completion']).strftime('%d/%m/%Y')
            elif repair['estimated_completion']:
                completion_date = f"DK: {repair['estimated_completion']}"
            
            # Status translation
            status_map = {
                'received': 'Đã tiếp nhận',
                'diagnosing': 'Đang chẩn đoán',
                'repairing': 'Đang sửa chữa',
                'waiting_parts': 'Chờ linh kiện',
                'completed': 'Hoàn thành',
                'customer_notified': 'Đã báo khách',
                'delivered': 'Đã giao',
                'cancelled': 'Hủy bỏ'
            }
            
            status_text = status_map.get(repair['repair_status'], repair['repair_status'])
            
            self.repairs_tree.insert('', 'end', values=(
                repair['id'],
                repair['repair_number'],
                repair_date,
                repair['customer_name'] or '',
                repair['device_info'][:30] + "..." if len(repair['device_info']) > 30 else repair['device_info'],
                repair['imei'] or '',
                repair['problem_description'][:50] + "..." if len(repair['problem_description']) > 50 else repair['problem_description'],
                status_text,
                f"{repair['total_cost']:,.0f}",
                completion_date
            ))
    
    def on_repair_search(self, *args):
        """Handle repair search"""
        search_term = self.repair_search_var.get().lower()
        
        if not search_term:
            self.refresh_repairs()
            return
        
        # Clear existing items
        for item in self.repairs_tree.get_children():
            self.repairs_tree.delete(item)
        
        # Search repairs
        query = """
        SELECT r.*, c.name as customer_name, c.phone as customer_phone
        FROM repairs r
        LEFT JOIN customers c ON r.customer_id = c.id
        WHERE LOWER(r.repair_number) LIKE ? OR
              LOWER(r.imei) LIKE ? OR
              LOWER(c.name) LIKE ? OR
              LOWER(r.device_info) LIKE ?
        ORDER BY r.created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        repairs = self.db_manager.fetch_all(query, (search_pattern, search_pattern, 
                                                   search_pattern, search_pattern))
        
        for repair in repairs:
            repair_date = datetime.fromisoformat(repair['created_at']).strftime('%d/%m/%Y')
            completion_date = ""
            if repair['actual_completion']:
                completion_date = datetime.fromisoformat(repair['actual_completion']).strftime('%d/%m/%Y')
            elif repair['estimated_completion']:
                completion_date = f"DK: {repair['estimated_completion']}"
            
            status_map = {
                'received': 'Đã tiếp nhận',
                'diagnosing': 'Đang chẩn đoán',
                'repairing': 'Đang sửa chữa',
                'waiting_parts': 'Chờ linh kiện',
                'completed': 'Hoàn thành',
                'customer_notified': 'Đã báo khách',
                'delivered': 'Đã giao',
                'cancelled': 'Hủy bỏ'
            }
            
            status_text = status_map.get(repair['repair_status'], repair['repair_status'])
            
            self.repairs_tree.insert('', 'end', values=(
                repair['id'],
                repair['repair_number'],
                repair_date,
                repair['customer_name'] or '',
                repair['device_info'][:30] + "..." if len(repair['device_info']) > 30 else repair['device_info'],
                repair['imei'] or '',
                repair['problem_description'][:50] + "..." if len(repair['problem_description']) > 50 else repair['problem_description'],
                status_text,
                f"{repair['total_cost']:,.0f}",
                completion_date
            ))
    
    def filter_repairs(self):
        """Filter repairs by status"""
        status_filter = self.status_filter_var.get()
        
        # Clear existing items
        for item in self.repairs_tree.get_children():
            self.repairs_tree.delete(item)
        
        # Build query based on filter
        if status_filter == "all":
            query = """
            SELECT r.*, c.name as customer_name, c.phone as customer_phone
            FROM repairs r
            LEFT JOIN customers c ON r.customer_id = c.id
            ORDER BY r.created_at DESC
            """
            params = ()
        else:
            query = """
            SELECT r.*, c.name as customer_name, c.phone as customer_phone
            FROM repairs r
            LEFT JOIN customers c ON r.customer_id = c.id
            WHERE r.repair_status = ?
            ORDER BY r.created_at DESC
            """
            params = (status_filter,)
        
        repairs = self.db_manager.fetch_all(query, params)
        
        for repair in repairs:
            repair_date = datetime.fromisoformat(repair['created_at']).strftime('%d/%m/%Y')
            completion_date = ""
            if repair['actual_completion']:
                completion_date = datetime.fromisoformat(repair['actual_completion']).strftime('%d/%m/%Y')
            elif repair['estimated_completion']:
                completion_date = f"DK: {repair['estimated_completion']}"
            
            status_map = {
                'received': 'Đã tiếp nhận',
                'diagnosing': 'Đang chẩn đoán',
                'repairing': 'Đang sửa chữa',
                'waiting_parts': 'Chờ linh kiện',
                'completed': 'Hoàn thành',
                'customer_notified': 'Đã báo khách',
                'delivered': 'Đã giao',
                'cancelled': 'Hủy bỏ'
            }
            
            status_text = status_map.get(repair['repair_status'], repair['repair_status'])
            
            self.repairs_tree.insert('', 'end', values=(
                repair['id'],
                repair['repair_number'],
                repair_date,
                repair['customer_name'] or '',
                repair['device_info'][:30] + "..." if len(repair['device_info']) > 30 else repair['device_info'],
                repair['imei'] or '',
                repair['problem_description'][:50] + "..." if len(repair['problem_description']) > 50 else repair['problem_description'],
                status_text,
                f"{repair['total_cost']:,.0f}",
                completion_date
            ))
    
    def view_repair_details(self):
        """View repair details"""
        selection = self.repairs_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biên nhận!")
            return
        
        item = self.repairs_tree.item(selection[0])
        repair_id = item['values'][0]
        self.show_repair_details_dialog(repair_id)
    
    def show_repair_details_dialog(self, repair_id):
        """Show repair details dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Chi tiết sửa chữa")
        dialog.geometry("800x700")
        dialog.transient(self.frame)
        
        # Load repair data
        repair = self.db_manager.fetch_one(
            """SELECT r.*, c.name as customer_name, c.phone as customer_phone,
                      c.address as customer_address, st.full_name as staff_name
               FROM repairs r
               LEFT JOIN customers c ON r.customer_id = c.id
               LEFT JOIN staff st ON r.staff_id = st.id
               WHERE r.id = ?""",
            (repair_id,)
        )
        
        if not repair:
            messagebox.showerror("Lỗi", "Không tìm thấy biên nhận!")
            dialog.destroy()
            return
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic info tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Thông tin cơ bản")
        
        info_container = ttk.Frame(info_frame, padding=20)
        info_container.pack(fill=tk.BOTH, expand=True)
        
        # Repair information
        repair_info_frame = ttk.LabelFrame(info_container, text="Thông tin sửa chữa", padding=10)
        repair_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_data = [
            ("Số biên nhận:", repair['repair_number']),
            ("Ngày tiếp nhận:", datetime.fromisoformat(repair['created_at']).strftime('%d/%m/%Y %H:%M')),
            ("Nhân viên tiếp nhận:", repair['staff_name'] or ''),
            ("Trạng thái:", repair['repair_status']),
            ("Chi phí tổng:", f"{repair['total_cost']:,.0f} VNĐ"),
            ("Đã thanh toán:", f"{repair['paid_amount']:,.0f} VNĐ")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row, col = divmod(i, 2)
            ttk.Label(repair_info_frame, text=label).grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(repair_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Customer information
        customer_info_frame = ttk.LabelFrame(info_container, text="Thông tin khách hàng", padding=10)
        customer_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        customer_data = [
            ("Tên khách hàng:", repair['customer_name'] or ''),
            ("Số điện thoại:", repair['customer_phone'] or ''),
            ("Địa chỉ:", repair['customer_address'] or '')
        ]
        
        for i, (label, value) in enumerate(customer_data):
            ttk.Label(customer_info_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(customer_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Device information
        device_info_frame = ttk.LabelFrame(info_container, text="Thông tin thiết bị", padding=10)
        device_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        device_data = [
            ("Thiết bị:", repair['device_info'] or ''),
            ("IMEI:", repair['imei'] or ''),
            ("Mô tả lỗi:", repair['problem_description'] or ''),
            ("Chẩn đoán:", repair['diagnosis'] or '')
        ]
        
        for i, (label, value) in enumerate(device_data):
            ttk.Label(device_info_frame, text=label).grid(row=i, column=0, sticky=tk.NW, padx=5, pady=2)
            if len(str(value)) > 50:
                # Use text widget for long content
                text_widget = tk.Text(device_info_frame, width=60, height=3, wrap=tk.WORD)
                text_widget.insert('1.0', str(value))
                text_widget.config(state=tk.DISABLED)
                text_widget.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            else:
                ttk.Label(device_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                    row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Status history tab
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Lịch sử trạng thái")
        
        # Parts used tab
        parts_frame = ttk.Frame(notebook)
        notebook.add(parts_frame, text="Linh kiện sử dụng")
        
        # QR Code tab
        qr_frame = ttk.Frame(notebook)
        notebook.add(qr_frame, text="QR Code")
        
        if repair['qr_code']:
            qr_container = ttk.Frame(qr_frame, padding=20)
            qr_container.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(qr_container, text="QR Code tra cứu trạng thái:", 
                     style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
            
            # Display QR code info
            ttk.Label(qr_container, text=f"Mã tra cứu: {repair['repair_number']}", 
                     font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
            ttk.Label(qr_container, text="Khách hàng có thể quét QR code này để tra cứu trạng thái sửa chữa.", 
                     font=('Arial', 10)).pack(anchor=tk.W, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ In biên nhận", 
                  command=lambda: self.print_repair_receipt_by_id(repair_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Cập nhật trạng thái", 
                  command=lambda: self.update_repair_status_dialog(repair_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Đóng", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def edit_repair(self):
        """Edit selected repair"""
        selection = self.repairs_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biên nhận!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng sửa biên nhận sẽ được phát triển!")
    
    def update_repair_status(self):
        """Update repair status"""
        selection = self.repairs_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biên nhận!")
            return
        
        item = self.repairs_tree.item(selection[0])
        repair_id = item['values'][0]
        self.update_repair_status_dialog(repair_id)
    
    def update_repair_status_dialog(self, repair_id):
        """Show update repair status dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Cập nhật trạng thái sửa chữa")
        dialog.geometry("400x300")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load current repair data
        repair = self.db_manager.fetch_one("SELECT * FROM repairs WHERE id = ?", (repair_id,))
        if not repair:
            messagebox.showerror("Lỗi", "Không tìm thấy biên nhận!")
            dialog.destroy()
            return
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current status
        ttk.Label(main_frame, text=f"Biên nhận: {repair['repair_number']}", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text=f"Trạng thái hiện tại: {repair['repair_status']}", 
                 font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 20))
        
        # New status
        ttk.Label(main_frame, text="Trạng thái mới:").pack(anchor=tk.W, pady=5)
        status_var = tk.StringVar(value=repair['repair_status'])
        
        status_options = [
            ('received', 'Đã tiếp nhận'),
            ('diagnosing', 'Đang chẩn đoán'),
            ('repairing', 'Đang sửa chữa'),
            ('waiting_parts', 'Chờ linh kiện'),
            ('completed', 'Hoàn thành'),
            ('customer_notified', 'Đã báo khách'),
            ('delivered', 'Đã giao'),
            ('cancelled', 'Hủy bỏ')
        ]
        
        for value, text in status_options:
            ttk.Radiobutton(main_frame, text=text, variable=status_var, value=value).pack(anchor=tk.W, pady=2)
        
        # Notes
        ttk.Label(main_frame, text="Ghi chú:").pack(anchor=tk.W, pady=(10, 5))
        notes_text = tk.Text(main_frame, width=40, height=4)
        notes_text.pack(fill=tk.X, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        def save_status():
            new_status = status_var.get()
            notes = notes_text.get('1.0', tk.END).strip()
            
            try:
                # Update repair status
                update_data = {
                    'repair_status': new_status,
                    'updated_at': datetime.now().isoformat()
                }
                
                # If completed, set actual completion date
                if new_status == 'completed':
                    update_data['actual_completion'] = date.today().isoformat()
                
                set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
                query = f"UPDATE repairs SET {set_clause} WHERE id = ?"
                params = list(update_data.values()) + [repair_id]
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", "Đã cập nhật trạng thái!")
                dialog.destroy()
                self.refresh_repairs()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật trạng thái: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_status).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def print_selected_receipt(self):
        """Print selected repair receipt"""
        selection = self.repairs_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biên nhận!")
            return
        
        item = self.repairs_tree.item(selection[0])
        repair_id = item['values'][0]
        self.print_repair_receipt_by_id(repair_id)
    
    def notify_customer(self):
        """Notify customer about repair status"""
        selection = self.repairs_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn biên nhận!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng thông báo khách hàng sẽ được phát triển!")
    
    def lookup_repair_status(self):
        """Lookup repair status by QR code or repair number"""
        lookup_value = self.qr_lookup_var.get().strip()
        if not lookup_value:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã tra cứu!")
            return
        
        # Extract repair number from QR code if necessary
        repair_number = lookup_value
        if lookup_value.startswith("REPAIR:"):
            repair_number = lookup_value.replace("REPAIR:", "")
        
        # Find repair
        repair = self.db_manager.fetch_one(
            """SELECT r.*, c.name as customer_name, c.phone as customer_phone
               FROM repairs r
               LEFT JOIN customers c ON r.customer_id = c.id
               WHERE r.repair_number = ?""",
            (repair_number,)
        )
        
        if not repair:
            # Hide results frame
            self.results_frame.pack_forget()
            messagebox.showwarning("Không tìm thấy", f"Không tìm thấy biên nhận với mã: {repair_number}")
            return
        
        # Show results
        self.show_repair_status_results(repair)
    
    def show_repair_status_results(self, repair):
        """Show repair status lookup results"""
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Show results frame
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Title
        ttk.Label(self.results_frame, text=f"Kết quả tra cứu - {repair['repair_number']}", 
                 style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        # Create info display
        info_frame = ttk.Frame(self.results_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Status with color coding
        status_map = {
            'received': ('Đã tiếp nhận', 'blue'),
            'diagnosing': ('Đang chẩn đoán', 'orange'),
            'repairing': ('Đang sửa chữa', 'orange'),
            'waiting_parts': ('Chờ linh kiện', 'red'),
            'completed': ('Hoàn thành', 'green'),
            'customer_notified': ('Đã báo khách', 'green'),
            'delivered': ('Đã giao', 'green'),
            'cancelled': ('Hủy bỏ', 'red')
        }
        
        status_text, status_color = status_map.get(repair['repair_status'], (repair['repair_status'], 'black'))
        
        ttk.Label(info_frame, text="Trạng thái hiện tại:", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        status_label = ttk.Label(info_frame, text=status_text, font=('Arial', 14, 'bold'))
        status_label.pack(anchor=tk.W, pady=(5, 15))
        
        # Basic information
        info_data = [
            ("Thiết bị:", repair['device_info']),
            ("IMEI:", repair['imei'] or 'N/A'),
            ("Ngày tiếp nhận:", datetime.fromisoformat(repair['created_at']).strftime('%d/%m/%Y')),
            ("Khách hàng:", repair['customer_name']),
            ("SĐT liên hệ:", repair['customer_phone'] or 'N/A'),
            ("Mô tả lỗi:", repair['problem_description']),
            ("Chi phí dự kiến:", f"{repair['total_cost']:,.0f} VNĐ")
        ]
        
        for label, value in info_data:
            row_frame = ttk.Frame(info_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=label, font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=str(value)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Completion date
        if repair['estimated_completion']:
            completion_frame = ttk.Frame(info_frame)
            completion_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(completion_frame, text="Dự kiến hoàn thành:", 
                     font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(completion_frame, text=repair['estimated_completion']).pack(side=tk.LEFT, padx=(10, 0))
        
        if repair['actual_completion']:
            completion_frame = ttk.Frame(info_frame)
            completion_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(completion_frame, text="Đã hoàn thành:", 
                     font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
            ttk.Label(completion_frame, text=repair['actual_completion']).pack(side=tk.LEFT, padx=(10, 0))
        
        # Instructions
        if repair['repair_status'] in ['completed', 'customer_notified']:
            ttk.Label(info_frame, text="✅ Thiết bị đã được sửa chữa xong. Vui lòng đến cửa hàng để nhận máy.", 
                     font=('Arial', 11, 'bold'), foreground='green').pack(anchor=tk.W, pady=(15, 0))
        elif repair['repair_status'] == 'delivered':
            ttk.Label(info_frame, text="✅ Thiết bị đã được giao cho khách hàng.", 
                     font=('Arial', 11, 'bold'), foreground='green').pack(anchor=tk.W, pady=(15, 0))
        else:
            ttk.Label(info_frame, text="⏳ Thiết bị đang được sửa chữa. Vui lòng chờ thông báo từ cửa hàng.", 
                     font=('Arial', 11)).pack(anchor=tk.W, pady=(15, 0))
    
    def scan_qr_code(self):
        """Scan QR code using camera"""
        messagebox.showinfo("Thông báo", "Chức năng quét QR code bằng camera sẽ được phát triển!")
        # This would integrate with camera/QR scanning library
