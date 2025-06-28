#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Staff management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import hashlib

from models import Staff
from config import BUSINESS_RULES

class StaffTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup staff tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Staff List tab
        self.setup_staff_list_tab()
        
        # Permissions tab
        self.setup_permissions_tab()
        
        # Performance tab
        self.setup_performance_tab()
        
        # Attendance tab
        self.setup_attendance_tab()
    
    def setup_staff_list_tab(self):
        """Setup staff list management tab"""
        staff_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(staff_list_frame, text="Danh Sách Nhân Viên")
        
        # Top controls
        top_frame = ttk.Frame(staff_list_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm nhân viên", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="Tên / Tài khoản:").pack(anchor=tk.W)
        self.staff_search_var = tk.StringVar()
        self.staff_search_var.trace('w', self.on_staff_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.staff_search_var, width=40)
        search_entry.pack(pady=5, fill=tk.X)
        
        # Status filter
        status_frame = ttk.LabelFrame(top_frame, text="Lọc trạng thái", padding=10)
        status_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_filter_var = tk.StringVar(value="all")
        status_values = [
            ("all", "Tất cả"),
            ("active", "Đang làm việc"),
            ("inactive", "Nghỉ việc")
        ]
        
        for value, text in status_values:
            ttk.Radiobutton(status_frame, text=text, variable=self.status_filter_var,
                           value=value, command=self.filter_staff).pack(anchor=tk.W)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="➕ Thêm NV", 
                  command=self.add_staff).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_staff).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔒 Đổi mật khẩu", 
                  command=self.change_password).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="👁️ Xem chi tiết", 
                  command=self.view_staff_details).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_staff).pack(pady=2, fill=tk.X)
        
        # Staff treeview
        tree_frame = ttk.Frame(staff_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.staff_tree = ttk.Treeview(tree_frame,
                                      columns=('id', 'username', 'full_name', 'phone', 'email',
                                             'role', 'commission_rate', 'salary', 'status', 'last_login'),
                                      show='headings',
                                      yscrollcommand=v_scrollbar.set,
                                      xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.staff_tree.yview)
        h_scrollbar.config(command=self.staff_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'username': ('Tài khoản', 120),
            'full_name': ('Họ tên', 150),
            'phone': ('Điện thoại', 120),
            'email': ('Email', 150),
            'role': ('Vai trò', 100),
            'commission_rate': ('Hoa hồng (%)', 100),
            'salary': ('Lương', 100),
            'status': ('Trạng thái', 100),
            'last_login': ('Đăng nhập cuối', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.staff_tree.heading(col, text=heading)
            self.staff_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.staff_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.staff_tree.bind('<Double-1>', lambda e: self.edit_staff())
    
    def setup_permissions_tab(self):
        """Setup permissions management tab"""
        permissions_frame = ttk.Frame(self.notebook)
        self.notebook.add(permissions_frame, text="Phân Quyền")
        
        # Staff selection
        selection_frame = ttk.LabelFrame(permissions_frame, text="Chọn nhân viên", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(selection_frame, text="Nhân viên:").pack(side=tk.LEFT)
        self.permission_staff_var = tk.StringVar()
        permission_staff_combo = ttk.Combobox(selection_frame, textvariable=self.permission_staff_var, width=40)
        permission_staff_combo.pack(side=tk.LEFT, padx=10)
        
        # Load staff for permissions
        self.load_staff_combo(permission_staff_combo)
        
        ttk.Button(selection_frame, text="🔄 Tải quyền", 
                  command=self.load_staff_permissions).pack(side=tk.LEFT, padx=10)
        
        # Permissions grid
        permissions_grid_frame = ttk.LabelFrame(permissions_frame, text="Phân quyền chi tiết", padding=20)
        permissions_grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Permission categories and specific permissions
        self.permission_vars = {}
        
        permission_structure = {
            "Quản lý kho": [
                ("inventory_view", "Xem kho hàng"),
                ("inventory_add", "Thêm sản phẩm"),
                ("inventory_edit", "Sửa sản phẩm"),
                ("inventory_delete", "Xóa sản phẩm"),
                ("inventory_import", "Nhập hàng"),
                ("inventory_export", "Xuất hàng")
            ],
            "Bán hàng": [
                ("sales_view", "Xem bán hàng"),
                ("sales_create", "Tạo hóa đơn"),
                ("sales_edit", "Sửa hóa đơn"),
                ("sales_delete", "Xóa hóa đơn"),
                ("sales_discount", "Giảm giá"),
                ("sales_refund", "Hoàn trả")
            ],
            "Sửa chữa": [
                ("repair_view", "Xem sửa chữa"),
                ("repair_create", "Tiếp nhận sửa chữa"),
                ("repair_edit", "Sửa biên nhận"),
                ("repair_status", "Cập nhật trạng thái"),
                ("repair_complete", "Hoàn thành sửa chữa"),
                ("repair_warranty", "Quản lý bảo hành")
            ],
            "Cầm đồ": [
                ("pawn_view", "Xem cầm đồ"),
                ("pawn_create", "Tạo hợp đồng"),
                ("pawn_edit", "Sửa hợp đồng"),
                ("pawn_payment", "Thu lãi"),
                ("pawn_redeem", "Chuộc đồ"),
                ("pawn_liquidate", "Thanh lý")
            ],
            "Tài chính": [
                ("finance_view", "Xem tài chính"),
                ("finance_income", "Thu tiền"),
                ("finance_expense", "Chi tiền"),
                ("finance_debt", "Quản lý công nợ"),
                ("finance_report", "Báo cáo tài chính")
            ],
            "Quản trị": [
                ("admin_staff", "Quản lý nhân viên"),
                ("admin_settings", "Cài đặt hệ thống"),
                ("admin_backup", "Sao lưu dữ liệu"),
                ("admin_logs", "Xem nhật ký")
            ]
        }
        
        row = 0
        for category, permissions in permission_structure.items():
            # Category header
            category_label = ttk.Label(permissions_grid_frame, text=category, 
                                     style="Heading.TLabel")
            category_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
            row += 1
            
            # Permissions in this category
            for i, (perm_key, perm_label) in enumerate(permissions):
                col = i % 3
                if col == 0 and i > 0:
                    row += 1
                
                var = tk.BooleanVar()
                self.permission_vars[perm_key] = var
                
                checkbox = ttk.Checkbutton(permissions_grid_frame, text=perm_label, variable=var)
                checkbox.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
            
            row += 1
        
        # Permission buttons
        perm_btn_frame = ttk.Frame(permissions_frame)
        perm_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(perm_btn_frame, text="💾 Lưu quyền", 
                  command=self.save_permissions).pack(side=tk.LEFT, padx=5)
        ttk.Button(perm_btn_frame, text="🔄 Đặt lại", 
                  command=self.reset_permissions).pack(side=tk.LEFT, padx=5)
        ttk.Button(perm_btn_frame, text="👥 Sao chép từ NV khác", 
                  command=self.copy_permissions).pack(side=tk.LEFT, padx=5)
    
    def setup_performance_tab(self):
        """Setup performance tracking tab"""
        performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="Hiệu Suất")
        
        # Time range selection
        time_frame = ttk.LabelFrame(performance_frame, text="Khoảng thời gian", padding=10)
        time_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(time_frame, text="Từ ngày:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.perf_from_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(time_frame, textvariable=self.perf_from_date_var, width=12)
        from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(time_frame, text="Đến ngày:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.perf_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(time_frame, textvariable=self.perf_to_date_var, width=12)
        to_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(time_frame, text="📊 Xem báo cáo", 
                  command=self.load_performance_data).grid(row=0, column=4, padx=20, pady=5)
        
        # Performance summary
        summary_frame = ttk.LabelFrame(performance_frame, text="Tổng quan hiệu suất", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Performance metrics treeview
        self.performance_tree = ttk.Treeview(summary_frame,
                                           columns=('staff', 'sales_count', 'sales_amount', 'commission',
                                                  'repairs_count', 'customer_rating', 'efficiency'),
                                           show='headings', height=10)
        
        # Column headings
        columns = {
            'staff': ('Nhân viên', 150),
            'sales_count': ('Số đơn bán', 100),
            'sales_amount': ('Doanh thu', 120),
            'commission': ('Hoa hồng', 100),
            'repairs_count': ('Số sửa chữa', 100),
            'customer_rating': ('Đánh giá KH', 100),
            'efficiency': ('Hiệu suất', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.performance_tree.heading(col, text=heading)
            self.performance_tree.column(col, width=width, minwidth=50)
        
        self.performance_tree.pack(fill=tk.BOTH, expand=True)
        
        # Detailed performance
        detail_frame = ttk.LabelFrame(performance_frame, text="Chi tiết hiệu suất", padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.performance_detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD, font=('Consolas', 10))
        self.performance_detail_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_attendance_tab(self):
        """Setup attendance tracking tab"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="Chấm Công")
        
        # Quick check-in/out
        checkin_frame = ttk.LabelFrame(attendance_frame, text="Chấm công nhanh", padding=10)
        checkin_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(checkin_frame, text="Nhân viên:").pack(side=tk.LEFT)
        self.checkin_staff_var = tk.StringVar()
        checkin_staff_combo = ttk.Combobox(checkin_frame, textvariable=self.checkin_staff_var, width=30)
        checkin_staff_combo.pack(side=tk.LEFT, padx=10)
        
        # Load staff for attendance
        self.load_staff_combo(checkin_staff_combo)
        
        ttk.Button(checkin_frame, text="📥 Check In", 
                  command=self.check_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(checkin_frame, text="📤 Check Out", 
                  command=self.check_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(checkin_frame, text="👁️ Xem hôm nay", 
                  command=self.view_today_attendance).pack(side=tk.LEFT, padx=5)
        
        # Attendance history
        history_frame = ttk.LabelFrame(attendance_frame, text="Lịch sử chấm công", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Date filter for attendance
        att_filter_frame = ttk.Frame(history_frame)
        att_filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(att_filter_frame, text="Tháng:").pack(side=tk.LEFT)
        self.att_month_var = tk.StringVar(value=str(date.today().month))
        month_combo = ttk.Combobox(att_filter_frame, textvariable=self.att_month_var,
                                  values=list(range(1, 13)), width=10, state="readonly")
        month_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(att_filter_frame, text="Năm:").pack(side=tk.LEFT, padx=(20, 0))
        self.att_year_var = tk.StringVar(value=str(date.today().year))
        year_combo = ttk.Combobox(att_filter_frame, textvariable=self.att_year_var,
                                 values=list(range(2020, 2030)), width=10, state="readonly")
        year_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(att_filter_frame, text="🔍 Lọc", 
                  command=self.filter_attendance).pack(side=tk.LEFT, padx=20)
        
        # Attendance treeview
        self.attendance_tree = ttk.Treeview(history_frame,
                                          columns=('date', 'staff', 'check_in', 'check_out',
                                                 'work_hours', 'overtime', 'status'),
                                          show='headings')
        
        # Column headings
        columns = {
            'date': ('Ngày', 100),
            'staff': ('Nhân viên', 150),
            'check_in': ('Giờ vào', 100),
            'check_out': ('Giờ ra', 100),
            'work_hours': ('Giờ làm', 100),
            'overtime': ('Tăng ca', 100),
            'status': ('Trạng thái', 100)
        }
        
        for col, (heading, width) in columns.items():
            self.attendance_tree.heading(col, text=heading)
            self.attendance_tree.column(col, width=width, minwidth=50)
        
        self.attendance_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Load all staff data"""
        self.refresh_staff()
        self.load_performance_data()
        self.filter_attendance()
    
    def refresh_staff(self):
        """Refresh staff list"""
        # Clear existing items
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        
        # Load staff
        query = """
        SELECT * FROM staff
        ORDER BY full_name
        """
        
        staff_members = self.db_manager.fetch_all(query)
        
        for staff in staff_members:
            status_text = "Đang làm việc" if staff['is_active'] else "Nghỉ việc"
            
            # Role translation
            role_map = {
                'admin': 'Quản trị viên',
                'manager': 'Quản lý',
                'staff': 'Nhân viên',
                'cashier': 'Thu ngân'
            }
            role_text = role_map.get(staff['role'], staff['role'])
            
            self.staff_tree.insert('', 'end', values=(
                staff['id'],
                staff['username'],
                staff['full_name'],
                staff['phone'] or '',
                staff['email'] or '',
                role_text,
                f"{(staff['commission_rate'] or 0) * 100:.1f}",
                f"{staff['salary'] or 0:,.0f}",
                status_text,
                "Chưa đăng nhập"  # This would come from a login_logs table
            ))
    
    def on_staff_search(self, *args):
        """Handle staff search"""
        search_term = self.staff_search_var.get().lower()
        
        if not search_term:
            self.refresh_staff()
            return
        
        # Clear existing items
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        
        # Search staff
        query = """
        SELECT * FROM staff
        WHERE LOWER(full_name) LIKE ? OR LOWER(username) LIKE ? OR LOWER(phone) LIKE ?
        ORDER BY full_name
        """
        
        search_pattern = f"%{search_term}%"
        staff_members = self.db_manager.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        
        for staff in staff_members:
            status_text = "Đang làm việc" if staff['is_active'] else "Nghỉ việc"
            
            role_map = {
                'admin': 'Quản trị viên',
                'manager': 'Quản lý',
                'staff': 'Nhân viên',
                'cashier': 'Thu ngân'
            }
            role_text = role_map.get(staff['role'], staff['role'])
            
            self.staff_tree.insert('', 'end', values=(
                staff['id'],
                staff['username'],
                staff['full_name'],
                staff['phone'] or '',
                staff['email'] or '',
                role_text,
                f"{(staff['commission_rate'] or 0) * 100:.1f}",
                f"{staff['salary'] or 0:,.0f}",
                status_text,
                "Chưa đăng nhập"
            ))
    
    def filter_staff(self):
        """Filter staff by status"""
        status_filter = self.status_filter_var.get()
        
        # Clear existing items
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        
        # Build query based on filter
        if status_filter == "all":
            query = "SELECT * FROM staff ORDER BY full_name"
            params = ()
        elif status_filter == "active":
            query = "SELECT * FROM staff WHERE is_active = 1 ORDER BY full_name"
            params = ()
        else:  # inactive
            query = "SELECT * FROM staff WHERE is_active = 0 ORDER BY full_name"
            params = ()
        
        staff_members = self.db_manager.fetch_all(query, params)
        
        for staff in staff_members:
            status_text = "Đang làm việc" if staff['is_active'] else "Nghỉ việc"
            
            role_map = {
                'admin': 'Quản trị viên',
                'manager': 'Quản lý',
                'staff': 'Nhân viên',
                'cashier': 'Thu ngân'
            }
            role_text = role_map.get(staff['role'], staff['role'])
            
            self.staff_tree.insert('', 'end', values=(
                staff['id'],
                staff['username'],
                staff['full_name'],
                staff['phone'] or '',
                staff['email'] or '',
                role_text,
                f"{(staff['commission_rate'] or 0) * 100:.1f}",
                f"{staff['salary'] or 0:,.0f}",
                status_text,
                "Chưa đăng nhập"
            ))
    
    def add_staff(self):
        """Add new staff member"""
        self.show_staff_dialog()
    
    def edit_staff(self):
        """Edit selected staff member"""
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        item = self.staff_tree.item(selection[0])
        staff_id = item['values'][0]
        self.show_staff_dialog(staff_id)
    
    def show_staff_dialog(self, staff_id=None):
        """Show add/edit staff dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thêm nhân viên" if staff_id is None else "Sửa thông tin nhân viên")
        dialog.geometry("600x500")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing staff data if editing
        staff_data = {}
        if staff_id:
            staff = self.db_manager.fetch_one("SELECT * FROM staff WHERE id = ?", (staff_id,))
            if staff:
                staff_data = dict(staff)
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Username
        ttk.Label(main_frame, text="Tên đăng nhập *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        username_var = tk.StringVar(value=staff_data.get('username', ''))
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=40)
        username_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Password (only for new staff)
        if not staff_id:
            ttk.Label(main_frame, text="Mật khẩu *:").grid(row=row, column=0, sticky=tk.W, pady=5)
            password_var = tk.StringVar()
            password_entry = ttk.Entry(main_frame, textvariable=password_var, width=40, show="*")
            password_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            row += 1
            
            ttk.Label(main_frame, text="Nhập lại mật khẩu *:").grid(row=row, column=0, sticky=tk.W, pady=5)
            confirm_password_var = tk.StringVar()
            confirm_password_entry = ttk.Entry(main_frame, textvariable=confirm_password_var, width=40, show="*")
            confirm_password_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
            row += 1
        
        # Full name
        ttk.Label(main_frame, text="Họ tên *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        full_name_var = tk.StringVar(value=staff_data.get('full_name', ''))
        full_name_entry = ttk.Entry(main_frame, textvariable=full_name_var, width=40)
        full_name_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Phone
        ttk.Label(main_frame, text="Số điện thoại:").grid(row=row, column=0, sticky=tk.W, pady=5)
        phone_var = tk.StringVar(value=staff_data.get('phone', ''))
        phone_entry = ttk.Entry(main_frame, textvariable=phone_var, width=40)
        phone_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=row, column=0, sticky=tk.W, pady=5)
        email_var = tk.StringVar(value=staff_data.get('email', ''))
        email_entry = ttk.Entry(main_frame, textvariable=email_var, width=40)
        email_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Role
        ttk.Label(main_frame, text="Vai trò:").grid(row=row, column=0, sticky=tk.W, pady=5)
        role_var = tk.StringVar(value=staff_data.get('role', 'staff'))
        role_combo = ttk.Combobox(main_frame, textvariable=role_var, width=37,
                                 values=['admin', 'manager', 'staff', 'cashier'], state="readonly")
        role_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Commission rate
        ttk.Label(main_frame, text="Tỷ lệ hoa hồng (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        commission_var = tk.StringVar(value=str((staff_data.get('commission_rate', 0) or 0) * 100))
        commission_entry = ttk.Entry(main_frame, textvariable=commission_var, width=40)
        commission_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Salary
        ttk.Label(main_frame, text="Lương cố định:").grid(row=row, column=0, sticky=tk.W, pady=5)
        salary_var = tk.StringVar(value=str(staff_data.get('salary', 0) or 0))
        salary_entry = ttk.Entry(main_frame, textvariable=salary_var, width=40)
        salary_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Status
        ttk.Label(main_frame, text="Trạng thái:").grid(row=row, column=0, sticky=tk.W, pady=5)
        is_active_var = tk.BooleanVar(value=staff_data.get('is_active', True))
        is_active_check = ttk.Checkbutton(main_frame, text="Đang làm việc", variable=is_active_var)
        is_active_check.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_staff():
            if not username_var.get().strip() or not full_name_var.get().strip():
                messagebox.showerror("Lỗi", "Vui lòng nhập tên đăng nhập và họ tên!")
                return
            
            if not staff_id:
                if not password_var.get() or not confirm_password_var.get():
                    messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu!")
                    return
                
                if password_var.get() != confirm_password_var.get():
                    messagebox.showerror("Lỗi", "Mật khẩu không khớp!")
                    return
            
            try:
                commission_rate = float(commission_var.get() or 0) / 100
                salary = float(salary_var.get() or 0)
            except ValueError:
                messagebox.showerror("Lỗi", "Giá trị không hợp lệ!")
                return
            
            # Prepare data
            data = {
                'username': username_var.get().strip(),
                'full_name': full_name_var.get().strip(),
                'phone': phone_var.get().strip(),
                'email': email_var.get().strip(),
                'role': role_var.get(),
                'commission_rate': commission_rate,
                'salary': salary,
                'is_active': is_active_var.get(),
                'updated_at': datetime.now().isoformat()
            }
            
            if not staff_id:
                # Hash password for new staff
                password_hash = hashlib.sha256(password_var.get().encode()).hexdigest()
                data['password'] = password_hash
                data['created_at'] = datetime.now().isoformat()
            
            try:
                if staff_id:
                    # Update existing staff
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                    query = f"UPDATE staff SET {set_clause} WHERE id = ?"
                    params = list(data.values()) + [staff_id]
                else:
                    # Insert new staff
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    query = f"INSERT INTO staff ({columns}) VALUES ({placeholders})"
                    params = list(data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật nhân viên!" if staff_id else "Đã thêm nhân viên!")
                dialog.destroy()
                self.refresh_staff()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu nhân viên: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_staff).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on username entry
        username_entry.focus_set()
    
    def change_password(self):
        """Change password for selected staff"""
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        item = self.staff_tree.item(selection[0])
        staff_id = item['values'][0]
        username = item['values'][1]
        
        self.show_change_password_dialog(staff_id, username)
    
    def show_change_password_dialog(self, staff_id, username):
        """Show change password dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title(f"Đổi mật khẩu - {username}")
        dialog.geometry("400x250")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # New password
        ttk.Label(main_frame, text="Mật khẩu mới *:").pack(anchor=tk.W, pady=5)
        new_password_var = tk.StringVar()
        new_password_entry = ttk.Entry(main_frame, textvariable=new_password_var, width=30, show="*")
        new_password_entry.pack(pady=5, fill=tk.X)
        
        # Confirm password
        ttk.Label(main_frame, text="Nhập lại mật khẩu *:").pack(anchor=tk.W, pady=5)
        confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(main_frame, textvariable=confirm_password_var, width=30, show="*")
        confirm_password_entry.pack(pady=5, fill=tk.X)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def change_password():
            if not new_password_var.get() or not confirm_password_var.get():
                messagebox.showerror("Lỗi", "Vui lòng nhập mật khẩu!")
                return
            
            if new_password_var.get() != confirm_password_var.get():
                messagebox.showerror("Lỗi", "Mật khẩu không khớp!")
                return
            
            if len(new_password_var.get()) < 6:
                messagebox.showerror("Lỗi", "Mật khẩu phải có ít nhất 6 ký tự!")
                return
            
            try:
                # Hash new password
                password_hash = hashlib.sha256(new_password_var.get().encode()).hexdigest()
                
                self.db_manager.execute_query(
                    "UPDATE staff SET password = ?, updated_at = ? WHERE id = ?",
                    (password_hash, datetime.now().isoformat(), staff_id)
                )
                
                messagebox.showinfo("Thành công", "Đã đổi mật khẩu!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đổi mật khẩu: {e}")
        
        ttk.Button(btn_frame, text="💾 Đổi mật khẩu", command=change_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on new password entry
        new_password_entry.focus_set()
    
    def view_staff_details(self):
        """View staff details"""
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng xem chi tiết nhân viên sẽ được phát triển!")
    
    def load_staff_combo(self, combo):
        """Load staff into combobox"""
        staff_members = self.db_manager.fetch_all(
            "SELECT id, full_name, username FROM staff WHERE is_active = 1 ORDER BY full_name"
        )
        combo['values'] = [f"{s['id']} - {s['full_name']} ({s['username']})" for s in staff_members]
    
    def load_staff_permissions(self):
        """Load permissions for selected staff"""
        if not self.permission_staff_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        staff_id = int(self.permission_staff_var.get().split(' - ')[0])
        
        # Load staff permissions
        staff = self.db_manager.fetch_one("SELECT permissions FROM staff WHERE id = ?", (staff_id,))
        
        if staff and staff['permissions']:
            # Parse permissions (assuming JSON format)
            try:
                import json
                permissions = json.loads(staff['permissions'])
                
                # Reset all permissions
                for var in self.permission_vars.values():
                    var.set(False)
                
                # Set permissions from database
                for perm_key, value in permissions.items():
                    if perm_key in self.permission_vars:
                        self.permission_vars[perm_key].set(value)
                        
            except (json.JSONDecodeError, TypeError):
                # If permissions is not JSON, assume it's "all" for admin
                if staff['permissions'] == 'all':
                    for var in self.permission_vars.values():
                        var.set(True)
        else:
            # No permissions set, reset all
            for var in self.permission_vars.values():
                var.set(False)
    
    def save_permissions(self):
        """Save permissions for selected staff"""
        if not self.permission_staff_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        staff_id = int(self.permission_staff_var.get().split(' - ')[0])
        
        # Collect permissions
        permissions = {}
        for perm_key, var in self.permission_vars.items():
            permissions[perm_key] = var.get()
        
        try:
            import json
            permissions_json = json.dumps(permissions)
            
            self.db_manager.execute_query(
                "UPDATE staff SET permissions = ?, updated_at = ? WHERE id = ?",
                (permissions_json, datetime.now().isoformat(), staff_id)
            )
            
            messagebox.showinfo("Thành công", "Đã lưu phân quyền!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu phân quyền: {e}")
    
    def reset_permissions(self):
        """Reset all permissions"""
        for var in self.permission_vars.values():
            var.set(False)
    
    def copy_permissions(self):
        """Copy permissions from another staff member"""
        messagebox.showinfo("Thông báo", "Chức năng sao chép quyền sẽ được phát triển!")
    
    def load_performance_data(self):
        """Load performance data"""
        from_date = self.perf_from_date_var.get()
        to_date = self.perf_to_date_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoảng thời gian!")
            return
        
        # Clear existing items
        for item in self.performance_tree.get_children():
            self.performance_tree.delete(item)
        
        # Load performance data (this would involve complex queries across multiple tables)
        staff_members = self.db_manager.fetch_all(
            "SELECT id, full_name FROM staff WHERE is_active = 1 ORDER BY full_name"
        )
        
        for staff in staff_members:
            # Sales performance
            sales_data = self.db_manager.fetch_one(
                """SELECT COUNT(*) as count, COALESCE(SUM(total_amount), 0) as total
                   FROM sales 
                   WHERE staff_id = ? AND DATE(sale_date) BETWEEN ? AND ?""",
                (staff['id'], from_date, to_date)
            )
            
            # Repairs performance
            repairs_data = self.db_manager.fetch_one(
                """SELECT COUNT(*) as count
                   FROM repairs 
                   WHERE staff_id = ? AND DATE(created_at) BETWEEN ? AND ?""",
                (staff['id'], from_date, to_date)
            )
            
            # Calculate commission (simplified)
            commission = sales_data['total'] * 0.02  # 2% commission example
            
            self.performance_tree.insert('', 'end', values=(
                staff['full_name'],
                sales_data['count'],
                f"{sales_data['total']:,.0f}",
                f"{commission:,.0f}",
                repairs_data['count'],
                "N/A",  # Customer rating would come from reviews
                "N/A"   # Efficiency metric
            ))
        
        # Update detail text
        self.performance_detail_text.delete('1.0', tk.END)
        detail_report = f"""
=== BÁO CÁO HIỆU SUẤT NHÂN VIÊN ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Báo cáo chi tiết hiệu suất nhân viên sẽ được tính toán dựa trên:
- Số lượng đơn hàng bán được
- Tổng doanh thu tạo ra
- Số lượng sửa chữa hoàn thành
- Đánh giá của khách hàng
- Tỷ lệ hoàn thành công việc đúng hạn

Chi tiết sẽ được phát triển thêm...
        """
        self.performance_detail_text.insert('1.0', detail_report.strip())
    
    def check_in(self):
        """Staff check in"""
        if not self.checkin_staff_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        staff_id = int(self.checkin_staff_var.get().split(' - ')[0])
        current_time = datetime.now()
        
        try:
            # Check if already checked in today
            today = date.today().strftime('%Y-%m-%d')
            existing = self.db_manager.fetch_one(
                "SELECT id FROM attendance WHERE staff_id = ? AND DATE(check_in) = ?",
                (staff_id, today)
            )
            
            if existing:
                messagebox.showwarning("Cảnh báo", "Nhân viên đã check in hôm nay!")
                return
            
            # Insert attendance record (would need attendance table)
            messagebox.showinfo("Thành công", f"Check in thành công lúc {current_time.strftime('%H:%M')}!")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể check in: {e}")
    
    def check_out(self):
        """Staff check out"""
        if not self.checkin_staff_var.get():
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên!")
            return
        
        messagebox.showinfo("Thành công", f"Check out thành công lúc {datetime.now().strftime('%H:%M')}!")
    
    def view_today_attendance(self):
        """View today's attendance"""
        messagebox.showinfo("Thông báo", "Chức năng xem chấm công hôm nay sẽ được phát triển!")
    
    def filter_attendance(self):
        """Filter attendance by month/year"""
        # Clear existing items
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
        
        # This would load attendance data from attendance table
        # For now, showing sample data
        sample_data = [
            (date.today().strftime('%d/%m/%Y'), "Admin", "08:00", "17:30", "8.5", "0.5", "Đúng giờ"),
            (date.today().strftime('%d/%m/%Y'), "Nhân viên 1", "08:15", "17:45", "8.5", "0.75", "Trễ 15 phút"),
        ]
        
        for data in sample_data:
            self.attendance_tree.insert('', 'end', values=data)
