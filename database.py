#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database management for ChViet Mobile Store Management System
"""

import sqlite3
import os
from datetime import datetime
from config import APP_CONFIG, DATABASE_CONFIG

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or APP_CONFIG['DATABASE_NAME']
        self.connection = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            
            # Apply PRAGMA settings
            for pragma in DATABASE_CONFIG['PRAGMA_SETTINGS']:
                self.connection.execute(pragma)
            
            return self.connection
        except Exception as e:
            print(f"Database connection error: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        if not self.connection:
            self.connect()
        
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            return cursor
        except Exception as e:
            self.connection.rollback()
            print(f"Query execution error: {e}")
            raise
    
    def fetch_all(self, query, params=None):
        """Fetch all results from a query"""
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Fetch one result from a query"""
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def initialize_database(self):
        """Initialize database with all required tables"""
        self.connect()
        
        # Create tables in order (respecting foreign key dependencies)
        self.create_categories_table()
        self.create_suppliers_table()
        self.create_customers_table()
        self.create_staff_table()
        self.create_products_table()
        self.create_inventory_table()
        self.create_sales_table()
        self.create_sale_items_table()
        self.create_repairs_table()
        self.create_repair_items_table()
        self.create_warranties_table()
        self.create_pawn_contracts_table()
        self.create_transactions_table()
        self.create_debts_table()
        self.create_sim_cards_table()
        self.create_settings_table()
        
        # Insert default data
        self.insert_default_data()
    
    def create_categories_table(self):
        """Create product categories table"""
        query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_suppliers_table(self):
        """Create suppliers table"""
        query = """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            tax_code TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_customers_table(self):
        """Create customers table"""
        query = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE,
            email TEXT,
            address TEXT,
            id_number TEXT,
            birth_date DATE,
            notes TEXT,
            debt_limit REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_staff_table(self):
        """Create staff table"""
        query = """
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            role TEXT DEFAULT 'staff',
            permissions TEXT,
            commission_rate REAL DEFAULT 0,
            salary REAL DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_products_table(self):
        """Create products table"""
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            brand TEXT,
            model TEXT,
            barcode TEXT UNIQUE,
            sku TEXT UNIQUE,
            cost_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            warranty_months INTEGER DEFAULT 12,
            description TEXT,
            specifications TEXT,
            is_active BOOLEAN DEFAULT 1,
            track_imei BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
        """
        self.execute_query(query)
    
    def create_inventory_table(self):
        """Create inventory table for tracking stock"""
        query = """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            imei TEXT UNIQUE,
            serial_number TEXT,
            condition TEXT DEFAULT 'new',
            status TEXT DEFAULT 'available',
            cost_price REAL,
            selling_price REAL,
            supplier_id INTEGER,
            purchase_date DATE,
            warranty_start_date DATE,
            warranty_end_date DATE,
            location TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
        """
        self.execute_query(query)
    
    def create_sales_table(self):
        """Create sales table"""
        query = """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            staff_id INTEGER,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            subtotal REAL DEFAULT 0,
            discount_amount REAL DEFAULT 0,
            tax_amount REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'cash',
            payment_status TEXT DEFAULT 'pending',
            sale_type TEXT DEFAULT 'retail',
            notes TEXT,
            is_installment BOOLEAN DEFAULT 0,
            installment_months INTEGER DEFAULT 0,
            monthly_payment REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
        """
        self.execute_query(query)
    
    def create_sale_items_table(self):
        """Create sale items table"""
        query = """
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            inventory_id INTEGER,
            product_id INTEGER NOT NULL,
            imei TEXT,
            quantity INTEGER DEFAULT 1,
            unit_price REAL NOT NULL,
            discount_amount REAL DEFAULT 0,
            total_price REAL NOT NULL,
            warranty_months INTEGER DEFAULT 12,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (inventory_id) REFERENCES inventory (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """
        self.execute_query(query)
    
    def create_repairs_table(self):
        """Create repairs table"""
        query = """
        CREATE TABLE IF NOT EXISTS repairs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repair_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER,
            staff_id INTEGER,
            device_info TEXT,
            imei TEXT,
            problem_description TEXT NOT NULL,
            diagnosis TEXT,
            repair_status TEXT DEFAULT 'received',
            labor_cost REAL DEFAULT 0,
            parts_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            paid_amount REAL DEFAULT 0,
            estimated_completion DATE,
            actual_completion DATE,
            warranty_months INTEGER DEFAULT 3,
            qr_code TEXT,
            pattern_lock_info TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
        """
        self.execute_query(query)
    
    def create_repair_items_table(self):
        """Create repair items (parts used) table"""
        query = """
        CREATE TABLE IF NOT EXISTS repair_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repair_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            unit_cost REAL NOT NULL,
            total_cost REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (repair_id) REFERENCES repairs (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        """
        self.execute_query(query)
    
    def create_warranties_table(self):
        """Create warranties table"""
        query = """
        CREATE TABLE IF NOT EXISTS warranties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warranty_number TEXT UNIQUE NOT NULL,
            imei TEXT,
            product_id INTEGER,
            customer_id INTEGER,
            sale_id INTEGER,
            repair_id INTEGER,
            warranty_type TEXT DEFAULT 'product',
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status TEXT DEFAULT 'active',
            qr_code TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (repair_id) REFERENCES repairs (id)
        )
        """
        self.execute_query(query)
    
    def create_pawn_contracts_table(self):
        """Create pawn contracts table"""
        query = """
        CREATE TABLE IF NOT EXISTS pawn_contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_number TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            staff_id INTEGER,
            item_description TEXT NOT NULL,
            item_value REAL NOT NULL,
            loan_amount REAL NOT NULL,
            interest_rate REAL NOT NULL,
            contract_date DATE NOT NULL,
            due_date DATE NOT NULL,
            status TEXT DEFAULT 'active',
            total_interest REAL DEFAULT 0,
            payments_made REAL DEFAULT 0,
            renewal_count INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id),
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
        """
        self.execute_query(query)
    
    def create_transactions_table(self):
        """Create financial transactions table"""
        query = """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            reference_id INTEGER,
            reference_type TEXT,
            payment_method TEXT DEFAULT 'cash',
            staff_id INTEGER,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff (id)
        )
        """
        self.execute_query(query)
    
    def create_debts_table(self):
        """Create debts table for customer/supplier debts"""
        query = """
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            debtor_type TEXT NOT NULL,
            debtor_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            reference_id INTEGER,
            reference_type TEXT,
            due_date DATE,
            status TEXT DEFAULT 'outstanding',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_sim_cards_table(self):
        """Create SIM cards table for managing phone numbers"""
        query = """
        CREATE TABLE IF NOT EXISTS sim_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            network_provider TEXT,
            sim_type TEXT DEFAULT 'prepaid',
            cost_price REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            status TEXT DEFAULT 'available',
            special_features TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def create_settings_table(self):
        """Create settings table for application configuration"""
        query = """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.execute_query(query)
    
    def insert_default_data(self):
        """Insert default data into tables"""
        try:
            # Default categories
            categories = [
                ('Điện thoại thông minh', 'Smartphone các loại'),
                ('Phụ kiện', 'Phụ kiện điện thoại'),
                ('Linh kiện sửa chữa', 'Linh kiện thay thế'),
                ('SIM số đẹp', 'SIM số đẹp các mạng'),
                ('Thẻ cào', 'Thẻ cào điện thoại')
            ]
            
            for name, desc in categories:
                try:
                    self.execute_query(
                        "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                        (name, desc)
                    )
                except:
                    pass
            
            # Default admin user
            try:
                self.execute_query(
                    """INSERT OR IGNORE INTO staff 
                       (username, password, full_name, role, permissions, is_active) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    ('admin', 'admin123', 'Quản trị viên', 'admin', 'all', 1)
                )
            except:
                pass
            
            # Default settings
            default_settings = [
                ('store_name', 'Cửa Hàng Điện Thoại ChViet', 'Tên cửa hàng'),
                ('store_address', '', 'Địa chỉ cửa hàng'),
                ('store_phone', '', 'Số điện thoại cửa hàng'),
                ('vat_rate', '10', 'Thuế VAT (%)'),
                ('currency', 'VNĐ', 'Đơn vị tiền tệ'),
                ('low_stock_threshold', '5', 'Ngưỡng cảnh báo tồn kho'),
                ('warranty_default_months', '12', 'Thời gian bảo hành mặc định (tháng)'),
                ('pawn_interest_rate', '3', 'Lãi suất cầm đồ (% tháng)')
            ]
            
            for key, value, desc in default_settings:
                try:
                    self.execute_query(
                        "INSERT OR IGNORE INTO settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                        (key, value, desc)
                    )
                except:
                    pass
            
        except Exception as e:
            print(f"Error inserting default data: {e}")
