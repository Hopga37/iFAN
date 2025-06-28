#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Currency utility functions for ChViet Mobile Store Management System
"""

import locale
from decimal import Decimal, ROUND_HALF_UP

def format_currency(amount, currency="VNĐ", show_symbol=True):
    """
    Format amount as Vietnamese currency
    
    Args:
        amount: Amount to format
        currency: Currency symbol (default: VNĐ)
        show_symbol: Whether to show currency symbol
    
    Returns:
        str: Formatted currency string
    """
    try:
        if amount is None:
            amount = 0
        
        # Convert to decimal for precise calculation
        decimal_amount = Decimal(str(amount))
        
        # Round to nearest whole number (Vietnamese dong doesn't use decimals)
        rounded_amount = decimal_amount.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
        # Format with thousand separators
        formatted = "{:,.0f}".format(float(rounded_amount))
        
        if show_symbol:
            return f"{formatted} {currency}"
        else:
            return formatted
            
    except (ValueError, TypeError):
        return "0 VNĐ" if show_symbol else "0"

def parse_currency(currency_string):
    """
    Parse currency string to numeric value
    
    Args:
        currency_string: Currency string to parse
    
    Returns:
        float: Numeric value
    """
    try:
        if not currency_string:
            return 0.0
        
        # Remove currency symbols and spaces
        cleaned = str(currency_string).replace("VNĐ", "").replace("đ", "").replace(",", "").strip()
        
        # Handle empty string
        if not cleaned:
            return 0.0
        
        return float(cleaned)
        
    except (ValueError, TypeError):
        return 0.0

def calculate_vat(amount, vat_rate=0.1):
    """
    Calculate VAT amount
    
    Args:
        amount: Base amount
        vat_rate: VAT rate (default: 10% = 0.1)
    
    Returns:
        tuple: (vat_amount, total_with_vat)
    """
    try:
        base_amount = Decimal(str(amount))
        vat_amount = base_amount * Decimal(str(vat_rate))
        total_with_vat = base_amount + vat_amount
        
        return (float(vat_amount), float(total_with_vat))
        
    except (ValueError, TypeError):
        return (0.0, float(amount or 0))

def calculate_discount(amount, discount_percent=0, discount_amount=0):
    """
    Calculate discount
    
    Args:
        amount: Original amount
        discount_percent: Discount percentage (0-100)
        discount_amount: Fixed discount amount
    
    Returns:
        tuple: (discount_amount, final_amount)
    """
    try:
        original_amount = Decimal(str(amount))
        
        if discount_amount > 0:
            # Fixed discount amount
            discount = Decimal(str(discount_amount))
        elif discount_percent > 0:
            # Percentage discount
            discount = original_amount * Decimal(str(discount_percent)) / Decimal('100')
        else:
            discount = Decimal('0')
        
        # Ensure discount doesn't exceed original amount
        if discount > original_amount:
            discount = original_amount
        
        final_amount = original_amount - discount
        
        return (float(discount), float(final_amount))
        
    except (ValueError, TypeError):
        return (0.0, float(amount or 0))

def calculate_installment(principal, months, interest_rate=0):
    """
    Calculate installment payment
    
    Args:
        principal: Principal amount
        months: Number of months
        interest_rate: Monthly interest rate (decimal)
    
    Returns:
        tuple: (monthly_payment, total_payment, total_interest)
    """
    try:
        if months <= 0:
            return (float(principal), float(principal), 0.0)
        
        principal_amount = Decimal(str(principal))
        
        if interest_rate > 0:
            # Calculate with interest
            monthly_rate = Decimal(str(interest_rate))
            num_payments = Decimal(str(months))
            
            # Monthly payment formula: P * [r(1+r)^n] / [(1+r)^n - 1]
            rate_plus_one = 1 + monthly_rate
            power_term = rate_plus_one ** num_payments
            
            monthly_payment = principal_amount * (monthly_rate * power_term) / (power_term - 1)
            total_payment = monthly_payment * num_payments
            total_interest = total_payment - principal_amount
        else:
            # Simple division without interest
            monthly_payment = principal_amount / Decimal(str(months))
            total_payment = principal_amount
            total_interest = Decimal('0')
        
        return (
            float(monthly_payment.quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
            float(total_payment.quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
            float(total_interest.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        )
        
    except (ValueError, TypeError, ZeroDivisionError):
        return (0.0, 0.0, 0.0)

def format_percentage(value, decimal_places=1):
    """
    Format value as percentage
    
    Args:
        value: Value to format (0.1 = 10%)
        decimal_places: Number of decimal places
    
    Returns:
        str: Formatted percentage
    """
    try:
        percentage = float(value) * 100
        format_string = f"{{:.{decimal_places}f}}%"
        return format_string.format(percentage)
    except (ValueError, TypeError):
        return "0.0%"