#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data models for ChViet Mobile Store Management System
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
import json

@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    category_id: Optional[int] = None
    brand: str = ""
    model: str = ""
    barcode: str = ""
    sku: str = ""
    cost_price: float = 0.0
    selling_price: float = 0.0
    warranty_months: int = 12
    description: str = ""
    specifications: str = ""
    is_active: bool = True
    track_imei: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class InventoryItem:
    id: Optional[int] = None
    product_id: int = 0
    imei: str = ""
    serial_number: str = ""
    condition: str = "new"
    status: str = "available"
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    supplier_id: Optional[int] = None
    purchase_date: Optional[date] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None
    location: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    id_number: str = ""
    birth_date: Optional[date] = None
    notes: str = ""
    debt_limit: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Sale:
    id: Optional[int] = None
    invoice_number: str = ""
    customer_id: Optional[int] = None
    staff_id: Optional[int] = None
    sale_date: Optional[datetime] = None
    subtotal: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    paid_amount: float = 0.0
    payment_method: str = "cash"
    payment_status: str = "pending"
    sale_type: str = "retail"
    notes: str = ""
    is_installment: bool = False
    installment_months: int = 0
    monthly_payment: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SaleItem:
    id: Optional[int] = None
    sale_id: int = 0
    inventory_id: Optional[int] = None
    product_id: int = 0
    imei: str = ""
    quantity: int = 1
    unit_price: float = 0.0
    discount_amount: float = 0.0
    total_price: float = 0.0
    warranty_months: int = 12
    created_at: Optional[datetime] = None

@dataclass
class Repair:
    id: Optional[int] = None
    repair_number: str = ""
    customer_id: Optional[int] = None
    staff_id: Optional[int] = None
    device_info: str = ""
    imei: str = ""
    problem_description: str = ""
    diagnosis: str = ""
    repair_status: str = "received"
    labor_cost: float = 0.0
    parts_cost: float = 0.0
    total_cost: float = 0.0
    paid_amount: float = 0.0
    estimated_completion: Optional[date] = None
    actual_completion: Optional[date] = None
    warranty_months: int = 3
    qr_code: str = ""
    pattern_lock_info: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Warranty:
    id: Optional[int] = None
    warranty_number: str = ""
    imei: str = ""
    product_id: Optional[int] = None
    customer_id: Optional[int] = None
    sale_id: Optional[int] = None
    repair_id: Optional[int] = None
    warranty_type: str = "product"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "active"
    qr_code: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class PawnContract:
    id: Optional[int] = None
    contract_number: str = ""
    customer_id: int = 0
    staff_id: Optional[int] = None
    item_description: str = ""
    item_value: float = 0.0
    loan_amount: float = 0.0
    interest_rate: float = 0.0
    contract_date: Optional[date] = None
    due_date: Optional[date] = None
    status: str = "active"
    total_interest: float = 0.0
    payments_made: float = 0.0
    renewal_count: int = 0
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Staff:
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    full_name: str = ""
    phone: str = ""
    email: str = ""
    role: str = "staff"
    permissions: str = ""
    commission_rate: float = 0.0
    salary: float = 0.0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Transaction:
    id: Optional[int] = None
    transaction_type: str = ""
    amount: float = 0.0
    description: str = ""
    reference_id: Optional[int] = None
    reference_type: str = ""
    payment_method: str = "cash"
    staff_id: Optional[int] = None
    transaction_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

@dataclass
class SimCard:
    id: Optional[int] = None
    phone_number: str = ""
    network_provider: str = ""
    sim_type: str = "prepaid"
    cost_price: float = 0.0
    selling_price: float = 0.0
    status: str = "available"
    special_features: str = ""
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
