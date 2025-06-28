#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reports and analytics tab for ChViet Mobile Store Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import calendar

from config import BUSINESS_RULES

class ReportsTab:
    def __init__(self, parent, db_manager, current_user):
        self.parent = parent
        self.db_manager = db_manager
        self.current_user = current_user
        
        self.frame = ttk.Frame(parent)
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup reports tab UI"""
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for report categories
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sales Reports tab
        self.setup_sales_reports_tab()
        
        # Inventory Reports tab
        self.setup_inventory_reports_tab()
        
        # Financial Reports tab
        self.setup_financial_reports_tab()
        
        # Customer Reports tab
        self.setup_customer_reports_tab()
        
        # Performance Reports tab
        self.setup_performance_reports_tab()
    
    def setup_sales_reports_tab(self):
        """Setup sales reports tab"""
        sales_reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(sales_reports_frame, text="Báo Cáo Bán Hàng")
        
        # Report controls
        controls_frame = ttk.LabelFrame(sales_reports_frame, text="Tùy chọn báo cáo", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Từ ngày:").pack(side=tk.LEFT)
        self.sales_from_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.sales_from_date_var, width=12)
        from_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Đến ngày:").pack(side=tk.LEFT, padx=(20, 0))
        self.sales_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.sales_to_date_var, width=12)
        to_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Report type
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(report_type_frame, text="Loại báo cáo:").pack(side=tk.LEFT)
        self.sales_report_type_var = tk.StringVar(value="summary")
        
        report_types = [
            ("summary", "Tổng hợp"),
            ("daily", "Theo ngày"),
            ("monthly", "Theo tháng"),
            ("by_product", "Theo sản phẩm"),
            ("by_staff", "Theo nhân viên"),
            ("by_customer", "Theo khách hàng")
        ]
        
        for value, text in report_types:
            ttk.Radiobutton(report_type_frame, text=text, variable=self.sales_report_type_var,
                           value=value).pack(side=tk.LEFT, padx=10)
        
        # Report buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Tạo báo cáo", 
                  command=self.generate_sales_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In báo cáo", 
                  command=self.print_sales_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_sales_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📈 Biểu đồ", 
                  command=self.show_sales_chart).pack(side=tk.LEFT, padx=5)
        
        # Report display
        report_display_frame = ttk.LabelFrame(sales_reports_frame, text="Kết quả báo cáo", padding=10)
        report_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create notebook for different views
        display_notebook = ttk.Notebook(report_display_frame)
        display_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Text report tab
        text_report_frame = ttk.Frame(display_notebook)
        display_notebook.add(text_report_frame, text="Báo cáo văn bản")
        
        self.sales_report_text = tk.Text(text_report_frame, wrap=tk.WORD, font=('Consolas', 10))
        sales_text_scrollbar = ttk.Scrollbar(text_report_frame, orient=tk.VERTICAL, command=self.sales_report_text.yview)
        self.sales_report_text.config(yscrollcommand=sales_text_scrollbar.set)
        
        self.sales_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sales_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Table report tab
        table_report_frame = ttk.Frame(display_notebook)
        display_notebook.add(table_report_frame, text="Bảng dữ liệu")
        
        self.sales_report_tree = ttk.Treeview(table_report_frame, show='headings')
        sales_table_scrollbar = ttk.Scrollbar(table_report_frame, orient=tk.VERTICAL, command=self.sales_report_tree.yview)
        self.sales_report_tree.config(yscrollcommand=sales_table_scrollbar.set)
        
        self.sales_report_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sales_table_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_inventory_reports_tab(self):
        """Setup inventory reports tab"""
        inventory_reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(inventory_reports_frame, text="Báo Cáo Kho Hàng")
        
        # Report controls
        controls_frame = ttk.LabelFrame(inventory_reports_frame, text="Tùy chọn báo cáo", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Report type
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(report_type_frame, text="Loại báo cáo:").pack(side=tk.LEFT)
        self.inventory_report_type_var = tk.StringVar(value="current_stock")
        
        inventory_report_types = [
            ("current_stock", "Tồn kho hiện tại"),
            ("low_stock", "Sắp hết hàng"),
            ("stock_movement", "Xuất nhập tồn"),
            ("abc_analysis", "Phân tích ABC"),
            ("aging_report", "Báo cáo lưu kho"),
            ("imei_tracking", "Theo dõi IMEI")
        ]
        
        row = 0
        for i, (value, text) in enumerate(inventory_report_types):
            col = i % 3
            if col == 0 and i > 0:
                row += 1
            
            ttk.Radiobutton(report_type_frame, text=text, variable=self.inventory_report_type_var,
                           value=value).grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Category filter
        filter_frame = ttk.Frame(controls_frame)
        filter_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filter_frame, text="Danh mục:").pack(side=tk.LEFT)
        self.inventory_category_var = tk.StringVar()
        category_combo = ttk.Combobox(filter_frame, textvariable=self.inventory_category_var, width=30)
        category_combo.pack(side=tk.LEFT, padx=10)
        
        # Load categories
        self.load_categories_combo(category_combo)
        
        # Report buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Tạo báo cáo", 
                  command=self.generate_inventory_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In báo cáo", 
                  command=self.print_inventory_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_inventory_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="⚠️ Cảnh báo hết hàng", 
                  command=self.show_stock_alerts).pack(side=tk.LEFT, padx=5)
        
        # Report display
        self.inventory_report_text = tk.Text(inventory_reports_frame, wrap=tk.WORD, font=('Consolas', 10))
        inventory_scrollbar = ttk.Scrollbar(inventory_reports_frame, orient=tk.VERTICAL, command=self.inventory_report_text.yview)
        self.inventory_report_text.config(yscrollcommand=inventory_scrollbar.set)
        
        self.inventory_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        inventory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
    
    def setup_financial_reports_tab(self):
        """Setup financial reports tab"""
        financial_reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(financial_reports_frame, text="Báo Cáo Tài Chính")
        
        # Report controls
        controls_frame = ttk.LabelFrame(financial_reports_frame, text="Tùy chọn báo cáo", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Date range
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="Từ ngày:").pack(side=tk.LEFT)
        self.financial_from_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.financial_from_date_var, width=12)
        from_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Đến ngày:").pack(side=tk.LEFT, padx=(20, 0))
        self.financial_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.financial_to_date_var, width=12)
        to_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Report type
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(report_type_frame, text="Loại báo cáo:").pack(side=tk.LEFT)
        self.financial_report_type_var = tk.StringVar(value="profit_loss")
        
        financial_report_types = [
            ("profit_loss", "Lãi lỗ"),
            ("cash_flow", "Dòng tiền"),
            ("revenue_analysis", "Phân tích doanh thu"),
            ("expense_analysis", "Phân tích chi phí"),
            ("debt_report", "Báo cáo công nợ"),
            ("tax_report", "Báo cáo thuế")
        ]
        
        row = 0
        for i, (value, text) in enumerate(financial_report_types):
            col = i % 3
            if col == 0 and i > 0:
                row += 1
            
            ttk.Radiobutton(report_type_frame, text=text, variable=self.financial_report_type_var,
                           value=value).grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Report buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Tạo báo cáo", 
                  command=self.generate_financial_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In báo cáo", 
                  command=self.print_financial_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_financial_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📈 Biểu đồ", 
                  command=self.show_financial_chart).pack(side=tk.LEFT, padx=5)
        
        # Report display
        self.financial_report_text = tk.Text(financial_reports_frame, wrap=tk.WORD, font=('Consolas', 10))
        financial_scrollbar = ttk.Scrollbar(financial_reports_frame, orient=tk.VERTICAL, command=self.financial_report_text.yview)
        self.financial_report_text.config(yscrollcommand=financial_scrollbar.set)
        
        self.financial_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        financial_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
    
    def setup_customer_reports_tab(self):
        """Setup customer reports tab"""
        customer_reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(customer_reports_frame, text="Báo Cáo Khách Hàng")
        
        # Report controls
        controls_frame = ttk.LabelFrame(customer_reports_frame, text="Tùy chọn báo cáo", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Report type
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(report_type_frame, text="Loại báo cáo:").pack(side=tk.LEFT)
        self.customer_report_type_var = tk.StringVar(value="customer_list")
        
        customer_report_types = [
            ("customer_list", "Danh sách khách hàng"),
            ("top_customers", "Khách hàng VIP"),
            ("purchase_history", "Lịch sử mua hàng"),
            ("debt_customers", "Khách hàng nợ"),
            ("loyalty_analysis", "Phân tích trung thành"),
            ("new_customers", "Khách hàng mới")
        ]
        
        row = 0
        for i, (value, text) in enumerate(customer_report_types):
            col = i % 3
            if col == 0 and i > 0:
                row += 1
            
            ttk.Radiobutton(report_type_frame, text=text, variable=self.customer_report_type_var,
                           value=value).grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Date range for customer reports
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="Từ ngày:").pack(side=tk.LEFT)
        self.customer_from_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.customer_from_date_var, width=12)
        from_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Đến ngày:").pack(side=tk.LEFT, padx=(20, 0))
        self.customer_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.customer_to_date_var, width=12)
        to_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Report buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Tạo báo cáo", 
                  command=self.generate_customer_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In báo cáo", 
                  command=self.print_customer_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_customer_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📧 Gửi email", 
                  command=self.send_customer_email).pack(side=tk.LEFT, padx=5)
        
        # Report display
        self.customer_report_text = tk.Text(customer_reports_frame, wrap=tk.WORD, font=('Consolas', 10))
        customer_scrollbar = ttk.Scrollbar(customer_reports_frame, orient=tk.VERTICAL, command=self.customer_report_text.yview)
        self.customer_report_text.config(yscrollcommand=customer_scrollbar.set)
        
        self.customer_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        customer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
    
    def setup_performance_reports_tab(self):
        """Setup performance reports tab"""
        performance_reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_reports_frame, text="Báo Cáo Hiệu Suất")
        
        # Report controls
        controls_frame = ttk.LabelFrame(performance_reports_frame, text="Tùy chọn báo cáo", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Time period
        period_frame = ttk.Frame(controls_frame)
        period_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(period_frame, text="Kỳ báo cáo:").pack(side=tk.LEFT)
        self.performance_period_var = tk.StringVar(value="monthly")
        
        periods = [
            ("daily", "Hàng ngày"),
            ("weekly", "Hàng tuần"),
            ("monthly", "Hàng tháng"),
            ("quarterly", "Hàng quý"),
            ("yearly", "Hàng năm")
        ]
        
        for value, text in periods:
            ttk.Radiobutton(period_frame, text=text, variable=self.performance_period_var,
                           value=value).pack(side=tk.LEFT, padx=10)
        
        # Report type
        report_type_frame = ttk.Frame(controls_frame)
        report_type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(report_type_frame, text="Loại báo cáo:").pack(side=tk.LEFT)
        self.performance_report_type_var = tk.StringVar(value="overall")
        
        performance_report_types = [
            ("overall", "Tổng quan"),
            ("sales_performance", "Hiệu suất bán hàng"),
            ("repair_performance", "Hiệu suất sửa chữa"),
            ("staff_performance", "Hiệu suất nhân viên"),
            ("product_performance", "Hiệu suất sản phẩm"),
            ("trend_analysis", "Phân tích xu hướng")
        ]
        
        row = 0
        for i, (value, text) in enumerate(performance_report_types):
            col = i % 3
            if col == 0 and i > 0:
                row += 1
            
            ttk.Radiobutton(report_type_frame, text=text, variable=self.performance_report_type_var,
                           value=value).grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
        
        # Date range
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="Từ ngày:").pack(side=tk.LEFT)
        self.performance_from_date_var = tk.StringVar(value=date.today().replace(day=1).strftime('%Y-%m-%d'))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.performance_from_date_var, width=12)
        from_date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(date_frame, text="Đến ngày:").pack(side=tk.LEFT, padx=(20, 0))
        self.performance_to_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.performance_to_date_var, width=12)
        to_date_entry.pack(side=tk.LEFT, padx=5)
        
        # Report buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="📊 Tạo báo cáo", 
                  command=self.generate_performance_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🖨️ In báo cáo", 
                  command=self.print_performance_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Xuất Excel", 
                  command=self.export_performance_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📈 Dashboard", 
                  command=self.show_performance_dashboard).pack(side=tk.LEFT, padx=5)
        
        # Report display
        self.performance_report_text = tk.Text(performance_reports_frame, wrap=tk.WORD, font=('Consolas', 10))
        performance_scrollbar = ttk.Scrollbar(performance_reports_frame, orient=tk.VERTICAL, command=self.performance_report_text.yview)
        self.performance_report_text.config(yscrollcommand=performance_scrollbar.set)
        
        self.performance_report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        performance_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
    
    def load_data(self):
        """Load initial report data"""
        # Generate default reports
        self.generate_sales_report()
    
    def load_categories_combo(self, combo):
        """Load categories into combobox"""
        categories = self.db_manager.fetch_all("SELECT id, name FROM categories ORDER BY name")
        combo['values'] = ["Tất cả"] + [f"{c['id']} - {c['name']}" for c in categories]
        combo.set("Tất cả")
    
    def generate_sales_report(self):
        """Generate sales report"""
        from_date = self.sales_from_date_var.get()
        to_date = self.sales_to_date_var.get()
        report_type = self.sales_report_type_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoảng thời gian!")
            return
        
        # Clear previous report
        self.sales_report_text.delete('1.0', tk.END)
        
        try:
            if report_type == "summary":
                self.generate_sales_summary_report(from_date, to_date)
            elif report_type == "daily":
                self.generate_daily_sales_report(from_date, to_date)
            elif report_type == "by_product":
                self.generate_product_sales_report(from_date, to_date)
            elif report_type == "by_staff":
                self.generate_staff_sales_report(from_date, to_date)
            else:
                self.generate_sales_summary_report(from_date, to_date)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def generate_sales_summary_report(self, from_date, to_date):
        """Generate sales summary report"""
        # Get sales data
        sales_data = self.db_manager.fetch_one(
            """SELECT COUNT(*) as total_orders,
                      COALESCE(SUM(total_amount), 0) as total_revenue,
                      COALESCE(SUM(paid_amount), 0) as total_paid,
                      COALESCE(AVG(total_amount), 0) as avg_order_value
               FROM sales 
               WHERE DATE(sale_date) BETWEEN ? AND ?""",
            (from_date, to_date)
        )
        
        # Get sales by payment method
        payment_methods = self.db_manager.fetch_all(
            """SELECT payment_method, COUNT(*) as count, SUM(total_amount) as amount
               FROM sales 
               WHERE DATE(sale_date) BETWEEN ? AND ?
               GROUP BY payment_method
               ORDER BY amount DESC""",
            (from_date, to_date)
        )
        
        # Get top products
        top_products = self.db_manager.fetch_all(
            """SELECT p.name, COUNT(si.id) as quantity, SUM(si.total_price) as revenue
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               JOIN sales s ON si.sale_id = s.id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?
               GROUP BY p.id, p.name
               ORDER BY revenue DESC
               LIMIT 10""",
            (from_date, to_date)
        )
        
        # Generate report
        report = f"""
=== BÁO CÁO TỔNG HỢP BÁN HÀNG ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. TỔNG QUAN:
   - Tổng số đơn hàng: {sales_data['total_orders']:,}
   - Tổng doanh thu: {sales_data['total_revenue']:,.0f} VNĐ
   - Đã thu được: {sales_data['total_paid']:,.0f} VNĐ
   - Giá trị đơn hàng trung bình: {sales_data['avg_order_value']:,.0f} VNĐ
   - Tỷ lệ thu tiền: {(sales_data['total_paid']/sales_data['total_revenue']*100 if sales_data['total_revenue'] > 0 else 0):.1f}%

2. PHÂN TÍCH THEO HÌNH THỨC THANH TOÁN:
"""
        
        for method in payment_methods:
            method_name = {
                'cash': 'Tiền mặt',
                'card': 'Thẻ',
                'transfer': 'Chuyển khoản',
                'mixed': 'Hỗn hợp'
            }.get(method['payment_method'], method['payment_method'])
            
            report += f"   - {method_name}: {method['count']:,} đơn ({method['amount']:,.0f} VNĐ)\n"
        
        report += f"\n3. TOP 10 SẢN PHẨM BÁN CHẠY:\n"
        
        for i, product in enumerate(top_products, 1):
            report += f"   {i:2d}. {product['name']}: {product['quantity']:,} sp ({product['revenue']:,.0f} VNĐ)\n"
        
        # Calculate daily average
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
            daily_avg = sales_data['total_revenue'] / days if days > 0 else 0
            
            report += f"\n4. HIỆU SUẤT:\n"
            report += f"   - Số ngày báo cáo: {days} ngày\n"
            report += f"   - Doanh thu trung bình/ngày: {daily_avg:,.0f} VNĐ\n"
            report += f"   - Số đơn hàng trung bình/ngày: {sales_data['total_orders']/days:.1f} đơn\n"
            
        except:
            pass
        
        self.sales_report_text.insert('1.0', report.strip())
    
    def generate_daily_sales_report(self, from_date, to_date):
        """Generate daily sales report"""
        # Get daily sales data
        daily_sales = self.db_manager.fetch_all(
            """SELECT DATE(sale_date) as sale_date,
                      COUNT(*) as orders,
                      SUM(total_amount) as revenue,
                      AVG(total_amount) as avg_order
               FROM sales 
               WHERE DATE(sale_date) BETWEEN ? AND ?
               GROUP BY DATE(sale_date)
               ORDER BY sale_date""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO BÁN HÀNG THEO NGÀY ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Ngày":<12} {"Số đơn":<10} {"Doanh thu":<15} {"ĐH trung bình":<15}
{"-"*60}
"""
        
        total_orders = 0
        total_revenue = 0
        
        for day in daily_sales:
            report += f"{day['sale_date']:<12} {day['orders']:<10} {day['revenue']:>12,.0f} {day['avg_order']:>12,.0f}\n"
            total_orders += day['orders']
            total_revenue += day['revenue']
        
        report += f"{'-'*60}\n"
        report += f"{'TỔNG CỘNG':<12} {total_orders:<10} {total_revenue:>12,.0f}\n"
        
        self.sales_report_text.insert('1.0', report)
    
    def generate_product_sales_report(self, from_date, to_date):
        """Generate product sales report"""
        # Get product sales data
        product_sales = self.db_manager.fetch_all(
            """SELECT p.name, p.brand, c.name as category,
                      COUNT(si.id) as quantity,
                      SUM(si.total_price) as revenue,
                      AVG(si.unit_price) as avg_price
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               LEFT JOIN categories c ON p.category_id = c.id
               JOIN sales s ON si.sale_id = s.id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?
               GROUP BY p.id, p.name, p.brand, c.name
               ORDER BY revenue DESC""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO BÁN HÀNG THEO SẢN PHẨM ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Sản phẩm":<30} {"Danh mục":<15} {"SL bán":<10} {"Doanh thu":<15}
{"-"*80}
"""
        
        for product in product_sales:
            product_display = product['name'][:25]
            if product['brand']:
                product_display += f" ({product['brand'][:10]})"
            
            report += f"{product_display:<30} {(product['category'] or 'N/A'):<15} {product['quantity']:<10} {product['revenue']:>12,.0f}\n"
        
        self.sales_report_text.insert('1.0', report)
    
    def generate_staff_sales_report(self, from_date, to_date):
        """Generate staff sales report"""
        # Get staff sales data
        staff_sales = self.db_manager.fetch_all(
            """SELECT st.full_name,
                      COUNT(s.id) as orders,
                      SUM(s.total_amount) as revenue,
                      AVG(s.total_amount) as avg_order
               FROM sales s
               JOIN staff st ON s.staff_id = st.id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?
               GROUP BY st.id, st.full_name
               ORDER BY revenue DESC""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO BÁN HÀNG THEO NHÂN VIÊN ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Nhân viên":<25} {"Số đơn":<10} {"Doanh thu":<15} {"ĐH trung bình":<15}
{"-"*70}
"""
        
        for staff in staff_sales:
            # Calculate commission (assuming 2% commission rate)
            commission = staff['revenue'] * 0.02
            
            report += f"{staff['full_name']:<25} {staff['orders']:<10} {staff['revenue']:>12,.0f} {staff['avg_order']:>12,.0f}\n"
        
        self.sales_report_text.insert('1.0', report)
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        report_type = self.inventory_report_type_var.get()
        
        self.inventory_report_text.delete('1.0', tk.END)
        
        try:
            if report_type == "current_stock":
                self.generate_current_stock_report()
            elif report_type == "low_stock":
                self.generate_low_stock_report()
            elif report_type == "stock_movement":
                self.generate_stock_movement_report()
            else:
                self.generate_current_stock_report()
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def generate_current_stock_report(self):
        """Generate current stock report"""
        # Get current stock data
        stock_data = self.db_manager.fetch_all(
            """SELECT p.name, p.brand, c.name as category,
                      COUNT(i.id) as total_stock,
                      COUNT(CASE WHEN i.status = 'available' THEN 1 END) as available_stock,
                      SUM(CASE WHEN i.status = 'available' THEN i.cost_price ELSE 0 END) as total_cost,
                      SUM(CASE WHEN i.status = 'available' THEN i.selling_price ELSE 0 END) as total_value
               FROM products p
               LEFT JOIN inventory i ON p.id = i.product_id
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.is_active = 1
               GROUP BY p.id, p.name, p.brand, c.name
               ORDER BY available_stock DESC"""
        )
        
        report = f"""
=== BÁO CÁO TỒN KHO HIỆN TẠI ===
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Sản phẩm":<30} {"Danh mục":<15} {"Tồn kho":<10} {"Có sẵn":<10} {"Giá trị":<15}
{"-"*90}
"""
        
        total_cost = 0
        total_value = 0
        total_items = 0
        
        for item in stock_data:
            product_display = item['name'][:25]
            if item['brand']:
                product_display += f" ({item['brand'][:8]})"
            
            cost = item['total_cost'] or 0
            value = item['total_value'] or 0
            available = item['available_stock'] or 0
            
            total_cost += cost
            total_value += value
            total_items += available
            
            report += f"{product_display:<30} {(item['category'] or 'N/A')[:14]:<15} {item['total_stock'] or 0:<10} {available:<10} {value:>12,.0f}\n"
        
        report += f"{'-'*90}\n"
        report += f"TỔNG CỘNG: {total_items} sản phẩm - Giá vốn: {total_cost:,.0f} VNĐ - Giá trị: {total_value:,.0f} VNĐ\n"
        report += f"Lợi nhuận tiềm năng: {total_value - total_cost:,.0f} VNĐ ({((total_value - total_cost)/total_cost*100 if total_cost > 0 else 0):.1f}%)\n"
        
        self.inventory_report_text.insert('1.0', report)
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        threshold = BUSINESS_RULES['LOW_STOCK_THRESHOLD']
        
        low_stock_items = self.db_manager.fetch_all(
            """SELECT p.name, p.brand, c.name as category,
                      COUNT(CASE WHEN i.status = 'available' THEN 1 END) as available_stock
               FROM products p
               LEFT JOIN inventory i ON p.id = i.product_id
               LEFT JOIN categories c ON p.category_id = c.id
               WHERE p.is_active = 1
               GROUP BY p.id, p.name, p.brand, c.name
               HAVING available_stock <= ?
               ORDER BY available_stock ASC""",
            (threshold,)
        )
        
        report = f"""
=== BÁO CÁO SẢN PHẨM SẮP HẾT HÀNG ===
Ngưỡng cảnh báo: {threshold} sản phẩm
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Sản phẩm":<40} {"Danh mục":<15} {"Tồn kho":<10} {"Mức độ":<15}
{"-"*90}
"""
        
        for item in low_stock_items:
            product_display = item['name'][:35]
            if item['brand']:
                product_display += f" ({item['brand'][:8]})"
            
            stock = item['available_stock'] or 0
            
            if stock == 0:
                urgency = "🔴 HẾT HÀNG"
            elif stock <= threshold // 2:
                urgency = "🟠 RẤT ÍT"
            else:
                urgency = "🟡 SẮP HẾT"
            
            report += f"{product_display:<40} {(item['category'] or 'N/A')[:14]:<15} {stock:<10} {urgency:<15}\n"
        
        if not low_stock_items:
            report += "\n✅ Không có sản phẩm nào sắp hết hàng!\n"
        
        self.inventory_report_text.insert('1.0', report)
    
    def generate_stock_movement_report(self):
        """Generate stock movement report"""
        # This would require a stock_movements table to track all inventory changes
        report = f"""
=== BÁO CÁO XUẤT NHẬP TỒN ===
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Báo cáo xuất nhập tồn chi tiết sẽ được phát triển khi có bảng theo dõi
chuyển động kho hàng (stock_movements).

Sẽ bao gồm:
- Nhập kho theo ngày
- Xuất kho (bán hàng, sửa chữa)
- Chuyển kho
- Kiểm kê kho
- Điều chỉnh tồn kho
        """
        
        self.inventory_report_text.insert('1.0', report)
    
    def generate_financial_report(self):
        """Generate financial report"""
        from_date = self.financial_from_date_var.get()
        to_date = self.financial_to_date_var.get()
        report_type = self.financial_report_type_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoảng thời gian!")
            return
        
        self.financial_report_text.delete('1.0', tk.END)
        
        try:
            if report_type == "profit_loss":
                self.generate_profit_loss_report(from_date, to_date)
            elif report_type == "cash_flow":
                self.generate_cash_flow_report(from_date, to_date)
            elif report_type == "revenue_analysis":
                self.generate_revenue_analysis(from_date, to_date)
            else:
                self.generate_profit_loss_report(from_date, to_date)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def generate_profit_loss_report(self, from_date, to_date):
        """Generate profit and loss report"""
        # Get revenue data
        revenue_data = self.db_manager.fetch_one(
            """SELECT COALESCE(SUM(amount), 0) as total_revenue
               FROM transactions 
               WHERE transaction_type = 'income' AND DATE(transaction_date) BETWEEN ? AND ?""",
            (from_date, to_date)
        )
        
        # Get expense data
        expense_data = self.db_manager.fetch_one(
            """SELECT COALESCE(SUM(amount), 0) as total_expenses
               FROM transactions 
               WHERE transaction_type = 'expense' AND DATE(transaction_date) BETWEEN ? AND ?""",
            (from_date, to_date)
        )
        
        # Get detailed expense breakdown
        expense_breakdown = self.db_manager.fetch_all(
            """SELECT description, SUM(amount) as amount
               FROM transactions 
               WHERE transaction_type = 'expense' AND DATE(transaction_date) BETWEEN ? AND ?
               GROUP BY description
               ORDER BY amount DESC""",
            (from_date, to_date)
        )
        
        total_revenue = revenue_data['total_revenue']
        total_expenses = expense_data['total_expenses']
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        report = f"""
=== BÁO CÁO LÃI LỖ ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. DOANH THU:
   Tổng doanh thu: {total_revenue:>20,.0f} VNĐ

2. CHI PHÍ:
   Tổng chi phí: {total_expenses:>22,.0f} VNĐ
   
   Chi tiết chi phí:
"""
        
        for expense in expense_breakdown:
            report += f"   - {expense['description'][:30]:<30}: {expense['amount']:>15,.0f} VNĐ\n"
        
        report += f"""
3. KẾT QUẢ KINH DOANH:
   Lợi nhuận ròng: {net_profit:>19,.0f} VNĐ
   Tỷ suất lợi nhuận: {profit_margin:>17.1f}%
   
4. ĐÁNH GIÁ:
"""
        
        if net_profit > 0:
            report += "   ✅ Kinh doanh có lãi\n"
        elif net_profit == 0:
            report += "   ⚠️ Hòa vốn\n"
        else:
            report += "   ❌ Kinh doanh thua lỗ\n"
        
        self.financial_report_text.insert('1.0', report)
    
    def generate_cash_flow_report(self, from_date, to_date):
        """Generate cash flow report"""
        # Get daily cash flow
        daily_flow = self.db_manager.fetch_all(
            """SELECT DATE(transaction_date) as date,
                      SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as inflow,
                      SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as outflow
               FROM transactions 
               WHERE DATE(transaction_date) BETWEEN ? AND ?
               GROUP BY DATE(transaction_date)
               ORDER BY date""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO DÒNG TIỀN ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Ngày":<12} {"Tiền vào":<15} {"Tiền ra":<15} {"Dòng tiền ròng":<15}
{"-"*70}
"""
        
        total_inflow = 0
        total_outflow = 0
        
        for day in daily_flow:
            net_flow = day['inflow'] - day['outflow']
            total_inflow += day['inflow']
            total_outflow += day['outflow']
            
            report += f"{day['date']:<12} {day['inflow']:>12,.0f} {day['outflow']:>12,.0f} {net_flow:>12,.0f}\n"
        
        net_total = total_inflow - total_outflow
        
        report += f"{'-'*70}\n"
        report += f"{'TỔNG CỘNG':<12} {total_inflow:>12,.0f} {total_outflow:>12,.0f} {net_total:>12,.0f}\n"
        
        self.financial_report_text.insert('1.0', report)
    
    def generate_revenue_analysis(self, from_date, to_date):
        """Generate revenue analysis report"""
        # Revenue by source
        revenue_sources = self.db_manager.fetch_all(
            """SELECT reference_type, SUM(amount) as amount
               FROM transactions 
               WHERE transaction_type = 'income' AND DATE(transaction_date) BETWEEN ? AND ?
               GROUP BY reference_type
               ORDER BY amount DESC""",
            (from_date, to_date)
        )
        
        report = f"""
=== PHÂN TÍCH DOANH THU ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. DOANH THU THEO NGUỒN:
"""
        
        total_revenue = sum(source['amount'] for source in revenue_sources)
        
        source_names = {
            'sale': 'Bán hàng',
            'repair': 'Sửa chữa',
            'pawn_interest': 'Lãi cầm đồ',
            'other': 'Khác'
        }
        
        for source in revenue_sources:
            source_name = source_names.get(source['reference_type'], source['reference_type'] or 'Không xác định')
            percentage = (source['amount'] / total_revenue * 100) if total_revenue > 0 else 0
            
            report += f"   - {source_name:<20}: {source['amount']:>15,.0f} VNĐ ({percentage:>5.1f}%)\n"
        
        report += f"\nTổng doanh thu: {total_revenue:,.0f} VNĐ\n"
        
        self.financial_report_text.insert('1.0', report)
    
    def generate_customer_report(self):
        """Generate customer report"""
        report_type = self.customer_report_type_var.get()
        from_date = self.customer_from_date_var.get()
        to_date = self.customer_to_date_var.get()
        
        self.customer_report_text.delete('1.0', tk.END)
        
        try:
            if report_type == "customer_list":
                self.generate_customer_list_report()
            elif report_type == "top_customers":
                self.generate_top_customers_report(from_date, to_date)
            elif report_type == "debt_customers":
                self.generate_debt_customers_report()
            else:
                self.generate_customer_list_report()
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def generate_customer_list_report(self):
        """Generate customer list report"""
        customers = self.db_manager.fetch_all(
            """SELECT c.*,
                      COUNT(s.id) as total_orders,
                      COALESCE(SUM(s.total_amount), 0) as total_spent
               FROM customers c
               LEFT JOIN sales s ON c.id = s.customer_id
               GROUP BY c.id
               ORDER BY total_spent DESC"""
        )
        
        report = f"""
=== DANH SÁCH KHÁCH HÀNG ===
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Tổng số khách hàng: {len(customers)}

{"Tên khách hàng":<25} {"Điện thoại":<15} {"Số đơn":<10} {"Tổng mua":<15}
{"-"*75}
"""
        
        for customer in customers:
            report += f"{customer['name'][:24]:<25} {(customer['phone'] or 'N/A')[:14]:<15} {customer['total_orders']:<10} {customer['total_spent']:>12,.0f}\n"
        
        self.customer_report_text.insert('1.0', report)
    
    def generate_top_customers_report(self, from_date, to_date):
        """Generate top customers report"""
        top_customers = self.db_manager.fetch_all(
            """SELECT c.name, c.phone,
                      COUNT(s.id) as orders,
                      SUM(s.total_amount) as total_spent,
                      AVG(s.total_amount) as avg_order
               FROM customers c
               JOIN sales s ON c.id = s.customer_id
               WHERE DATE(s.sale_date) BETWEEN ? AND ?
               GROUP BY c.id, c.name, c.phone
               ORDER BY total_spent DESC
               LIMIT 20""",
            (from_date, to_date)
        )
        
        report = f"""
=== TOP 20 KHÁCH HÀNG VIP ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"#":<3} {"Tên khách hàng":<25} {"Số đơn":<10} {"Tổng mua":<15} {"ĐH trung bình":<15}
{"-"*80}
"""
        
        for i, customer in enumerate(top_customers, 1):
            report += f"{i:<3} {customer['name'][:24]:<25} {customer['orders']:<10} {customer['total_spent']:>12,.0f} {customer['avg_order']:>12,.0f}\n"
        
        self.customer_report_text.insert('1.0', report)
    
    def generate_debt_customers_report(self):
        """Generate customers with debt report"""
        debt_customers = self.db_manager.fetch_all(
            """SELECT c.name, c.phone, SUM(d.amount) as total_debt
               FROM customers c
               JOIN debts d ON c.id = d.debtor_id
               WHERE d.debtor_type = 'customer' AND d.status = 'outstanding'
               GROUP BY c.id, c.name, c.phone
               ORDER BY total_debt DESC"""
        )
        
        report = f"""
=== KHÁCH HÀNG CÓ CÔNG NỢ ===
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Tên khách hàng":<25} {"Điện thoại":<15} {"Số nợ":<15}
{"-"*65}
"""
        
        total_debt = 0
        
        for customer in debt_customers:
            total_debt += customer['total_debt']
            report += f"{customer['name'][:24]:<25} {(customer['phone'] or 'N/A')[:14]:<15} {customer['total_debt']:>12,.0f}\n"
        
        report += f"{'-'*65}\n"
        report += f"TỔNG CÔNG NỢ: {total_debt:,.0f} VNĐ\n"
        
        if not debt_customers:
            report += "\n✅ Không có khách hàng nào đang nợ!\n"
        
        self.customer_report_text.insert('1.0', report)
    
    def generate_performance_report(self):
        """Generate performance report"""
        from_date = self.performance_from_date_var.get()
        to_date = self.performance_to_date_var.get()
        report_type = self.performance_report_type_var.get()
        
        if not from_date or not to_date:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khoảng thời gian!")
            return
        
        self.performance_report_text.delete('1.0', tk.END)
        
        try:
            if report_type == "overall":
                self.generate_overall_performance_report(from_date, to_date)
            elif report_type == "sales_performance":
                self.generate_sales_performance_report(from_date, to_date)
            elif report_type == "staff_performance":
                self.generate_staff_performance_report(from_date, to_date)
            else:
                self.generate_overall_performance_report(from_date, to_date)
                
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo báo cáo: {e}")
    
    def generate_overall_performance_report(self, from_date, to_date):
        """Generate overall performance report"""
        # Key metrics
        sales_metrics = self.db_manager.fetch_one(
            """SELECT COUNT(*) as orders, SUM(total_amount) as revenue
               FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?""",
            (from_date, to_date)
        )
        
        repairs_metrics = self.db_manager.fetch_one(
            """SELECT COUNT(*) as repairs, SUM(total_cost) as repair_revenue
               FROM repairs WHERE DATE(created_at) BETWEEN ? AND ?""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO HIỆU SUẤT TỔNG QUAN ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

1. HIỆU SUẤT BÁN HÀNG:
   - Số đơn hàng: {sales_metrics['orders']:,}
   - Doanh thu: {sales_metrics['revenue']:,.0f} VNĐ
   - Đơn hàng trung bình: {(sales_metrics['revenue']/sales_metrics['orders'] if sales_metrics['orders'] > 0 else 0):,.0f} VNĐ

2. HIỆU SUẤT SỬA CHỮA:
   - Số lượng sửa chữa: {repairs_metrics['repairs']:,}
   - Doanh thu sửa chữa: {(repairs_metrics['repair_revenue'] or 0):,.0f} VNĐ

3. TỔNG KẾT:
   - Tổng doanh thu: {sales_metrics['revenue'] + (repairs_metrics['repair_revenue'] or 0):,.0f} VNĐ
   - Hiệu suất tổng thể: Đạt mục tiêu (cần thiết lập KPI)
        """
        
        self.performance_report_text.insert('1.0', report)
    
    def generate_sales_performance_report(self, from_date, to_date):
        """Generate sales performance report"""
        # Sales by time periods
        daily_sales = self.db_manager.fetch_all(
            """SELECT DATE(sale_date) as date, COUNT(*) as orders, SUM(total_amount) as revenue
               FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?
               GROUP BY DATE(sale_date) ORDER BY date""",
            (from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO HIỆU SUẤT BÁN HÀNG ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

HIỆU SUẤT THEO NGÀY:
{"Ngày":<12} {"Đơn hàng":<10} {"Doanh thu":<15} {"Hiệu suất":<12}
{"-"*55}
"""
        
        total_orders = sum(day['orders'] for day in daily_sales)
        total_revenue = sum(day['revenue'] for day in daily_sales)
        avg_daily_revenue = total_revenue / len(daily_sales) if daily_sales else 0
        
        for day in daily_sales:
            performance = "Tốt" if day['revenue'] >= avg_daily_revenue else "Trung bình"
            report += f"{day['date']:<12} {day['orders']:<10} {day['revenue']:>12,.0f} {performance:<12}\n"
        
        report += f"\nTổng kết: {total_orders} đơn hàng, {total_revenue:,.0f} VNĐ\n"
        
        self.performance_report_text.insert('1.0', report)
    
    def generate_staff_performance_report(self, from_date, to_date):
        """Generate staff performance report"""
        # Staff performance metrics
        staff_performance = self.db_manager.fetch_all(
            """SELECT st.full_name,
                      COUNT(s.id) as sales_count,
                      SUM(s.total_amount) as sales_revenue,
                      COUNT(r.id) as repairs_count
               FROM staff st
               LEFT JOIN sales s ON st.id = s.staff_id AND DATE(s.sale_date) BETWEEN ? AND ?
               LEFT JOIN repairs r ON st.id = r.staff_id AND DATE(r.created_at) BETWEEN ? AND ?
               WHERE st.is_active = 1
               GROUP BY st.id, st.full_name
               ORDER BY sales_revenue DESC""",
            (from_date, to_date, from_date, to_date)
        )
        
        report = f"""
=== BÁO CÁO HIỆU SUẤT NHÂN VIÊN ===
Từ ngày: {from_date} đến ngày: {to_date}
Thời gian tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{"Nhân viên":<20} {"Bán hàng":<10} {"Doanh thu":<15} {"Sửa chữa":<10} {"Xếp hạng":<10}
{"-"*75}
"""
        
        for i, staff in enumerate(staff_performance, 1):
            ranking = f"#{i}"
            report += f"{staff['full_name'][:19]:<20} {staff['sales_count'] or 0:<10} {(staff['sales_revenue'] or 0):>12,.0f} {staff['repairs_count'] or 0:<10} {ranking:<10}\n"
        
        self.performance_report_text.insert('1.0', report)
    
    # Print and export functions
    def print_sales_report(self):
        """Print sales report"""
        try:
            from utils.print_utils import print_text_report
            report_content = self.sales_report_text.get('1.0', tk.END)
            print_text_report("Báo cáo bán hàng", report_content)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in báo cáo: {e}")
    
    def export_sales_excel(self):
        """Export sales report to Excel"""
        try:
            from utils.excel_utils import export_sales_report
            from_date = self.sales_from_date_var.get()
            to_date = self.sales_to_date_var.get()
            export_sales_report(self.db_manager, from_date, to_date)
            messagebox.showinfo("Thành công", "Đã xuất báo cáo ra Excel!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất Excel: {e}")
    
    def show_sales_chart(self):
        """Show sales chart"""
        messagebox.showinfo("Thông báo", "Chức năng biểu đồ bán hàng sẽ được phát triển!")
    
    def print_inventory_report(self):
        """Print inventory report"""
        try:
            from utils.print_utils import print_text_report
            report_content = self.inventory_report_text.get('1.0', tk.END)
            print_text_report("Báo cáo kho hàng", report_content)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in báo cáo: {e}")
    
    def export_inventory_excel(self):
        """Export inventory report to Excel"""
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel báo cáo kho hàng sẽ được phát triển!")
    
    def show_stock_alerts(self):
        """Show stock alerts"""
        messagebox.showinfo("Thông báo", "Chức năng cảnh báo hết hàng sẽ được phát triển!")
    
    def print_financial_report(self):
        """Print financial report"""
        try:
            from utils.print_utils import print_text_report
            report_content = self.financial_report_text.get('1.0', tk.END)
            print_text_report("Báo cáo tài chính", report_content)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in báo cáo: {e}")
    
    def export_financial_excel(self):
        """Export financial report to Excel"""
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel báo cáo tài chính sẽ được phát triển!")
    
    def show_financial_chart(self):
        """Show financial chart"""
        messagebox.showinfo("Thông báo", "Chức năng biểu đồ tài chính sẽ được phát triển!")
    
    def print_customer_report(self):
        """Print customer report"""
        try:
            from utils.print_utils import print_text_report
            report_content = self.customer_report_text.get('1.0', tk.END)
            print_text_report("Báo cáo khách hàng", report_content)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in báo cáo: {e}")
    
    def export_customer_excel(self):
        """Export customer report to Excel"""
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel báo cáo khách hàng sẽ được phát triển!")
    
    def send_customer_email(self):
        """Send customer email"""
        messagebox.showinfo("Thông báo", "Chức năng gửi email khách hàng sẽ được phát triển!")
    
    def print_performance_report(self):
        """Print performance report"""
        try:
            from utils.print_utils import print_text_report
            report_content = self.performance_report_text.get('1.0', tk.END)
            print_text_report("Báo cáo hiệu suất", report_content)
        except Exception as e:
            messagebox.showerror("Lỗi in", f"Không thể in báo cáo: {e}")
    
    def export_performance_excel(self):
        """Export performance report to Excel"""
        messagebox.showinfo("Thông báo", "Chức năng xuất Excel báo cáo hiệu suất sẽ được phát triển!")
    
    def show_performance_dashboard(self):
        """Show performance dashboard"""
        messagebox.showinfo("Thông báo", "Chức năng dashboard hiệu suất sẽ được phát triển!")
