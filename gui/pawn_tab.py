#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pawn shop management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import uuid

from models import PawnContract, Customer
from config import BUSINESS_RULES

class PawnTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup pawn tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # New Contract tab
        self.setup_new_contract_tab()
        
        # Contract List tab
        self.setup_contract_list_tab()
        
        # Payments tab
        self.setup_payments_tab()
        
        # Reports tab
        self.setup_reports_tab()
    
    def setup_new_contract_tab(self):
        """Setup new pawn contract tab"""
        new_contract_frame = ttk.Frame(self.notebook)
        self.notebook.add(new_contract_frame, text="Hợp Đồng Mới")
        
        # Main form
        form_frame = ttk.LabelFrame(new_contract_frame, text="Thông tin hợp đồng cầm đồ", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create form in two columns
        left_frame = ttk.Frame(form_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        right_frame = ttk.Frame(form_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left column - Basic info
        row = 0
        
        # Contract number
        ttk.Label(left_frame, text="Số hợp đồng:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.contract_number_var = tk.StringVar()
        contract_number_entry = ttk.Entry(left_frame, textvariable=self.contract_number_var, width=25, state="readonly")
        contract_number_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(left_frame, text="Tạo mã", 
                  command=self.generate_contract_number).grid(row=row, column=2, pady=5, padx=(5, 0))
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
        
        # Item description
        ttk.Label(left_frame, text="Mô tả tài sản *:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.item_description_text = tk.Text(left_frame, width=40, height=4)
        self.item_description_text.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Item value
        ttk.Label(left_frame, text="Giá trị tài sản *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.item_value_var = tk.StringVar()
        item_value_entry = ttk.Entry(left_frame, textvariable=self.item_value_var, width=25)
        item_value_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        item_value_entry.bind('<KeyRelease>', self.calculate_loan_amount)
        row += 1
        
        # Loan amount
        ttk.Label(left_frame, text="Số tiền cho vay *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.loan_amount_var = tk.StringVar()
        loan_amount_entry = ttk.Entry(left_frame, textvariable=self.loan_amount_var, width=25)
        loan_amount_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        loan_amount_entry.bind('<KeyRelease>', self.calculate_interest)
        row += 1
        
        # Interest rate
        ttk.Label(left_frame, text="Lãi suất (%/tháng):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.interest_rate_var = tk.StringVar(value=str(BUSINESS_RULES['PAWN_INTEREST_RATE'] * 100))
        interest_rate_entry = ttk.Entry(left_frame, textvariable=self.interest_rate_var, width=25)
        interest_rate_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        interest_rate_entry.bind('<KeyRelease>', self.calculate_interest)
        row += 1
        
        # Right column - Dates and calculations
        row = 0
        
        # Contract date
        ttk.Label(right_frame, text="Ngày hợp đồng:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.contract_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        contract_date_entry = ttk.Entry(right_frame, textvariable=self.contract_date_var, width=20)
        contract_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Due date
        ttk.Label(right_frame, text="Ngày đáo hạn:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.due_date_var = tk.StringVar()
        due_date_entry = ttk.Entry(right_frame, textvariable=self.due_date_var, width=20)
        due_date_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Button(right_frame, text="30 ngày", 
                  command=self.set_due_date).grid(row=row, column=2, pady=5, padx=(5, 0))
        row += 1
        
        # Monthly interest
        ttk.Label(right_frame, text="Lãi hàng tháng:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.monthly_interest_label = ttk.Label(right_frame, text="0 VNĐ", 
                                               style="Success.TLabel", font=('Arial', 10, 'bold'))
        self.monthly_interest_label.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Total to pay (if paid on time)
        ttk.Label(right_frame, text="Tổng trả (30 ngày):", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        self.total_payment_label = ttk.Label(right_frame, text="0 VNĐ", 
                                            style="Warning.TLabel", font=('Arial', 10, 'bold'))
        self.total_payment_label.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(right_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(right_frame, width=30, height=6)
        self.notes_text.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(btn_frame, text="💾 Lưu hợp đồng", 
                  command=self.save_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In hợp đồng", 
                  command=self.print_contract).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa form", 
                  command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Generate initial contract number and set due date
        self.generate_contract_number()
        self.set_due_date()
    
    def setup_contract_list_tab(self):
        """Setup contract list tab"""
        contract_list_frame = ttk.Frame(self.notebook)
        self.notebook.add(contract_list_frame, text="Danh Sách Hợp Đồng")
        
        # Top controls
        top_frame = ttk.Frame(contract_list_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Search frame
        search_frame = ttk.LabelFrame(top_frame, text="Tìm kiếm", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Label(search_frame, text="Số HĐ / Khách hàng:").pack(anchor=tk.W)
        self.contract_search_var = tk.StringVar()
        self.contract_search_var.trace('w', self.on_contract_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.contract_search_var, width=40)
        search_entry.pack(pady=5, fill=tk.X)
        
        # Status filter
        status_frame = ttk.LabelFrame(top_frame, text="Lọc trạng thái", padding=10)
        status_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_filter_var = tk.StringVar(value="all")
        status_values = [
            ("all", "Tất cả"),
            ("active", "Đang hiệu lực"),
            ("overdue", "Quá hạn"),
            ("redeemed", "Đã chuộc"),
            ("liquidated", "Đã thanh lý"),
            ("extended", "Đã gia hạn")
        ]
        
        for value, text in status_values:
            ttk.Radiobutton(status_frame, text=text, variable=self.status_filter_var,
                           value=value, command=self.filter_contracts).pack(anchor=tk.W)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="👁️ Xem chi tiết", 
                  command=self.view_contract_details).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="💰 Thu lãi", 
                  command=self.collect_interest).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Gia hạn", 
                  command=self.extend_contract).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="✅ Chuộc đồ", 
                  command=self.redeem_item).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="💸 Thanh lý", 
                  command=self.liquidate_item).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🖨️ In HĐ", 
                  command=self.print_selected_contract).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_contracts).pack(pady=2, fill=tk.X)
        
        # Contracts treeview
        tree_frame = ttk.Frame(contract_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.contracts_tree = ttk.Treeview(tree_frame,
                                          columns=('id', 'contract_number', 'date', 'customer', 'item',
                                                 'item_value', 'loan_amount', 'due_date', 'status', 'overdue_days'),
                                          show='headings',
                                          yscrollcommand=v_scrollbar.set,
                                          xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.contracts_tree.yview)
        h_scrollbar.config(command=self.contracts_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'contract_number': ('Số HĐ', 120),
            'date': ('Ngày tạo', 100),
            'customer': ('Khách hàng', 150),
            'item': ('Tài sản', 200),
            'item_value': ('Giá trị TS', 100),
            'loan_amount': ('Tiền vay', 100),
            'due_date': ('Đáo hạn', 100),
            'status': ('Trạng thái', 100),
            'overdue_days': ('Quá hạn', 80)
        }
        
        for col, (heading, width) in columns.items():
            self.contracts_tree.heading(col, text=heading)
            self.contracts_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.contracts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.contracts_tree.bind('<Double-1>', lambda e: self.view_contract_details())
    
    def setup_payments_tab(self):
        """Setup payments management tab"""
        payments_frame = ttk.Frame(self.notebook)
        self.notebook.add(payments_frame, text="Thanh Toán")
        
        # Payment form
        payment_form = ttk.LabelFrame(payments_frame, text="Thu lãi / Thanh toán", padding=20)
        payment_form.pack(fill=tk.X, padx=10, pady=10)
        
        # Contract lookup
        ttk.Label(payment_form, text="Số hợp đồng:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.payment_contract_var = tk.StringVar()
        payment_contract_combo = ttk.Combobox(payment_form, textvariable=self.payment_contract_var, width=30)
        payment_contract_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Load active contracts
        self.load_active_contracts_combo(payment_contract_combo)
        
        ttk.Button(payment_form, text="🔍 Tìm", 
                  command=self.load_contract_for_payment).grid(row=0, column=2, pady=5, padx=(5, 0))
        
        # Contract info display
        self.contract_info_frame = ttk.LabelFrame(payments_frame, text="Thông tin hợp đồng", padding=10)
        # Initially hidden
        
        # Payment amount
        ttk.Label(payment_form, text="Số tiền thanh toán:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.payment_amount_var = tk.StringVar()
        payment_amount_entry = ttk.Entry(payment_form, textvariable=self.payment_amount_var, width=20)
        payment_amount_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Payment type
        ttk.Label(payment_form, text="Loại thanh toán:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.payment_type_var = tk.StringVar(value="interest")
        payment_type_combo = ttk.Combobox(payment_form, textvariable=self.payment_type_var, width=27,
                                         values=["interest", "partial_redemption", "full_redemption"],
                                         state="readonly")
        payment_type_combo.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Payment buttons
        btn_frame = ttk.Frame(payment_form)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        ttk.Button(btn_frame, text="💰 Thu tiền", 
                  command=self.process_payment).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In biên lai", 
                  command=self.print_receipt).pack(side=tk.LEFT, padx=5)
        
        # Payment history
        history_frame = ttk.LabelFrame(payments_frame, text="Lịch sử thanh toán", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.payments_tree = ttk.Treeview(history_frame,
                                         columns=('date', 'contract', 'customer', 'amount', 'type', 'staff'),
                                         show='headings')
        
        # Column headings
        columns = {
            'date': ('Ngày', 120),
            'contract': ('Số HĐ', 120),
            'customer': ('Khách hàng', 150),
            'amount': ('Số tiền', 100),
            'type': ('Loại', 120),
            'staff': ('Thu ngân', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.payments_tree.heading(col, text=heading)
            self.payments_tree.column(col, width=width, minwidth=50)
        
        self.payments_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_reports_tab(self):
        """Setup pawn reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Báo Cáo")
        
        # Report filters
        filter_frame = ttk.LabelFrame(reports_frame, text="Bộ lọc báo cáo", padding=20)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range
        ttk.Label(filter_frame, text="Từ ngày:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.report_from_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(filter_frame, textvariable=self.report_from_date_var, width=12)
        from_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Đến ngày:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.report_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(filter_frame, textvariable=self.report_to_date_var, width=12)
        to_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Report buttons
        btn_frame = ttk.Frame(filter_frame)
        btn_frame.grid(row=1, column=0, columnspan=4, pady=20)
        
        ttk.Button(btn_frame, text="📊 Báo cáo tổng hợp", 
                  command=self.generate_summary_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💰 Báo cáo thu chi", 
                  command=self.generate_revenue_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚠️ HĐ quá hạn", 
                  command=self.generate_overdue_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_to_excel).pack(side=tk.LEFT, padx=5)
        
        # Report display
        self.report_text = tk.Text(reports_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar for report
        report_scrollbar = ttk.Scrollbar(reports_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.config(yscrollcommand=report_scrollbar.set)
    
    def load_data(self):
        """Load all data"""
        self.refresh_contracts()
        self.load_payment_history()
    
    def load_customers_combo(self, combo):
        """Load customers into combobox"""
        customers = self.db_manager.fetch_all("SELECT id, name, phone FROM customers ORDER BY name")
        combo['values'] = [""] + [f"{c['id']} - {c['name']} ({c['phone']})" for c in customers if c['phone']]
    
    def load_active_contracts_combo(self, combo):
        """Load active contracts into combobox"""
        contracts = self.db_manager.fetch_all(
            """SELECT pc.contract_number, c.name as customer_name
               FROM pawn_contracts pc
               JOIN customers c ON pc.customer_id = c.id
               WHERE pc.status = 'active'
               ORDER BY pc.created_at DESC"""
        )
        combo['values'] = [f"{c['contract_number']} - {c['customer_name']}" for c in contracts]
    
    def generate_contract_number(self):
        """Generate unique contract number"""
        contract_number = f"CD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.contract_number_var.set(contract_number)
    
    def set_due_date(self):
        """Set due date to 30 days from contract date"""
        try:
            contract_date_str = self.contract_date_var.get()
            contract_date = datetime.strptime(contract_date_str, '%Y-%m-%d').date()
            due_date = contract_date + timedelta(days=30)
            self.due_date_var.set(due_date.strftime('%Y-%m-%d'))
        except:
            pass
    
    def calculate_loan_amount(self, event=None):
        """Calculate suggested loan amount (typically 70-80% of item value)"""
        try:
            item_value = float(self.item_value_var.get() or 0)
            suggested_loan = item_value * 0.75  # 75% of item value
            self.loan_amount_var.set(f"{suggested_loan:.0f}")
            self.calculate_interest()
        except ValueError:
            pass
    
    def calculate_interest(self, event=None):
        """Calculate monthly interest and total payment"""
        try:
            loan_amount = float(self.loan_amount_var.get() or 0)
            interest_rate = float(self.interest_rate_var.get() or 0) / 100
            
            monthly_interest = loan_amount * interest_rate
            total_payment = loan_amount + monthly_interest
            
            self.monthly_interest_label.config(text=f"{monthly_interest:,.0f} VNĐ")
            self.total_payment_label.config(text=f"{total_payment:,.0f} VNĐ")
        except ValueError:
            self.monthly_interest_label.config(text="0 VNĐ")
            self.total_payment_label.config(text="0 VNĐ")
    
    def add_customer(self):
        """Add new customer"""
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
        
        # ID Number
        ttk.Label(main_frame, text="CMND/CCCD:").grid(row=row, column=0, sticky=tk.W, pady=5)
        id_number_var = tk.StringVar()
        id_number_entry = ttk.Entry(main_frame, textvariable=id_number_var, width=40)
        id_number_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
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
                'id_number': id_number_var.get().strip(),
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
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu khách hàng: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_customer).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on name entry
        name_entry.focus_set()
    
    def save_contract(self):
        """Save pawn contract"""
        # Validate required fields
        if not self.contract_number_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng tạo số hợp đồng!")
            return
        
        if not self.customer_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng!")
            return
        
        if not self.item_description_text.get('1.0', tk.END).strip():
            messagebox.showerror("Lỗi", "Vui lòng mô tả tài sản!")
            return
        
        if not self.item_value_var.get() or not self.loan_amount_var.get():
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị tài sản và số tiền vay!")
            return
        
        try:
            # Get customer ID
            customer_id = int(self.customer_var.get().split(' - ')[0])
            
            # Get values
            item_value = float(self.item_value_var.get())
            loan_amount = float(self.loan_amount_var.get())
            interest_rate = float(self.interest_rate_var.get()) / 100
            
            # Prepare contract data
            contract_data = {
                'contract_number': self.contract_number_var.get().strip(),
                'customer_id': customer_id,
                'staff_id': self.current_user['id'],
                'item_description': self.item_description_text.get('1.0', tk.END).strip(),
                'item_value': item_value,
                'loan_amount': loan_amount,
                'interest_rate': interest_rate,
                'contract_date': self.contract_date_var.get(),
                'due_date': self.due_date_var.get(),
                'status': 'active',
                'total_interest': 0,
                'payments_made': 0,
                'renewal_count': 0,
                'notes': self.notes_text.get('1.0', tk.END).strip(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Insert contract record
            columns = ', '.join(contract_data.keys())
            placeholders = ', '.join(['?' for _ in contract_data])
            query = f"INSERT INTO pawn_contracts ({columns}) VALUES ({placeholders})"
            cursor = self.db_manager.execute_query(query, list(contract_data.values()))
            contract_id = cursor.lastrowid
            
            # Create transaction record for loan disbursement
            transaction_data = {
                'transaction_type': 'expense',
                'amount': loan_amount,
                'description': f'Cho vay cầm đồ - {self.contract_number_var.get()}',
                'reference_id': contract_id,
                'reference_type': 'pawn_loan',
                'payment_method': 'cash',
                'staff_id': self.current_user['id'],
                'transaction_date': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            columns = ', '.join(transaction_data.keys())
            placeholders = ', '.join(['?' for _ in transaction_data])
            query = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
            self.db_manager.execute_query(query, list(transaction_data.values()))
            
            messagebox.showinfo("Thành công", f"Đã tạo hợp đồng cầm đồ {self.contract_number_var.get()}!")
            
            # Ask to print contract
            if messagebox.askyesno("In hợp đồng", "Bạn có muốn in hợp đồng không?"):
                self.print_contract_by_id(contract_id)
            
            # Clear form
            self.clear_form()
            
            # Refresh contracts list
            self.refresh_contracts()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu hợp đồng: {e}")
    
    def print_contract(self):
        """Print contract for current form"""
        contract_number = self.contract_number_var.get()
        if not contract_number:
            messagebox.showwarning("Cảnh báo", "Chưa có số hợp đồng!")
            return
        
        # Find contract by number
        contract = self.db_manager.fetch_one(
            "SELECT id FROM pawn_contracts WHERE contract_number = ?",
            (contract_number,)
        )
        
        if contract:
            self.print_contract_by_id(contract['id'])
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng lưu hợp đồng trước khi in!")
    
    def print_contract_by_id(self, contract_id):
        """Print contract by ID"""
        try:
            from utils.print_utils import print_pawn_contract
            print_pawn_contract(self.db_manager, contract_id)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in hợp đồng: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.generate_contract_number()
        self.customer_var.set("")
        self.item_description_text.delete('1.0', tk.END)
        self.item_value_var.set("")
        self.loan_amount_var.set("")
        self.interest_rate_var.set(str(BUSINESS_RULES['PAWN_INTEREST_RATE'] * 100))
        self.contract_date_var.set(date.today().strftime('%Y-%m-%d'))
        self.set_due_date()
        self.notes_text.delete('1.0', tk.END)
        self.calculate_interest()
    
    def refresh_contracts(self):
        """Refresh contracts list"""
        # Clear existing items
        for item in self.contracts_tree.get_children():
            self.contracts_tree.delete(item)
        
        # Load contracts
        query = """
        SELECT pc.*, c.name as customer_name
        FROM pawn_contracts pc
        LEFT JOIN customers c ON pc.customer_id = c.id
        ORDER BY pc.created_at DESC
        """
        
        contracts = self.db_manager.fetch_all(query)
        
        for contract in contracts:
            contract_date = datetime.fromisoformat(contract['created_at']).strftime('%d/%m/%Y')
            
            # Calculate overdue days
            try:
                due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
                overdue_days = (date.today() - due_date).days
                overdue_text = f"{overdue_days} ngày" if overdue_days > 0 else ""
            except:
                overdue_text = ""
            
            # Status translation
            status_map = {
                'active': 'Đang hiệu lực',
                'overdue': 'Quá hạn',
                'redeemed': 'Đã chuộc',
                'liquidated': 'Đã thanh lý',
                'extended': 'Đã gia hạn'
            }
            
            status_text = status_map.get(contract['status'], contract['status'])
            
            # Update status if overdue
            if contract['status'] == 'active' and overdue_days > 0:
                status_text = "Quá hạn"
            
            self.contracts_tree.insert('', 'end', values=(
                contract['id'],
                contract['contract_number'],
                contract_date,
                contract['customer_name'] or '',
                contract['item_description'][:50] + "..." if len(contract['item_description']) > 50 else contract['item_description'],
                f"{contract['item_value']:,.0f}",
                f"{contract['loan_amount']:,.0f}",
                contract['due_date'],
                status_text,
                overdue_text
            ))
    
    def on_contract_search(self, *args):
        """Handle contract search"""
        search_term = self.contract_search_var.get().lower()
        
        if not search_term:
            self.refresh_contracts()
            return
        
        # Clear existing items
        for item in self.contracts_tree.get_children():
            self.contracts_tree.delete(item)
        
        # Search contracts
        query = """
        SELECT pc.*, c.name as customer_name
        FROM pawn_contracts pc
        LEFT JOIN customers c ON pc.customer_id = c.id
        WHERE LOWER(pc.contract_number) LIKE ? OR
              LOWER(c.name) LIKE ? OR
              LOWER(pc.item_description) LIKE ?
        ORDER BY pc.created_at DESC
        """
        
        search_pattern = f"%{search_term}%"
        contracts = self.db_manager.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        
        for contract in contracts:
            contract_date = datetime.fromisoformat(contract['created_at']).strftime('%d/%m/%Y')
            
            try:
                due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
                overdue_days = (date.today() - due_date).days
                overdue_text = f"{overdue_days} ngày" if overdue_days > 0 else ""
            except:
                overdue_text = ""
            
            status_map = {
                'active': 'Đang hiệu lực',
                'overdue': 'Quá hạn',
                'redeemed': 'Đã chuộc',
                'liquidated': 'Đã thanh lý',
                'extended': 'Đã gia hạn'
            }
            
            status_text = status_map.get(contract['status'], contract['status'])
            
            if contract['status'] == 'active' and overdue_days > 0:
                status_text = "Quá hạn"
            
            self.contracts_tree.insert('', 'end', values=(
                contract['id'],
                contract['contract_number'],
                contract_date,
                contract['customer_name'] or '',
                contract['item_description'][:50] + "..." if len(contract['item_description']) > 50 else contract['item_description'],
                f"{contract['item_value']:,.0f}",
                f"{contract['loan_amount']:,.0f}",
                contract['due_date'],
                status_text,
                overdue_text
            ))
    
    def filter_contracts(self):
        """Filter contracts by status"""
        status_filter = self.status_filter_var.get()
        
        # Clear existing items
        for item in self.contracts_tree.get_children():
            self.contracts_tree.delete(item)
        
        # Build query based on filter
        if status_filter == "all":
            query = """
            SELECT pc.*, c.name as customer_name
            FROM pawn_contracts pc
            LEFT JOIN customers c ON pc.customer_id = c.id
            ORDER BY pc.created_at DESC
            """
            params = ()
        elif status_filter == "overdue":
            query = """
            SELECT pc.*, c.name as customer_name
            FROM pawn_contracts pc
            LEFT JOIN customers c ON pc.customer_id = c.id
            WHERE pc.status = 'active' AND DATE(pc.due_date) < DATE('now')
            ORDER BY pc.created_at DESC
            """
            params = ()
        else:
            query = """
            SELECT pc.*, c.name as customer_name
            FROM pawn_contracts pc
            LEFT JOIN customers c ON pc.customer_id = c.id
            WHERE pc.status = ?
            ORDER BY pc.created_at DESC
            """
            params = (status_filter,)
        
        contracts = self.db_manager.fetch_all(query, params)
        
        for contract in contracts:
            contract_date = datetime.fromisoformat(contract['created_at']).strftime('%d/%m/%Y')
            
            try:
                due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
                overdue_days = (date.today() - due_date).days
                overdue_text = f"{overdue_days} ngày" if overdue_days > 0 else ""
            except:
                overdue_text = ""
            
            status_map = {
                'active': 'Đang hiệu lực',
                'overdue': 'Quá hạn',
                'redeemed': 'Đã chuộc',
                'liquidated': 'Đã thanh lý',
                'extended': 'Đã gia hạn'
            }
            
            status_text = status_map.get(contract['status'], contract['status'])
            
            if contract['status'] == 'active' and overdue_days > 0:
                status_text = "Quá hạn"
            
            self.contracts_tree.insert('', 'end', values=(
                contract['id'],
                contract['contract_number'],
                contract_date,
                contract['customer_name'] or '',
                contract['item_description'][:50] + "..." if len(contract['item_description']) > 50 else contract['item_description'],
                f"{contract['item_value']:,.0f}",
                f"{contract['loan_amount']:,.0f}",
                contract['due_date'],
                status_text,
                overdue_text
            ))
    
    def view_contract_details(self):
        """View contract details"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        item = self.contracts_tree.item(selection[0])
        contract_id = item['values'][0]
        self.show_contract_details_dialog(contract_id)
    
    def show_contract_details_dialog(self, contract_id):
        """Show contract details dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Chi tiết hợp đồng cầm đồ")
        dialog.geometry("800x700")
        dialog.transient(self.frame)
        
        # Load contract data
        contract = self.db_manager.fetch_one(
            """SELECT pc.*, c.name as customer_name, c.phone as customer_phone,
                      c.address as customer_address, c.id_number as customer_id_number,
                      st.full_name as staff_name
               FROM pawn_contracts pc
               LEFT JOIN customers c ON pc.customer_id = c.id
               LEFT JOIN staff st ON pc.staff_id = st.id
               WHERE pc.id = ?""",
            (contract_id,)
        )
        
        if not contract:
            messagebox.showerror("Lỗi", "Không tìm thấy hợp đồng!")
            dialog.destroy()
            return
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Contract info tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="Thông tin hợp đồng")
        
        info_container = ttk.Frame(info_frame, padding=20)
        info_container.pack(fill=tk.BOTH, expand=True)
        
        # Contract information
        contract_info_frame = ttk.LabelFrame(info_container, text="Thông tin hợp đồng", padding=10)
        contract_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Calculate current status
        try:
            due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
            overdue_days = (date.today() - due_date).days
            current_interest = contract['loan_amount'] * contract['interest_rate'] * max(1, overdue_days / 30)
            total_to_pay = contract['loan_amount'] + current_interest
        except:
            overdue_days = 0
            current_interest = 0
            total_to_pay = contract['loan_amount']
        
        info_data = [
            ("Số hợp đồng:", contract['contract_number']),
            ("Ngày tạo:", datetime.fromisoformat(contract['created_at']).strftime('%d/%m/%Y %H:%M')),
            ("Nhân viên:", contract['staff_name'] or ''),
            ("Ngày đáo hạn:", contract['due_date']),
            ("Trạng thái:", contract['status']),
            ("Số ngày quá hạn:", f"{overdue_days} ngày" if overdue_days > 0 else "Chưa quá hạn"),
            ("Lãi suất:", f"{contract['interest_rate'] * 100:.1f}%/tháng"),
            ("Tổng phải trả hiện tại:", f"{total_to_pay:,.0f} VNĐ")
        ]
        
        for i, (label, value) in enumerate(info_data):
            row, col = divmod(i, 2)
            ttk.Label(contract_info_frame, text=label).grid(row=row, column=col*2, sticky=tk.W, padx=5, pady=2)
            ttk.Label(contract_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=row, column=col*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Customer information
        customer_info_frame = ttk.LabelFrame(info_container, text="Thông tin khách hàng", padding=10)
        customer_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        customer_data = [
            ("Tên khách hàng:", contract['customer_name'] or ''),
            ("Số điện thoại:", contract['customer_phone'] or ''),
            ("CMND/CCCD:", contract['customer_id_number'] or ''),
            ("Địa chỉ:", contract['customer_address'] or '')
        ]
        
        for i, (label, value) in enumerate(customer_data):
            ttk.Label(customer_info_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(customer_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Item information
        item_info_frame = ttk.LabelFrame(info_container, text="Thông tin tài sản", padding=10)
        item_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        item_data = [
            ("Mô tả tài sản:", contract['item_description'] or ''),
            ("Giá trị tài sản:", f"{contract['item_value']:,.0f} VNĐ"),
            ("Số tiền cho vay:", f"{contract['loan_amount']:,.0f} VNĐ"),
            ("Tỷ lệ cho vay:", f"{(contract['loan_amount'] / contract['item_value'] * 100):.1f}%")
        ]
        
        for i, (label, value) in enumerate(item_data):
            if label == "Mô tả tài sản:":
                ttk.Label(item_info_frame, text=label).grid(row=i, column=0, sticky=tk.NW, padx=5, pady=2)
                text_widget = tk.Text(item_info_frame, width=60, height=3, wrap=tk.WORD)
                text_widget.insert('1.0', str(value))
                text_widget.config(state=tk.DISABLED)
                text_widget.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            else:
                ttk.Label(item_info_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
                ttk.Label(item_info_frame, text=str(value), font=('Arial', 10, 'bold')).grid(
                    row=i, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Payment history tab
        payment_frame = ttk.Frame(notebook)
        notebook.add(payment_frame, text="Lịch sử thanh toán")
        
        # Notes tab
        notes_frame = ttk.Frame(notebook)
        notebook.add(notes_frame, text="Ghi chú")
        
        if contract['notes']:
            notes_container = ttk.Frame(notes_frame, padding=20)
            notes_container.pack(fill=tk.BOTH, expand=True)
            
            notes_text = tk.Text(notes_container, width=60, height=15, wrap=tk.WORD, state=tk.DISABLED)
            notes_text.insert('1.0', contract['notes'])
            notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ In hợp đồng", 
                  command=lambda: self.print_contract_by_id(contract_id)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💰 Thu lãi", 
                  command=lambda: [dialog.destroy(), self.collect_interest_for_contract(contract['contract_number'])]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Gia hạn", 
                  command=lambda: [dialog.destroy(), self.extend_contract_dialog(contract_id)]).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Đóng", 
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def collect_interest(self):
        """Collect interest for selected contract"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        item = self.contracts_tree.item(selection[0])
        contract_number = item['values'][1]
        self.collect_interest_for_contract(contract_number)
    
    def collect_interest_for_contract(self, contract_number):
        """Collect interest for specific contract"""
        # Switch to payments tab and load contract
        self.notebook.select(2)  # Payments tab
        self.payment_contract_var.set(contract_number)
        self.load_contract_for_payment()
    
    def extend_contract(self):
        """Extend selected contract"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        item = self.contracts_tree.item(selection[0])
        contract_id = item['values'][0]
        self.extend_contract_dialog(contract_id)
    
    def extend_contract_dialog(self, contract_id):
        """Show extend contract dialog"""
        messagebox.showinfo("Thông báo", "Chức năng gia hạn hợp đồng sẽ được phát triển!")
    
    def redeem_item(self):
        """Redeem pawned item"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng chuộc đồ sẽ được phát triển!")
    
    def liquidate_item(self):
        """Liquidate pawned item"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        messagebox.showinfo("Thông báo", "Chức năng thanh lý sẽ được phát triển!")
    
    def print_selected_contract(self):
        """Print selected contract"""
        selection = self.contracts_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng!")
            return
        
        item = self.contracts_tree.item(selection[0])
        contract_id = item['values'][0]
        self.print_contract_by_id(contract_id)
    
    def load_contract_for_payment(self):
        """Load contract details for payment"""
        contract_number = self.payment_contract_var.get().split(' - ')[0] if ' - ' in self.payment_contract_var.get() else self.payment_contract_var.get()
        
        if not contract_number:
            return
        
        # Load contract
        contract = self.db_manager.fetch_one(
            """SELECT pc.*, c.name as customer_name
               FROM pawn_contracts pc
               JOIN customers c ON pc.customer_id = c.id
               WHERE pc.contract_number = ?""",
            (contract_number,)
        )
        
        if not contract:
            messagebox.showwarning("Không tìm thấy", f"Không tìm thấy hợp đồng: {contract_number}")
            return
        
        # Calculate current interest
        try:
            due_date = datetime.strptime(contract['due_date'], '%Y-%m-%d').date()
            overdue_days = max(0, (date.today() - due_date).days)
            months_overdue = max(1, overdue_days / 30)
            current_interest = contract['loan_amount'] * contract['interest_rate'] * months_overdue
            
            # Set suggested payment amount
            self.payment_amount_var.set(f"{current_interest:.0f}")
            
            # Show contract info
            self.show_contract_payment_info(contract, current_interest, overdue_days)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tính toán lãi suất: {e}")
    
    def show_contract_payment_info(self, contract, current_interest, overdue_days):
        """Show contract information for payment"""
        # Show contract info frame
        self.contract_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Clear existing info
        for widget in self.contract_info_frame.winfo_children():
            widget.destroy()
        
        # Display contract info
        info_text = f"""
Hợp đồng: {contract['contract_number']}
Khách hàng: {contract['customer_name']}
Số tiền vay: {contract['loan_amount']:,.0f} VNĐ
Lãi suất: {contract['interest_rate'] * 100:.1f}%/tháng
Ngày đáo hạn: {contract['due_date']}
Số ngày quá hạn: {overdue_days} ngày
Lãi hiện tại: {current_interest:,.0f} VNĐ
Tổng phải trả: {contract['loan_amount'] + current_interest:,.0f} VNĐ
        """
        
        info_label = ttk.Label(self.contract_info_frame, text=info_text.strip(), 
                              font=('Consolas', 10), justify=tk.LEFT)
        info_label.pack(anchor=tk.W, padx=10, pady=10)
    
    def process_payment(self):
        """Process payment"""
        if not self.payment_contract_var.get():
            messagebox.showerror("Lỗi", "Vui lòng chọn hợp đồng!")
            return
        
        if not self.payment_amount_var.get():
            messagebox.showerror("Lỗi", "Vui lòng nhập số tiền thanh toán!")
            return
        
        try:
            payment_amount = float(self.payment_amount_var.get())
            if payment_amount <= 0:
                messagebox.showerror("Lỗi", "Số tiền thanh toán phải lớn hơn 0!")
                return
            
            # Record payment
            messagebox.showinfo("Thành công", f"Đã thu {payment_amount:,.0f} VNĐ!")
            
            # Clear payment form
            self.payment_amount_var.set("")
            self.contract_info_frame.pack_forget()
            
            # Refresh data
            self.load_payment_history()
            self.refresh_contracts()
            
        except ValueError:
            messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xử lý thanh toán: {e}")
    
    def print_receipt(self):
        """Print payment receipt"""
        messagebox.showinfo("Thông báo", "Chức năng in biên lai sẽ được phát triển!")
    
    def load_payment_history(self):
        """Load payment history"""
        # Clear existing items
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        # This would load actual payment records from transactions table
        # For now, showing placeholder
        pass
    
    def generate_summary_report(self):
        """Generate summary report"""
        from_date = self.report_from_date_var.get()
        to_date = self.report_to_date_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoảng thời gian!")
            return
        
        # Clear report text
        self.report_text.delete('1.0', tk.END)
        
        # Generate report
        report = f"""
=== BÁO CÁO TỔNG HỢP DỊCH VỤ CẦM ĐỒ ===
Từ ngày: {from_date} đến ngày: {to_date}
Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. TỔNG QUAN:
   - Tổng số hợp đồng: [Sẽ được tính toán]
   - Tổng tiền cho vay: [Sẽ được tính toán]
   - Tổng lãi thu được: [Sẽ được tính toán]

2. PHÂN TÍCH THEO TRẠNG THÁI:
   - Hợp đồng đang hiệu lực: [Sẽ được tính toán]
   - Hợp đồng quá hạn: [Sẽ được tính toán]
   - Hợp đồng đã chuộc: [Sẽ được tính toán]
   - Hợp đồng đã thanh lý: [Sẽ được tính toán]

3. HIỆU SUẤT:
   - Tỷ lệ chuộc đồ: [Sẽ được tính toán]
   - Tỷ lệ thanh lý: [Sẽ được tính toán]
   - Lợi nhuận trung bình: [Sẽ được tính toán]
        """
        
        self.report_text.insert('1.0', report.strip())
    
    def generate_revenue_report(self):
        """Generate revenue report"""
        messagebox.showinfo("Thông báo", "Chức năng báo cáo thu chi sẽ được phát triển!")
    
    def generate_overdue_report(self):
        """Generate overdue contracts report"""
        messagebox.showinfo("Thông báo", "Chức năng báo cáo quá hạn sẽ được phát triển!")
    
    def export_to_excel(self):
        """Export data to Excel"""
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel sẽ được phát triển!")
