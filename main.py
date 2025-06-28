#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChViet Mobile Store Management System
Main application entry point
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Set DISPLAY for VNC environment
if not os.environ.get('DISPLAY'):
    os.environ['DISPLAY'] = ':1'

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from gui.main_window import MainWindow
from config import APP_CONFIG

class ChVietApp:
    def __init__(self):
        self.db_manager = None
        self.main_window = None
        
    def initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            self.db_manager = DatabaseManager()
            self.db_manager.initialize_database()
            print("Database initialized successfully")
            return True
        except Exception as e:
            messagebox.showerror("Lỗi Database", f"Không thể khởi tạo database: {str(e)}")
            return False
    
    def run(self):
        """Main application entry point"""
        # Initialize database
        if not self.initialize_database():
            return
        
        # Create main window
        root = tk.Tk()
        root.title(APP_CONFIG['APP_NAME'])
        root.geometry(APP_CONFIG['WINDOW_SIZE'])
        root.state('zoomed' if os.name == 'nt' else 'normal')  # Maximize on Windows
        
        # Set application icon and style
        try:
            # Use ttk style for modern appearance
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure colors to match ChViet theme
            style.configure('TNotebook', background='#f0f0f0')
            style.configure('TNotebook.Tab', padding=[15, 8])
            style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), foreground='#2c5aa0')
            style.configure('Success.TLabel', foreground='#28a745')
            style.configure('Warning.TLabel', foreground='#ffc107')
            style.configure('Error.TLabel', foreground='#dc3545')
            
        except Exception as e:
            print(f"Style configuration error: {e}")
        
        # Initialize main window
        self.main_window = MainWindow(root, self.db_manager)
        
        # Handle window closing
        def on_closing():
            if messagebox.askokcancel("Thoát", "Bạn có chắc chắn muốn thoát ứng dụng?"):
                if self.db_manager:
                    self.db_manager.close_connection()
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        print("Starting ChViet Mobile Store Management System...")
        root.mainloop()

if __name__ == "__main__":
    app = ChVietApp()
    app.run()
