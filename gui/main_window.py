#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from gui.inventory_tab import InventoryTab
from gui.sales_tab import SalesTab
from gui.repair_tab import RepairTab
from gui.warranty_tab import WarrantyTab
from gui.pawn_tab import PawnTab
from gui.financial_tab import FinancialTab
from gui.staff_tab import StaffTab
from gui.reports_tab import ReportsTab
from config import APP_CONFIG, GUI_CONFIG

class MainWindow:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.current_user = None
        
        # Login first
        if not self.show_login():
            self.root.quit()
            return
        
        self.setup_main_interface()
    
    def show_login(self):
        """Show login dialog"""
        login_window = tk.Toplevel(self.root)
        login_window.title("Đăng nhập - ChViet")
        login_window.geometry("400x300")
        login_window.transient(self.root)
        login_window.grab_set()
        
        # Center the login window
        login_window.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() // 2 - 200,
            self.root.winfo_screenheight() // 2 - 150
        ))
        
        # Login form
        main_frame = ttk.Frame(login_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="ChViet - Quản Lý Cửa Hàng", 
                               style="Heading.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Username
        ttk.Label(main_frame, text="Tên đăng nhập:").pack(anchor=tk.W)
        username_entry = ttk.Entry(main_frame, width=30)
        username_entry.pack(pady=(5, 10), fill=tk.X)
        username_entry.insert(0, "admin")  # Default for testing
        
        # Password
        ttk.Label(main_frame, text="Mật khẩu:").pack(anchor=tk.W)
        password_entry = ttk.Entry(main_frame, width=30, show="*")
        password_entry.pack(pady=(5, 10), fill=tk.X)
        password_entry.insert(0, "admin123")  # Default for testing
        
        # Login result
        result_var = tk.BooleanVar()
        
        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return
            
            # Check credentials
            user = self.db_manager.fetch_one(
                "SELECT * FROM staff WHERE username = ? AND password = ? AND is_active = 1",
                (username, password)
            )
            
            if user:
                self.current_user = dict(user)
                result_var.set(True)
                login_window.destroy()
            else:
                messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
        
        def on_enter(event):
            do_login()
        
        # Bind Enter key
        username_entry.bind('<Return>', on_enter)
        password_entry.bind('<Return>', on_enter)
        
        # Login button
        login_btn = ttk.Button(main_frame, text="Đăng nhập", command=do_login)
        login_btn.pack(pady=(20, 10))
        
        # Focus on username entry
        username_entry.focus_set()
        
        # Wait for login window to close
        login_window.wait_window()
        
        return result_var.get()
    
    def setup_main_interface(self):
        """Setup the main application interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Header
        self.create_header(main_container)
        
        # Main content with notebook tabs
        self.create_notebook(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_header(self, parent):
        """Create application header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="ChViet - Quản Lý Cửa Hàng Điện Thoại", 
                               style="Heading.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # User info
        user_info = ttk.Label(header_frame, 
                             text=f"Xin chào: {self.current_user['full_name']} | "
                                  f"Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        user_info.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5, 0))
    
    def create_notebook(self, parent):
        """Create main notebook with tabs"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Initialize tabs
        self.tabs = {}
        
        # Inventory tab
        self.tabs['inventory'] = InventoryTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['inventory'].frame, text="📦 Kho Hàng")
        
        # Sales tab
        self.tabs['sales'] = SalesTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['sales'].frame, text="💰 Bán Hàng")
        
        # Repair tab
        self.tabs['repair'] = RepairTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['repair'].frame, text="🔧 Sửa Chữa")
        
        # Warranty tab
        self.tabs['warranty'] = WarrantyTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['warranty'].frame, text="🛡️ Bảo Hành")
        
        # Pawn tab
        self.tabs['pawn'] = PawnTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['pawn'].frame, text="💎 Cầm Đồ")
        
        # Financial tab
        self.tabs['financial'] = FinancialTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['financial'].frame, text="💼 Tài Chính")
        
        # Staff tab (admin only)
        if self.current_user['role'] == 'admin':
            self.tabs['staff'] = StaffTab(self.notebook, self.db_manager, self.current_user)
            self.notebook.add(self.tabs['staff'].frame, text="👥 Nhân Viên")
        
        # Reports tab
        self.tabs['reports'] = ReportsTab(self.notebook, self.db_manager, self.current_user)
        self.notebook.add(self.tabs['reports'].frame, text="📊 Báo Cáo")
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_bar = ttk.Frame(parent)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(10, 5))
        
        self.status_label = ttk.Label(self.status_bar, text="Sẵn sàng")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Clock
        self.clock_label = ttk.Label(self.status_bar, text="")
        self.clock_label.pack(side=tk.RIGHT, padx=5)
        
        self.update_clock()
    
    def update_clock(self):
        """Update clock in status bar"""
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)
    
    def set_status(self, message):
        """Set status bar message"""
        self.status_label.config(text=message)
        self.root.after(3000, lambda: self.status_label.config(text="Sẵn sàng"))
