#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration settings for ChViet Mobile Store Management System
"""

import os

# Application Configuration
APP_CONFIG = {
    'APP_NAME': 'ChViet - Quản Lý Cửa Hàng Điện Thoại',
    'VERSION': '1.0.0',
    'WINDOW_SIZE': '1400x900',
    'DATABASE_NAME': 'chviet_store.db',
    'BACKUP_DIR': 'backups',
    'REPORTS_DIR': 'reports',
    'TEMP_DIR': 'temp'
}

# Database Configuration
DATABASE_CONFIG = {
    'PRAGMA_SETTINGS': [
        'PRAGMA foreign_keys = ON',
        'PRAGMA journal_mode = WAL',
        'PRAGMA synchronous = NORMAL',
        'PRAGMA cache_size = 10000'
    ]
}

# Business Configuration
BUSINESS_RULES = {
    'VAT_RATE': 0.1,  # 10% VAT
    'DEFAULT_WARRANTY_MONTHS': 12,
    'PAWN_INTEREST_RATE': 0.03,  # 3% per month
    'LOW_STOCK_THRESHOLD': 5,
    'CURRENCY': 'VNĐ',
    'DATE_FORMAT': '%d/%m/%Y',
    'DATETIME_FORMAT': '%d/%m/%Y %H:%M:%S'
}

# GUI Configuration
GUI_CONFIG = {
    'COLORS': {
        'PRIMARY': '#2c5aa0',
        'SUCCESS': '#28a745',
        'WARNING': '#ffc107',
        'DANGER': '#dc3545',
        'LIGHT': '#f8f9fa',
        'DARK': '#343a40'
    },
    'FONTS': {
        'DEFAULT': ('Arial', 10),
        'HEADING': ('Arial', 12, 'bold'),
        'LARGE': ('Arial', 14),
        'SMALL': ('Arial', 8)
    }
}

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    dirs = [
        APP_CONFIG['BACKUP_DIR'],
        APP_CONFIG['REPORTS_DIR'],
        APP_CONFIG['TEMP_DIR']
    ]
    
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Initialize directories on import
create_directories()
