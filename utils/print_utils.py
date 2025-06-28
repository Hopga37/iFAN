#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Print utility functions for ChViet Mobile Store Management System
"""

from datetime import datetime
import os

def print_report(content, title="Báo cáo", print_date=True):
    """
    Print report content
    
    Args:
        content: Report content to print
        title: Report title
        print_date: Whether to include print date
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n{title}")
        print("=" * 50)
        
        if print_date:
            print(f"Ngày in: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("-" * 50)
        
        print(content)
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"Lỗi in báo cáo: {e}")
        return False

def save_report_to_file(content, filename, title="Báo cáo"):
    """
    Save report content to file
    
    Args:
        content: Report content
        filename: Output filename
        title: Report title
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure reports directory exists
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("-" * 50 + "\n")
            f.write(content)
            f.write("\n" + "=" * 50)
        
        return True
        
    except Exception as e:
        print(f"Lỗi lưu báo cáo: {e}")
        return False

def format_report_header(title, company_name="ChViet Mobile Store"):
    """
    Format standard report header
    
    Args:
        title: Report title
        company_name: Company name
    
    Returns:
        str: Formatted header
    """
    header = f"""
{company_name}
{'='*60}
{title.upper()}
Ngày báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
{'='*60}
"""
    return header

def format_report_footer():
    """
    Format standard report footer
    
    Returns:
        str: Formatted footer
    """
    footer = f"""
{'='*60}
Báo cáo được tạo bởi hệ thống ChViet
Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
    return footer

def print_invoice(invoice_data):
    """
    Print invoice/receipt
    
    Args:
        invoice_data: Dictionary containing invoice information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("\n" + "="*40)
        print("        ChViet Mobile Store")
        print("      HÓA ĐƠN BÁN HÀNG")
        print("="*40)
        
        # Invoice header
        print(f"Số HĐ: {invoice_data.get('invoice_number', 'N/A')}")
        print(f"Ngày: {invoice_data.get('date', datetime.now().strftime('%d/%m/%Y %H:%M'))}")
        print(f"Khách hàng: {invoice_data.get('customer_name', 'Khách lẻ')}")
        if invoice_data.get('customer_phone'):
            print(f"SĐT: {invoice_data['customer_phone']}")
        print("-"*40)
        
        # Items
        print(f"{'Sản phẩm':<20} {'SL':<5} {'Đơn giá':<10} {'Thành tiền':<10}")
        print("-"*40)
        
        total = 0
        for item in invoice_data.get('items', []):
            name = item.get('name', '')[:18]
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            subtotal = qty * price
            total += subtotal
            
            print(f"{name:<20} {qty:<5} {price:<10,.0f} {subtotal:<10,.0f}")
        
        print("-"*40)
        print(f"{'Tổng cộng:':<30} {total:>9,.0f}")
        
        if invoice_data.get('discount', 0) > 0:
            discount = invoice_data['discount']
            print(f"{'Giảm giá:':<30} {discount:>9,.0f}")
            total -= discount
        
        if invoice_data.get('tax', 0) > 0:
            tax = invoice_data['tax']
            print(f"{'Thuế VAT:':<30} {tax:>9,.0f}")
            total += tax
        
        print("="*40)
        print(f"{'THÀNH TIỀN:':<30} {total:>9,.0f}")
        print("="*40)
        
        print("\nCảm ơn quý khách!")
        print("Hẹn gặp lại!")
        
        return True
        
    except Exception as e:
        print(f"Lỗi in hóa đơn: {e}")
        return False

def print_text_report(content, title="Báo cáo"):
    """
    Print text report content
    
    Args:
        content: Report content to print
        title: Report title
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n{title}")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return True
    except Exception as e:
        print(f"Lỗi in báo cáo: {e}")
        return False

def print_receipt(receipt_data, receipt_type="receipt"):
    """
    Print receipt (repair, pawn, etc.)
    
    Args:
        receipt_data: Dictionary containing receipt information
        receipt_type: Type of receipt (repair, pawn, payment)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("\n" + "="*40)
        print("        ChViet Mobile Store")
        
        if receipt_type == "repair":
            print("       BIÊN NHẬN SỬA CHỮA")
        elif receipt_type == "pawn":
            print("       HỢP ĐỒNG CẦM ĐỒ")
        elif receipt_type == "payment":
            print("         BIÊN LAI THU TIỀN")
        else:
            print("           BIÊN NHẬN")
        
        print("="*40)
        
        # Common fields
        print(f"Số: {receipt_data.get('number', 'N/A')}")
        print(f"Ngày: {receipt_data.get('date', datetime.now().strftime('%d/%m/%Y %H:%M'))}")
        print(f"Khách hàng: {receipt_data.get('customer_name', 'N/A')}")
        if receipt_data.get('customer_phone'):
            print(f"SĐT: {receipt_data['customer_phone']}")
        print("-"*40)
        
        # Specific content based on type
        if receipt_type == "repair":
            print(f"Thiết bị: {receipt_data.get('device', 'N/A')}")
            if receipt_data.get('imei'):
                print(f"IMEI: {receipt_data['imei']}")
            print(f"Lỗi: {receipt_data.get('problem', 'N/A')}")
            print(f"Chi phí: {receipt_data.get('cost', 0):,.0f} VNĐ")
            if receipt_data.get('completion_date'):
                print(f"Dự kiến xong: {receipt_data['completion_date']}")
                
        elif receipt_type == "pawn":
            print(f"Tài sản: {receipt_data.get('item', 'N/A')}")
            print(f"Giá trị: {receipt_data.get('value', 0):,.0f} VNĐ")
            print(f"Số vay: {receipt_data.get('loan', 0):,.0f} VNĐ")
            print(f"Lãi suất: {receipt_data.get('interest_rate', 0)}%/tháng")
            if receipt_data.get('due_date'):
                print(f"Đáo hạn: {receipt_data['due_date']}")
                
        elif receipt_type == "payment":
            print(f"Số tiền: {receipt_data.get('amount', 0):,.0f} VNĐ")
            print(f"Loại: {receipt_data.get('type', 'N/A')}")
            print(f"Ghi chú: {receipt_data.get('description', '')}")
        
        print("="*40)
        print("Cảm ơn quý khách!")
        
        return True
        
    except Exception as e:
        print(f"Lỗi in biên nhận: {e}")
        return False