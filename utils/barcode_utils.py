#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Barcode utility functions for ChViet Mobile Store Management System
"""

import uuid
from datetime import datetime

def generate_barcode(product_id=None, prefix="CV"):
    """
    Generate a unique barcode for products
    
    Args:
        product_id: Optional product ID to include in barcode
        prefix: Prefix for the barcode (default: CV for ChViet)
    
    Returns:
        str: Generated barcode
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    if product_id:
        return f"{prefix}{product_id:04d}{timestamp[-6:]}"
    else:
        # Generate random suffix
        random_suffix = str(uuid.uuid4().int)[-6:]
        return f"{prefix}{timestamp[-8:]}{random_suffix}"

def validate_barcode(barcode):
    """
    Validate barcode format
    
    Args:
        barcode: Barcode string to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not barcode or len(barcode) < 8:
        return False
    
    # Basic validation - can be enhanced with checksum validation
    return barcode.isalnum()

def format_barcode_for_printing(barcode):
    """
    Format barcode for printing with proper spacing
    
    Args:
        barcode: Barcode string
    
    Returns:
        str: Formatted barcode
    """
    if not barcode:
        return ""
    
    # Add spaces every 4 characters for readability
    formatted = ""
    for i, char in enumerate(barcode):
        if i > 0 and i % 4 == 0:
            formatted += " "
        formatted += char
    
    return formatted

def generate_sku(category_code="GEN", product_counter=1):
    """
    Generate SKU (Stock Keeping Unit) for products
    
    Args:
        category_code: Category code (3 letters)
        product_counter: Sequential product number
    
    Returns:
        str: Generated SKU
    """
    return f"{category_code.upper()}{product_counter:06d}"