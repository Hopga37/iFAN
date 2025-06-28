#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QR Code utility functions for ChViet Mobile Store Management System
"""

import uuid
from datetime import datetime

def generate_qr_code(data, qr_type="general"):
    """
    Generate QR code data string
    
    Args:
        data: Data to encode in QR code
        qr_type: Type of QR code (repair, warranty, product, etc.)
    
    Returns:
        str: QR code data string
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    qr_id = str(uuid.uuid4())[:8]
    
    if qr_type == "repair":
        return f"REPAIR:{data}:{timestamp}:{qr_id}"
    elif qr_type == "warranty":
        return f"WARRANTY:{data}:{timestamp}:{qr_id}"
    elif qr_type == "product":
        return f"PRODUCT:{data}:{timestamp}:{qr_id}"
    elif qr_type == "pawn":
        return f"PAWN:{data}:{timestamp}:{qr_id}"
    else:
        return f"CHVIET:{data}:{timestamp}:{qr_id}"

def parse_qr_code(qr_data):
    """
    Parse QR code data string
    
    Args:
        qr_data: QR code data string
    
    Returns:
        dict: Parsed QR code information
    """
    try:
        parts = qr_data.split(':')
        if len(parts) >= 4:
            return {
                'type': parts[0],
                'data': parts[1],
                'timestamp': parts[2],
                'qr_id': parts[3],
                'valid': True
            }
        else:
            return {
                'type': 'unknown',
                'data': qr_data,
                'timestamp': '',
                'qr_id': '',
                'valid': False
            }
    except Exception:
        return {
            'type': 'unknown',
            'data': qr_data,
            'timestamp': '',
            'qr_id': '',
            'valid': False
        }

def generate_repair_qr(repair_number):
    """
    Generate QR code for repair tracking
    
    Args:
        repair_number: Repair number/ID
    
    Returns:
        str: QR code data for repair
    """
    return generate_qr_code(repair_number, "repair")

def generate_warranty_qr(warranty_number, imei=""):
    """
    Generate QR code for warranty tracking
    
    Args:
        warranty_number: Warranty number
        imei: Optional IMEI number
    
    Returns:
        str: QR code data for warranty
    """
    data = f"{warranty_number}|{imei}" if imei else warranty_number
    return generate_qr_code(data, "warranty")

def generate_product_qr(product_id, imei="", serial=""):
    """
    Generate QR code for product tracking
    
    Args:
        product_id: Product ID
        imei: Optional IMEI number
        serial: Optional serial number
    
    Returns:
        str: QR code data for product
    """
    data_parts = [str(product_id)]
    if imei:
        data_parts.append(imei)
    if serial:
        data_parts.append(serial)
    
    data = "|".join(data_parts)
    return generate_qr_code(data, "product")

def create_qr_lookup_url(qr_data, base_url="https://chviet.com/lookup"):
    """
    Create lookup URL for QR code
    
    Args:
        qr_data: QR code data
        base_url: Base URL for lookup service
    
    Returns:
        str: Lookup URL
    """
    return f"{base_url}?qr={qr_data}"