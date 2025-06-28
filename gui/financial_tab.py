#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Financial management tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import calendar

from models import Transaction
from config import BUSINESS_RULES

class FinancialTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup financial tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for sub-tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.setup_dashboard_tab()
        
        # Transactions tab
        self.setup_transactions_tab()
        
        # Debts tab
        self.setup_debts_tab()
        
        # Cash Flow tab
        self.setup_cash_flow_tab()
    
    def setup_dashboard_tab(self):
        """Setup financial dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="Tổng Quan")
        
        # Top summary cards
        summary_frame = ttk.Frame(dashboard_frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Revenue card
        revenue_card = ttk.LabelFrame(summary_frame, text="Doanh thu hôm nay", padding=10)
        revenue_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.today_revenue_label = ttk.Label(revenue_card, text="0 VNĐ", 
                                           style="Success.TLabel", font=('Arial', 16, 'bold'))
        self.today_revenue_label.pack()
        
        # Expenses card
        expenses_card = ttk.LabelFrame(summary_frame, text="Chi phí hôm nay", padding=10)
        expenses_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.today_expenses_label = ttk.Label(expenses_card, text="0 VNĐ", 
                                            style="Error.TLabel", font=('Arial', 16, 'bold'))
        self.today_expenses_label.pack()
        
        # Profit card
        profit_card = ttk.LabelFrame(summary_frame, text="Lợi nhuận hôm nay", padding=10)
        profit_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.today_profit_label = ttk.Label(profit_card, text="0 VNĐ", 
                                          font=('Arial', 16, 'bold'))
        self.today_profit_label.pack()
        
        # Cash on hand card
        cash_card = ttk.LabelFrame(summary_frame, text="Tiền mặt", padding=10)
        cash_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.cash_on_hand_label = ttk.Label(cash_card, text="0 VNĐ", 
                                          style="Warning.TLabel", font=('Arial', 16, 'bold'))
        self.cash_on_hand_label.pack()
        
        # Monthly comparison
        monthly_frame = ttk.LabelFrame(dashboard_frame, text="So sánh theo tháng", padding=10)
        monthly_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Month selector
        month_selector_frame = ttk.Frame(monthly_frame)
        month_selector_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(month_selector_frame, text="Tháng:").pack(side=tk.LEFT)
        self.selected_month_var = tk.StringVar(value=str(date.today().month))
        month_combo = ttk.Combobox(month_selector_frame, textvariable=self.selected_month_var, 
                                  values=list(range(1, 13)), width=10, state="readonly")
        month_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(month_selector_frame, text="Năm:").pack(side=tk.LEFT, padx=(20, 0))
        self.selected_year_var = tk.StringVar(value=str(date.today().year))
        year_combo = ttk.Combobox(month_selector_frame, textvariable=self.selected_year_var,
                                 values=list(range(2020, 2030)), width=10, state="readonly")
        year_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(month_selector_frame, text="🔄 Cập nhật", 
                  command=self.update_monthly_data).pack(side=tk.LEFT, padx=20)
        
        # Monthly statistics
        monthly_stats_frame = ttk.Frame(monthly_frame)
        monthly_stats_frame.pack(fill=tk.X)
        
        # This month
        this_month_frame = ttk.LabelFrame(monthly_stats_frame, text="Tháng này", padding=10)
        this_month_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.this_month_revenue_label = ttk.Label(this_month_frame, text="Doanh thu: 0 VNĐ")
        self.this_month_revenue_label.pack(anchor=tk.W)
        
        self.this_month_expenses_label = ttk.Label(this_month_frame, text="Chi phí: 0 VNĐ")
        self.this_month_expenses_label.pack(anchor=tk.W)
        
        self.this_month_profit_label = ttk.Label(this_month_frame, text="Lợi nhuận: 0 VNĐ", 
                                               font=('Arial', 10, 'bold'))
        self.this_month_profit_label.pack(anchor=tk.W)
        
        # Last month
        last_month_frame = ttk.LabelFrame(monthly_stats_frame, text="Tháng trước", padding=10)
        last_month_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.last_month_revenue_label = ttk.Label(last_month_frame, text="Doanh thu: 0 VNĐ")
        self.last_month_revenue_label.pack(anchor=tk.W)
        
        self.last_month_expenses_label = ttk.Label(last_month_frame, text="Chi phí: 0 VNĐ")
        self.last_month_expenses_label.pack(anchor=tk.W)
        
        self.last_month_profit_label = ttk.Label(last_month_frame, text="Lợi nhuận: 0 VNĐ", 
                                               font=('Arial', 10, 'bold'))
        self.last_month_profit_label.pack(anchor=tk.W)
        
        # Growth comparison
        growth_frame = ttk.LabelFrame(monthly_stats_frame, text="Tăng trưởng", padding=10)
        growth_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.revenue_growth_label = ttk.Label(growth_frame, text="Doanh thu: 0%")
        self.revenue_growth_label.pack(anchor=tk.W)
        
        self.profit_growth_label = ttk.Label(growth_frame, text="Lợi nhuận: 0%")
        self.profit_growth_label.pack(anchor=tk.W)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(dashboard_frame, text="Thao tác nhanh", padding=10)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(actions_frame, text="➕ Thu tiền", 
                  command=self.quick_income).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="➖ Chi tiền", 
                  command=self.quick_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="💰 Kiểm kê tiền mặt", 
                  command=self.cash_count).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📊 Báo cáo nhanh", 
                  command=self.quick_report).pack(side=tk.LEFT, padx=5)
        
        # Recent transactions
        recent_frame = ttk.LabelFrame(dashboard_frame, text="Giao dịch gần đây", padding=10)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.recent_transactions_tree = ttk.Treeview(recent_frame,
                                                   columns=('time', 'type', 'amount', 'description'),
                                                   show='headings', height=8)
        
        self.recent_transactions_tree.heading('time', text='Thời gian')
        self.recent_transactions_tree.heading('type', text='Loại')
        self.recent_transactions_tree.heading('amount', text='Số tiền')
        self.recent_transactions_tree.heading('description', text='Mô tả')
        
        self.recent_transactions_tree.column('time', width=120)
        self.recent_transactions_tree.column('type', width=80)
        self.recent_transactions_tree.column('amount', width=100)
        self.recent_transactions_tree.column('description', width=250)
        
        self.recent_transactions_tree.pack(fill=tk.BOTH, expand=True)
    
    def setup_transactions_tab(self):
        """Setup transactions management tab"""
        transactions_frame = ttk.Frame(self.notebook)
        self.notebook.add(transactions_frame, text="Giao Dịch")
        
        # Top controls
        top_frame = ttk.Frame(transactions_frame)
        top_frame.pack(fill=tk.X, pady=(10, 10), padx=10)
        
        # Date filter
        date_frame = ttk.LabelFrame(top_frame, text="Lọc theo ngày", padding=10)
        date_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(date_frame, text="Từ:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.trans_from_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.trans_from_date_var, width=12)
        from_date_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(date_frame, text="Đến:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.trans_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.trans_to_date_var, width=12)
        to_date_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Button(date_frame, text="🔍 Lọc", 
                  command=self.filter_transactions).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Type filter
        type_frame = ttk.LabelFrame(top_frame, text="Loại giao dịch", padding=10)
        type_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.transaction_type_filter_var = tk.StringVar(value="all")
        type_values = [
            ("all", "Tất cả"),
            ("income", "Thu"),
            ("expense", "Chi")
        ]
        
        for value, text in type_values:
            ttk.Radiobutton(type_frame, text=text, variable=self.transaction_type_filter_var,
                           value=value, command=self.filter_transactions).pack(anchor=tk.W)
        
        # Control buttons
        btn_frame = ttk.Frame(top_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="➕ Thu tiền", 
                  command=self.add_income).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="➖ Chi tiền", 
                  command=self.add_expense).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="✏️ Sửa", 
                  command=self.edit_transaction).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🗑️ Xóa", 
                  command=self.delete_transaction).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                  command=self.refresh_transactions).pack(pady=2, fill=tk.X)
        
        # Transactions treeview
        tree_frame = ttk.Frame(transactions_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        self.transactions_tree = ttk.Treeview(tree_frame,
                                            columns=('id', 'date', 'type', 'amount', 'description',
                                                   'payment_method', 'reference', 'staff'),
                                            show='headings',
                                            yscrollcommand=v_scrollbar.set,
                                            xscrollcommand=h_scrollbar.set)
        
        # Configure scrollbars
        v_scrollbar.config(command=self.transactions_tree.yview)
        h_scrollbar.config(command=self.transactions_tree.xview)
        
        # Column headings
        columns = {
            'id': ('ID', 50),
            'date': ('Ngày', 120),
            'type': ('Loại', 80),
            'amount': ('Số tiền', 100),
            'description': ('Mô tả', 250),
            'payment_method': ('Hình thức', 100),
            'reference': ('Tham chiếu', 120),
            'staff': ('Nhân viên', 120)
        }
        
        for col, (heading, width) in columns.items():
            self.transactions_tree.heading(col, text=heading)
            self.transactions_tree.column(col, width=width, minwidth=50)
        
        # Pack treeview and scrollbars
        self.transactions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind double-click
        self.transactions_tree.bind('<Double-1>', lambda e: self.edit_transaction())
    
    def setup_debts_tab(self):
        """Setup debts management tab"""
        debts_frame = ttk.Frame(self.notebook)
        self.notebook.add(debts_frame, text="Công Nợ")
        
        # Create sub-notebook for customer and supplier debts
        debts_notebook = ttk.Notebook(debts_frame)
        debts_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Customer debts
        customer_debts_frame = ttk.Frame(debts_notebook)
        debts_notebook.add(customer_debts_frame, text="Nợ Khách Hàng")
        
        # Customer debts controls
        customer_top_frame = ttk.Frame(customer_debts_frame)
        customer_top_frame.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(customer_top_frame, text="➕ Thêm nợ", 
                  command=self.add_customer_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(customer_top_frame, text="💰 Thu nợ", 
                  command=self.collect_customer_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(customer_top_frame, text="📊 Sao kê", 
                  command=self.customer_debt_statement).pack(side=tk.LEFT, padx=5)
        
        # Customer debts treeview
        self.customer_debts_tree = ttk.Treeview(customer_debts_frame,
                                              columns=('customer', 'amount', 'description', 'due_date', 'overdue_days'),
                                              show='headings')
        
        columns = {
            'customer': ('Khách hàng', 200),
            'amount': ('Số nợ', 100),
            'description': ('Mô tả', 250),
            'due_date': ('Hạn trả', 100),
            'overdue_days': ('Quá hạn', 80)
        }
        
        for col, (heading, width) in columns.items():
            self.customer_debts_tree.heading(col, text=heading)
            self.customer_debts_tree.column(col, width=width, minwidth=50)
        
        self.customer_debts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Supplier debts
        supplier_debts_frame = ttk.Frame(debts_notebook)
        debts_notebook.add(supplier_debts_frame, text="Nợ Nhà Cung Cấp")
        
        # Supplier debts controls
        supplier_top_frame = ttk.Frame(supplier_debts_frame)
        supplier_top_frame.pack(fill=tk.X, pady=(10, 10))
        
        ttk.Button(supplier_top_frame, text="➕ Thêm nợ", 
                  command=self.add_supplier_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(supplier_top_frame, text="💰 Trả nợ", 
                  command=self.pay_supplier_debt).pack(side=tk.LEFT, padx=5)
        ttk.Button(supplier_top_frame, text="📊 Sao kê", 
                  command=self.supplier_debt_statement).pack(side=tk.LEFT, padx=5)
        
        # Supplier debts treeview
        self.supplier_debts_tree = ttk.Treeview(supplier_debts_frame,
                                              columns=('supplier', 'amount', 'description', 'due_date', 'overdue_days'),
                                              show='headings')
        
        for col, (heading, width) in columns.items():
            self.supplier_debts_tree.heading(col, text=heading)
            self.supplier_debts_tree.column(col, width=width, minwidth=50)
        
        self.supplier_debts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def setup_cash_flow_tab(self):
        """Setup cash flow management tab"""
        cash_flow_frame = ttk.Frame(self.notebook)
        self.notebook.add(cash_flow_frame, text="Dòng Tiền")
        
        # Cash sources
        sources_frame = ttk.LabelFrame(cash_flow_frame, text="Nguồn tiền", padding=10)
        sources_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Cash sources treeview
        self.cash_sources_tree = ttk.Treeview(sources_frame,
                                            columns=('source', 'amount', 'last_updated'),
                                            show='headings', height=6)
        
        self.cash_sources_tree.heading('source', text='Nguồn')
        self.cash_sources_tree.heading('amount', text='Số tiền')
        self.cash_sources_tree.heading('last_updated', text='Cập nhật lần cuối')
        
        self.cash_sources_tree.column('source', width=200)
        self.cash_sources_tree.column('amount', width=150)
        self.cash_sources_tree.column('last_updated', width=150)
        
        self.cash_sources_tree.pack(fill=tk.X, pady=(0, 10))
        
        # Cash source controls
        source_controls = ttk.Frame(sources_frame)
        source_controls.pack(fill=tk.X)
        
        ttk.Button(source_controls, text="➕ Thêm nguồn", 
                  command=self.add_cash_source).pack(side=tk.LEFT, padx=5)
        ttk.Button(source_controls, text="✏️ Sửa", 
                  command=self.edit_cash_source).pack(side=tk.LEFT, padx=5)
        ttk.Button(source_controls, text="💰 Điều chỉnh", 
                  command=self.adjust_cash_source).pack(side=tk.LEFT, padx=5)
        
        # Daily cash flow
        daily_flow_frame = ttk.LabelFrame(cash_flow_frame, text="Dòng tiền hàng ngày", padding=10)
        daily_flow_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Date selector
        date_selector = ttk.Frame(daily_flow_frame)
        date_selector.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(date_selector, text="Ngày:").pack(side=tk.LEFT)
        self.cash_flow_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        date_entry = ttk.Entry(date_selector, textvariable=self.cash_flow_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(date_selector, text="📊 Xem", 
                  command=self.view_daily_cash_flow).pack(side=tk.LEFT, padx=10)
        ttk.Button(date_selector, text="📄 Báo cáo", 
                  command=self.generate_cash_flow_report).pack(side=tk.LEFT, padx=5)
        
        # Cash flow summary
        self.cash_flow_text = tk.Text(daily_flow_frame, height=15, wrap=tk.WORD, font=('Consolas', 10))
        self.cash_flow_text.pack(fill=tk.BOTH, expand=True)
        
        # Cash flow scrollbar
        cash_flow_scrollbar = ttk.Scrollbar(daily_flow_frame, orient=tk.VERTICAL, command=self.cash_flow_text.yview)
        self.cash_flow_text.config(yscrollcommand=cash_flow_scrollbar.set)
    
    def load_data(self):
        """Load all financial data"""
        self.refresh_dashboard()
        self.refresh_transactions()
        self.refresh_debts()
        self.refresh_cash_sources()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        try:
            # Today's data
            today = date.today().strftime('%Y-%m-%d')
            
            # Today's revenue
            today_revenue = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'income' AND DATE(transaction_date) = ?""",
                (today,)
            )
            self.today_revenue_label.config(text=f"{today_revenue['total']:,.0f} VNĐ")
            
            # Today's expenses
            today_expenses = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'expense' AND DATE(transaction_date) = ?""",
                (today,)
            )
            self.today_expenses_label.config(text=f"{today_expenses['total']:,.0f} VNĐ")
            
            # Today's profit
            today_profit = today_revenue['total'] - today_expenses['total']
            self.today_profit_label.config(text=f"{today_profit:,.0f} VNĐ")
            
            # Set profit color
            if today_profit > 0:
                self.today_profit_label.config(style="Success.TLabel")
            elif today_profit < 0:
                self.today_profit_label.config(style="Error.TLabel")
            else:
                self.today_profit_label.config(style="")
            
            # Cash on hand (this would be calculated from cash sources)
            self.cash_on_hand_label.config(text="0 VNĐ")
            
            # Load recent transactions
            self.load_recent_transactions()
            
            # Update monthly data
            self.update_monthly_data()
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    def load_recent_transactions(self):
        """Load recent transactions for dashboard"""
        # Clear existing items
        for item in self.recent_transactions_tree.get_children():
            self.recent_transactions_tree.delete(item)
        
        # Load recent transactions
        transactions = self.db_manager.fetch_all(
            """SELECT * FROM transactions 
               ORDER BY transaction_date DESC 
               LIMIT 10"""
        )
        
        for trans in transactions:
            trans_time = datetime.fromisoformat(trans['transaction_date']).strftime('%H:%M')
            trans_type = "Thu" if trans['transaction_type'] == 'income' else "Chi"
            
            self.recent_transactions_tree.insert('', 'end', values=(
                trans_time,
                trans_type,
                f"{trans['amount']:,.0f}",
                trans['description'][:50] + "..." if len(trans['description']) > 50 else trans['description']
            ))
    
    def update_monthly_data(self):
        """Update monthly comparison data"""
        try:
            selected_month = int(self.selected_month_var.get())
            selected_year = int(self.selected_year_var.get())
            
            # This month
            this_month_start = date(selected_year, selected_month, 1)
            if selected_month == 12:
                this_month_end = date(selected_year + 1, 1, 1) - timedelta(days=1)
            else:
                this_month_end = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
            
            # This month revenue
            this_month_revenue = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'income' 
                   AND DATE(transaction_date) BETWEEN ? AND ?""",
                (this_month_start.strftime('%Y-%m-%d'), this_month_end.strftime('%Y-%m-%d'))
            )
            
            # This month expenses
            this_month_expenses = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'expense' 
                   AND DATE(transaction_date) BETWEEN ? AND ?""",
                (this_month_start.strftime('%Y-%m-%d'), this_month_end.strftime('%Y-%m-%d'))
            )
            
            this_month_profit = this_month_revenue['total'] - this_month_expenses['total']
            
            self.this_month_revenue_label.config(text=f"Doanh thu: {this_month_revenue['total']:,.0f} VNĐ")
            self.this_month_expenses_label.config(text=f"Chi phí: {this_month_expenses['total']:,.0f} VNĐ")
            self.this_month_profit_label.config(text=f"Lợi nhuận: {this_month_profit:,.0f} VNĐ")
            
            # Last month
            if selected_month == 1:
                last_month = 12
                last_year = selected_year - 1
            else:
                last_month = selected_month - 1
                last_year = selected_year
            
            last_month_start = date(last_year, last_month, 1)
            last_month_end = date(selected_year, selected_month, 1) - timedelta(days=1)
            
            # Last month revenue
            last_month_revenue = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'income' 
                   AND DATE(transaction_date) BETWEEN ? AND ?""",
                (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d'))
            )
            
            # Last month expenses
            last_month_expenses = self.db_manager.fetch_one(
                """SELECT COALESCE(SUM(amount), 0) as total 
                   FROM transactions 
                   WHERE transaction_type = 'expense' 
                   AND DATE(transaction_date) BETWEEN ? AND ?""",
                (last_month_start.strftime('%Y-%m-%d'), last_month_end.strftime('%Y-%m-%d'))
            )
            
            last_month_profit = last_month_revenue['total'] - last_month_expenses['total']
            
            self.last_month_revenue_label.config(text=f"Doanh thu: {last_month_revenue['total']:,.0f} VNĐ")
            self.last_month_expenses_label.config(text=f"Chi phí: {last_month_expenses['total']:,.0f} VNĐ")
            self.last_month_profit_label.config(text=f"Lợi nhuận: {last_month_profit:,.0f} VNĐ")
            
            # Calculate growth
            revenue_growth = 0
            profit_growth = 0
            
            if last_month_revenue['total'] > 0:
                revenue_growth = ((this_month_revenue['total'] - last_month_revenue['total']) / last_month_revenue['total']) * 100
            
            if last_month_profit != 0:
                profit_growth = ((this_month_profit - last_month_profit) / abs(last_month_profit)) * 100
            
            self.revenue_growth_label.config(text=f"Doanh thu: {revenue_growth:+.1f}%")
            self.profit_growth_label.config(text=f"Lợi nhuận: {profit_growth:+.1f}%")
            
        except Exception as e:
            print(f"Error updating monthly data: {e}")
    
    def quick_income(self):
        """Quick income entry"""
        self.show_transaction_dialog(transaction_type='income')
    
    def quick_expense(self):
        """Quick expense entry"""
        self.show_transaction_dialog(transaction_type='expense')
    
    def cash_count(self):
        """Cash counting dialog"""
        messagebox.showinfo("Thông báo", "Chức năng kiểm kê tiền mặt sẽ được phát triển!")
    
    def quick_report(self):
        """Generate quick financial report"""
        messagebox.showinfo("Thông báo", "Chức năng báo cáo nhanh sẽ được phát triển!")
    
    def refresh_transactions(self):
        """Refresh transactions list"""
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Load transactions
        query = """
        SELECT t.*, s.full_name as staff_name
        FROM transactions t
        LEFT JOIN staff s ON t.staff_id = s.id
        ORDER BY t.transaction_date DESC
        LIMIT 1000
        """
        
        transactions = self.db_manager.fetch_all(query)
        
        for trans in transactions:
            trans_date = datetime.fromisoformat(trans['transaction_date']).strftime('%d/%m/%Y %H:%M')
            trans_type = "Thu" if trans['transaction_type'] == 'income' else "Chi"
            
            # Format reference
            reference = ""
            if trans['reference_type'] and trans['reference_id']:
                reference = f"{trans['reference_type']}#{trans['reference_id']}"
            
            self.transactions_tree.insert('', 'end', values=(
                trans['id'],
                trans_date,
                trans_type,
                f"{trans['amount']:,.0f}",
                trans['description'] or '',
                trans['payment_method'] or '',
                reference,
                trans['staff_name'] or ''
            ))
    
    def filter_transactions(self):
        """Filter transactions by date and type"""
        from_date = self.trans_from_date_var.get()
        to_date = self.trans_to_date_var.get()
        trans_type = self.transaction_type_filter_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ khoảng thời gian!")
            return
        
        # Clear existing items
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        
        # Build query
        if trans_type == "all":
            query = """
            SELECT t.*, s.full_name as staff_name
            FROM transactions t
            LEFT JOIN staff s ON t.staff_id = s.id
            WHERE DATE(t.transaction_date) BETWEEN ? AND ?
            ORDER BY t.transaction_date DESC
            """
            params = (from_date, to_date)
        else:
            query = """
            SELECT t.*, s.full_name as staff_name
            FROM transactions t
            LEFT JOIN staff s ON t.staff_id = s.id
            WHERE DATE(t.transaction_date) BETWEEN ? AND ? AND t.transaction_type = ?
            ORDER BY t.transaction_date DESC
            """
            params = (from_date, to_date, trans_type)
        
        transactions = self.db_manager.fetch_all(query, params)
        
        for trans in transactions:
            trans_date = datetime.fromisoformat(trans['transaction_date']).strftime('%d/%m/%Y %H:%M')
            trans_type_display = "Thu" if trans['transaction_type'] == 'income' else "Chi"
            
            reference = ""
            if trans['reference_type'] and trans['reference_id']:
                reference = f"{trans['reference_type']}#{trans['reference_id']}"
            
            self.transactions_tree.insert('', 'end', values=(
                trans['id'],
                trans_date,
                trans_type_display,
                f"{trans['amount']:,.0f}",
                trans['description'] or '',
                trans['payment_method'] or '',
                reference,
                trans['staff_name'] or ''
            ))
    
    def add_income(self):
        """Add income transaction"""
        self.show_transaction_dialog(transaction_type='income')
    
    def add_expense(self):
        """Add expense transaction"""
        self.show_transaction_dialog(transaction_type='expense')
    
    def show_transaction_dialog(self, transaction_id=None, transaction_type='income'):
        """Show add/edit transaction dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Thu tiền" if transaction_type == 'income' else "Chi tiền")
        dialog.geometry("500x400")
        dialog.transient(self.frame)
        dialog.grab_set()
        
        # Load existing transaction data if editing
        transaction_data = {}
        if transaction_id:
            trans = self.db_manager.fetch_one("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
            if trans:
                transaction_data = dict(trans)
                transaction_type = transaction_data['transaction_type']
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # Amount
        ttk.Label(main_frame, text="Số tiền *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        amount_var = tk.StringVar(value=str(transaction_data.get('amount', '')))
        amount_entry = ttk.Entry(main_frame, textvariable=amount_var, width=30, font=('Arial', 12))
        amount_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Description
        ttk.Label(main_frame, text="Mô tả *:").grid(row=row, column=0, sticky=tk.W, pady=5)
        description_var = tk.StringVar(value=transaction_data.get('description', ''))
        description_entry = ttk.Entry(main_frame, textvariable=description_var, width=40)
        description_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Payment method
        ttk.Label(main_frame, text="Hình thức:").grid(row=row, column=0, sticky=tk.W, pady=5)
        payment_method_var = tk.StringVar(value=transaction_data.get('payment_method', 'cash'))
        payment_method_combo = ttk.Combobox(main_frame, textvariable=payment_method_var, width=37,
                                           values=['cash', 'card', 'transfer', 'other'], state="readonly")
        payment_method_combo.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Date and time
        ttk.Label(main_frame, text="Ngày giờ:").grid(row=row, column=0, sticky=tk.W, pady=5)
        datetime_var = tk.StringVar(value=transaction_data.get('transaction_date', datetime.now().strftime('%Y-%m-%d %H:%M')))
        datetime_entry = ttk.Entry(main_frame, textvariable=datetime_var, width=30)
        datetime_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Reference (optional)
        ttk.Label(main_frame, text="Tham chiếu:").grid(row=row, column=0, sticky=tk.W, pady=5)
        reference_var = tk.StringVar(value=transaction_data.get('reference_type', ''))
        reference_entry = ttk.Entry(main_frame, textvariable=reference_var, width=40)
        reference_entry.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Notes
        ttk.Label(main_frame, text="Ghi chú:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(main_frame, width=40, height=6)
        notes_text.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        row += 1
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        def save_transaction():
            if not amount_var.get() or not description_var.get():
                messagebox.showerror("Lỗi", "Vui lòng nhập số tiền và mô tả!")
                return
            
            try:
                amount = float(amount_var.get())
                if amount <= 0:
                    messagebox.showerror("Lỗi", "Số tiền phải lớn hơn 0!")
                    return
                
                # Parse datetime
                try:
                    trans_datetime = datetime.strptime(datetime_var.get(), '%Y-%m-%d %H:%M')
                except:
                    trans_datetime = datetime.now()
                
                data = {
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'description': description_var.get().strip(),
                    'payment_method': payment_method_var.get(),
                    'staff_id': self.current_user['id'],
                    'transaction_date': trans_datetime.isoformat(),
                    'created_at': datetime.now().isoformat()
                }
                
                if transaction_id:
                    # Update existing transaction
                    data['updated_at'] = datetime.now().isoformat()
                    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
                    query = f"UPDATE transactions SET {set_clause} WHERE id = ?"
                    params = list(data.values()) + [transaction_id]
                else:
                    # Insert new transaction
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    query = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
                    params = list(data.values())
                
                self.db_manager.execute_query(query, params)
                
                messagebox.showinfo("Thành công", 
                                   "Đã cập nhật giao dịch!" if transaction_id else "Đã thêm giao dịch!")
                dialog.destroy()
                self.refresh_transactions()
                self.refresh_dashboard()
                
            except ValueError:
                messagebox.showerror("Lỗi", "Số tiền không hợp lệ!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu giao dịch: {e}")
        
        ttk.Button(btn_frame, text="💾 Lưu", command=save_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Focus on amount entry
        amount_entry.focus_set()
    
    def edit_transaction(self):
        """Edit selected transaction"""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giao dịch!")
            return
        
        item = self.transactions_tree.item(selection[0])
        transaction_id = item['values'][0]
        self.show_transaction_dialog(transaction_id)
    
    def delete_transaction(self):
        """Delete selected transaction"""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn giao dịch!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giao dịch này?"):
            item = self.transactions_tree.item(selection[0])
            transaction_id = item['values'][0]
            
            try:
                self.db_manager.execute_query("DELETE FROM transactions WHERE id = ?", (transaction_id,))
                messagebox.showinfo("Thành công", "Đã xóa giao dịch!")
                self.refresh_transactions()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa giao dịch: {e}")
    
    def refresh_debts(self):
        """Refresh debts data"""
        # Clear existing items
        for item in self.customer_debts_tree.get_children():
            self.customer_debts_tree.delete(item)
        
        for item in self.supplier_debts_tree.get_children():
            self.supplier_debts_tree.delete(item)
        
        # Load customer debts
        customer_debts = self.db_manager.fetch_all(
            """SELECT d.*, c.name as customer_name
               FROM debts d
               JOIN customers c ON d.debtor_id = c.id
               WHERE d.debtor_type = 'customer' AND d.status = 'outstanding'
               ORDER BY d.created_at DESC"""
        )
        
        for debt in customer_debts:
            # Calculate overdue days
            overdue_days = 0
            if debt['due_date']:
                try:
                    due_date = datetime.strptime(debt['due_date'], '%Y-%m-%d').date()
                    overdue_days = max(0, (date.today() - due_date).days)
                except:
                    pass
            
            self.customer_debts_tree.insert('', 'end', values=(
                debt['customer_name'],
                f"{debt['amount']:,.0f}",
                debt['description'] or '',
                debt['due_date'] or '',
                f"{overdue_days} ngày" if overdue_days > 0 else ""
            ))
        
        # Load supplier debts (would need suppliers table)
        # For now, showing placeholder
        pass
    
    def add_customer_debt(self):
        """Add customer debt"""
        messagebox.showinfo("Thông báo", "Chức năng thêm nợ khách hàng sẽ được phát triển!")
    
    def collect_customer_debt(self):
        """Collect customer debt"""
        messagebox.showinfo("Thông báo", "Chức năng thu nợ khách hàng sẽ được phát triển!")
    
    def customer_debt_statement(self):
        """Generate customer debt statement"""
        messagebox.showinfo("Thông báo", "Chức năng sao kê nợ khách hàng sẽ được phát triển!")
    
    def add_supplier_debt(self):
        """Add supplier debt"""
        messagebox.showinfo("Thông báo", "Chức năng thêm nợ nhà cung cấp sẽ được phát triển!")
    
    def pay_supplier_debt(self):
        """Pay supplier debt"""
        messagebox.showinfo("Thông báo", "Chức năng trả nợ nhà cung cấp sẽ được phát triển!")
    
    def supplier_debt_statement(self):
        """Generate supplier debt statement"""
        messagebox.showinfo("Thông báo", "Chức năng sao kê nợ nhà cung cấp sẽ được phát triển!")
    
    def refresh_cash_sources(self):
        """Refresh cash sources"""
        # Clear existing items
        for item in self.cash_sources_tree.get_children():
            self.cash_sources_tree.delete(item)
        
        # Default cash sources
        default_sources = [
            ("Tiền mặt", 0, "Chưa cập nhật"),
            ("Ngân hàng Vietcombank", 0, "Chưa cập nhật"),
            ("Ngân hàng Techcombank", 0, "Chưa cập nhật")
        ]
        
        for source, amount, updated in default_sources:
            self.cash_sources_tree.insert('', 'end', values=(
                source,
                f"{amount:,.0f} VNĐ",
                updated
            ))
    
    def add_cash_source(self):
        """Add cash source"""
        messagebox.showinfo("Thông báo", "Chức năng thêm nguồn tiền sẽ được phát triển!")
    
    def edit_cash_source(self):
        """Edit cash source"""
        messagebox.showinfo("Thông báo", "Chức năng sửa nguồn tiền sẽ được phát triển!")
    
    def adjust_cash_source(self):
        """Adjust cash source amount"""
        messagebox.showinfo("Thông báo", "Chức năng điều chỉnh nguồn tiền sẽ được phát triển!")
    
    def view_daily_cash_flow(self):
        """View daily cash flow"""
        selected_date = self.cash_flow_date_var.get()
        
        if not selected_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngày!")
            return
        
        # Clear cash flow text
        self.cash_flow_text.delete('1.0', tk.END)
        
        # Generate cash flow report
        cash_flow_report = f"""
=== BÁO CÁO DÒNG TIỀN NGÀY {selected_date} ===
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. SỐ DƯ ĐẦU NGÀY:
   - Tiền mặt: [Sẽ được tính toán]
   - Ngân hàng: [Sẽ được tính toán]
   - Tổng cộng: [Sẽ được tính toán]

2. DÒNG TIỀN VÀO:
   - Bán hàng: [Sẽ được tính toán]
   - Thu nợ: [Sẽ được tính toán]
   - Thu khác: [Sẽ được tính toán]
   - Tổng thu: [Sẽ được tính toán]

3. DÒNG TIỀN RA:
   - Nhập hàng: [Sẽ được tính toán]
   - Chi phí hoạt động: [Sẽ được tính toán]
   - Trả nợ: [Sẽ được tính toán]
   - Chi khác: [Sẽ được tính toán]
   - Tổng chi: [Sẽ được tính toán]

4. SỐ DƯ CUỐI NGÀY:
   - Tiền mặt: [Sẽ được tính toán]
   - Ngân hàng: [Sẽ được tính toán]
   - Tổng cộng: [Sẽ được tính toán]

5. DÒNG TIỀN RÒNG: [Sẽ được tính toán]
        """
        
        self.cash_flow_text.insert('1.0', cash_flow_report.strip())
    
    def generate_cash_flow_report(self):
        """Generate detailed cash flow report"""
        messagebox.showinfo("Thông báo", "Chức năng báo cáo dòng tiền chi tiết sẽ được phát triển!")


