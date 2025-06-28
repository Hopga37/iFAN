# ChViet Mobile Store Management System

## Overview

ChViet is a comprehensive mobile phone store management system built with Python and Tkinter. The system manages inventory, sales, repairs, warranties, pawn services, financial tracking, staff management, and reporting for a mobile phone retail business. The application follows a desktop-first approach with a tabbed interface for different business modules.

## System Architecture

### Desktop Application Architecture
- **Frontend**: Tkinter-based GUI with modern ttk styling
- **Backend**: Python business logic with modular design
- **Database**: SQLite for local data storage
- **Configuration**: Centralized configuration management
- **Models**: Dataclass-based data models for type safety

### Key Design Principles
- Modular tab-based architecture for different business functions
- Separation of concerns with dedicated modules for GUI, database, and business logic
- Configuration-driven approach for business rules and settings
- Object-oriented design with clear model definitions

## Key Components

### Core Application Layer
- **main.py**: Application entry point and initialization
- **config.py**: Centralized configuration for business rules, GUI settings, and database parameters
- **database.py**: SQLite database connection and query management
- **models.py**: Data models using Python dataclasses

### GUI Modules (gui/ directory)
- **main_window.py**: Main application window with login system
- **inventory_tab.py**: Product and inventory management
- **sales_tab.py**: Sales processing and customer management
- **repair_tab.py**: Device repair service management
- **warranty_tab.py**: Warranty tracking and claims
- **pawn_tab.py**: Pawn shop operations
- **financial_tab.py**: Financial tracking and reporting
- **staff_tab.py**: Employee management and permissions
- **reports_tab.py**: Business analytics and reporting

### Business Logic
- VAT calculation (10% rate)
- Warranty management (12-month default)
- Pawn interest calculations (3% monthly)
- Low stock alerts (threshold of 5 units)
- Vietnamese currency formatting (VNĐ)

## Data Flow

### Application Startup
1. Database initialization and connection
2. User authentication via login dialog
3. Main window creation with tabbed interface
4. Module initialization with database manager injection

### Transaction Processing
1. User input through GUI forms
2. Data validation and business rule application
3. Database persistence through DatabaseManager
4. UI updates and feedback to user

### Data Persistence
- SQLite database with WAL journaling mode
- Foreign key constraints enabled
- Optimized cache settings for performance
- Automatic backup capabilities

## External Dependencies

### Core Dependencies
- **Python 3.11**: Primary runtime environment
- **tkinter/ttk**: GUI framework (standard library)
- **sqlite3**: Database engine (standard library)
- **datetime**: Date/time handling
- **dataclasses**: Model definitions
- **json**: Data serialization
- **hashlib**: Password hashing
- **uuid**: Unique identifier generation

### Utility Dependencies
- **calendar**: Date calculations
- **decimal**: Precise financial calculations
- **os**: File system operations

## Deployment Strategy

### Development Environment
- Replit-based development with Python 3.11 module
- Nix channel stable-24_05 for package management
- Workflow configuration for easy project execution

### Database Strategy
- Local SQLite database for single-user desktop deployment
- Database file: `chviet_store.db`
- Automatic directory creation for backups, reports, and temporary files

### Configuration Management
- Environment-specific settings in config.py
- Support for Vietnamese localization
- Configurable business rules and GUI themes

## Changelog

```
Changelog:
- June 27, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```