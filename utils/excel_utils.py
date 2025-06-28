#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel utility functions for ChViet Mobile Store Management System
"""

import csv
import os
from datetime import datetime

def export_to_csv(data, filename, headers=None):
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries or list of lists
        filename: Output filename
        headers: Optional headers list
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure reports directory exists
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if not data:
                return True
            
            if isinstance(data[0], dict):
                # Data is list of dictionaries
                fieldnames = headers or list(data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                # Data is list of lists
                writer = csv.writer(csvfile)
                if headers:
                    writer.writerow(headers)
                writer.writerows(data)
        
        return True
        
    except Exception as e:
        print(f"Lỗi xuất CSV: {e}")
        return False

def format_sales_data_for_export(sales_data):
    """
    Format sales data for CSV export
    
    Args:
        sales_data: Raw sales data from database
    
    Returns:
        tuple: (formatted_data, headers)
    """
    headers = [
        'Số HĐ', 'Ngày', 'Khách hàng', 'Nhân viên',
        'Tổng tiền', 'Đã thanh toán', 'Hình thức TT', 'Trạng thái'
    ]
    
    formatted_data = []
    for sale in sales_data:
        formatted_data.append([
            sale.get('invoice_number', ''),
            sale.get('sale_date', ''),
            sale.get('customer_name', 'Khách lẻ'),
            sale.get('staff_name', ''),
            f"{sale.get('total_amount', 0):,.0f}",
            f"{sale.get('paid_amount', 0):,.0f}",
            sale.get('payment_method', ''),
            sale.get('payment_status', '')
        ])
    
    return formatted_data, headers

def format_inventory_data_for_export(inventory_data):
    """
    Format inventory data for CSV export
    
    Args:
        inventory_data: Raw inventory data from database
    
    Returns:
        tuple: (formatted_data, headers)
    """
    headers = [
        'Sản phẩm', 'Thương hiệu', 'Mẫu mã', 'IMEI',
        'Serial', 'Tình trạng', 'Trạng thái', 'Giá nhập',
        'Giá bán', 'Vị trí'
    ]
    
    formatted_data = []
    for item in inventory_data:
        formatted_data.append([
            item.get('product_name', ''),
            item.get('brand', ''),
            item.get('model', ''),
            item.get('imei', ''),
            item.get('serial_number', ''),
            item.get('condition', ''),
            item.get('status', ''),
            f"{item.get('cost_price', 0):,.0f}",
            f"{item.get('selling_price', 0):,.0f}",
            item.get('location', '')
        ])
    
    return formatted_data, headers

def format_financial_data_for_export(financial_data):
    """
    Format financial data for CSV export
    
    Args:
        financial_data: Raw financial data from database
    
    Returns:
        tuple: (formatted_data, headers)
    """
    headers = [
        'Ngày', 'Loại', 'Số tiền', 'Mô tả',
        'Hình thức TT', 'Tham chiếu', 'Nhân viên'
    ]
    
    formatted_data = []
    for transaction in financial_data:
        formatted_data.append([
            transaction.get('transaction_date', ''),
            'Thu' if transaction.get('transaction_type') == 'income' else 'Chi',
            f"{transaction.get('amount', 0):,.0f}",
            transaction.get('description', ''),
            transaction.get('payment_method', ''),
            transaction.get('reference_type', ''),
            transaction.get('staff_name', '')
        ])
    
    return formatted_data, headers

def format_customer_data_for_export(customer_data):
    """
    Format customer data for CSV export
    
    Args:
        customer_data: Raw customer data from database
    
    Returns:
        tuple: (formatted_data, headers)
    """
    headers = [
        'Tên khách hàng', 'Điện thoại', 'Email', 'Địa chỉ',
        'CMND/CCCD', 'Ngày sinh', 'Tổng mua hàng', 'Công nợ'
    ]
    
    formatted_data = []
    for customer in customer_data:
        formatted_data.append([
            customer.get('name', ''),
            customer.get('phone', ''),
            customer.get('email', ''),
            customer.get('address', ''),
            customer.get('id_number', ''),
            customer.get('birth_date', ''),
            f"{customer.get('total_purchases', 0):,.0f}",
            f"{customer.get('debt', 0):,.0f}"
        ])
    
    return formatted_data, headers

def export_sales_report(sales_data, filename=None):
    """
    Export sales report to CSV
    
    Args:
        sales_data: Sales data to export
        filename: Optional filename, auto-generated if not provided
    
    Returns:
        str: Filepath if successful, None if failed
    """
    try:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bao_cao_ban_hang_{timestamp}.csv"
        
        formatted_data, headers = format_sales_data_for_export(sales_data)
        
        if export_to_csv(formatted_data, filename, headers):
            return os.path.join("reports", filename)
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi xuất báo cáo bán hàng: {e}")
        return None

def export_inventory_report(inventory_data, filename=None):
    """
    Export inventory report to CSV
    
    Args:
        inventory_data: Inventory data to export
        filename: Optional filename, auto-generated if not provided
    
    Returns:
        str: Filepath if successful, None if failed
    """
    try:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bao_cao_kho_hang_{timestamp}.csv"
        
        formatted_data, headers = format_inventory_data_for_export(inventory_data)
        
        if export_to_csv(formatted_data, filename, headers):
            return os.path.join("reports", filename)
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi xuất báo cáo kho hàng: {e}")
        return None

def export_financial_report(financial_data, filename=None):
    """
    Export financial report to CSV
    
    Args:
        financial_data: Financial data to export
        filename: Optional filename, auto-generated if not provided
    
    Returns:
        str: Filepath if successful, None if failed
    """
    try:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bao_cao_tai_chinh_{timestamp}.csv"
        
        formatted_data, headers = format_financial_data_for_export(financial_data)
        
        if export_to_csv(formatted_data, filename, headers):
            return os.path.join("reports", filename)
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi xuất báo cáo tài chính: {e}")
        return None

def export_customer_report(customer_data, filename=None):
    """
    Export customer report to CSV
    
    Args:
        customer_data: Customer data to export
        filename: Optional filename, auto-generated if not provided
    
    Returns:
        str: Filepath if successful, None if failed
    """
    try:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bao_cao_khach_hang_{timestamp}.csv"
        
        formatted_data, headers = format_customer_data_for_export(customer_data)
        
        if export_to_csv(formatted_data, filename, headers):
            return os.path.join("reports", filename)
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi xuất báo cáo khách hàng: {e}")
        return None

def create_backup_csv(table_name, data):
    """
    Create backup CSV for a database table
    
    Args:
        table_name: Name of the table
        data: Table data
    
    Returns:
        str: Backup filepath if successful, None if failed
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{table_name}_{timestamp}.csv"
        
        if export_to_csv(data, filename):
            return os.path.join("reports", filename)
        else:
            return None
            
    except Exception as e:
        print(f"Lỗi tạo backup CSV: {e}")
        return None