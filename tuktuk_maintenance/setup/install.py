"""
Installation and Setup Functions for Maintenance Addon
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Setup maintenance addon after installation"""
    try:
        # Create custom fields in base doctypes
        create_maintenance_custom_fields()
        
        # Setup default maintenance schedules
        setup_default_maintenance_schedules()
        
        # Create default parts inventory
        setup_default_parts_inventory()
        
        # Setup roles and permissions
        setup_maintenance_roles()
        
        print("TukTuk Maintenance addon installed successfully!")
        
    except Exception as e:
        frappe.log_error(f"Error during maintenance addon installation: {str(e)}")

def create_maintenance_custom_fields():
    """Add maintenance fields to base TukTuk Vehicle doctype"""
    custom_fields = {
        "TukTuk Vehicle": [
            {
                "fieldname": "maintenance_tab",
                "fieldtype": "Tab Break",
                "label": "Maintenance",
                "insert_after": "location_tab"
            },
            {
                "fieldname": "maintenance_info_section",
                "fieldtype": "Section Break", 
                "label": "Maintenance Information",
                "insert_after": "maintenance_tab"
            },
            {
                "fieldname": "last_maintenance_date",
                "fieldtype": "Date",
                "label": "Last Maintenance",
                "insert_after": "maintenance_info_section"
            },
            {
                "fieldname": "next_maintenance_due",
                "fieldtype": "Date",
                "label": "Next Maintenance Due", 
                "insert_after": "last_maintenance_date"
            },
            {
                "fieldname": "maintenance_status",
                "fieldtype": "Select",
                "label": "Maintenance Status",
                "options": "Good\nNeeds Attention\nCritical\nOverdue",
                "default": "Good",
                "insert_after": "next_maintenance_due"
            },
            {
                "fieldname": "column_break_maintenance",
                "fieldtype": "Column Break",
                "insert_after": "maintenance_status"
            },
            {
                "fieldname": "total_maintenance_cost",
                "fieldtype": "Currency",
                "label": "Total Maintenance Cost",
                "read_only": 1,
                "insert_after": "column_break_maintenance"
            },
            {
                "fieldname": "maintenance_alerts_count",
                "fieldtype": "Int",
                "label": "Active Alerts",
                "read_only": 1,
                "insert_after": "total_maintenance_cost"
            }
        ]
    }
    
    create_custom_fields(custom_fields)

def setup_default_maintenance_schedules():
    """Create default maintenance schedule templates"""
    default_schedules = [
        {
            "maintenance_type": "Daily Check",
            "frequency_days": 1,
            "priority": "Low",
            "description": "Daily vehicle inspection and battery check"
        },
        {
            "maintenance_type": "Weekly Service", 
            "frequency_days": 7,
            "priority": "Medium",
            "description": "Weekly maintenance including tire pressure, lights, and cleaning"
        },
        {
            "maintenance_type": "Monthly Service",
            "frequency_days": 30, 
            "priority": "Medium",
            "description": "Monthly comprehensive service and battery health check"
        },
        {
            "maintenance_type": "Battery Check",
            "frequency_days": 14,
            "priority": "High", 
            "description": "Bi-weekly battery health and charging system inspection"
        },
        {
            "maintenance_type": "Solar Panel Cleaning",
            "frequency_days": 7,
            "priority": "Medium",
            "description": "Weekly solar panel cleaning and inspection"
        }
    ]
    
    # These would be created as templates, not active schedules
    # Active schedules would be created per vehicle during vehicle setup

def setup_default_parts_inventory():
    """Create default parts inventory items"""
    default_parts = [
        {
            "part_name": "12V Battery Cell",
            "category": "Battery",
            "minimum_stock": 5,
            "unit_cost": 2500,
            "description": "Standard 12V battery cell for TukTuk"
        },
        {
            "part_name": "Solar Panel 100W", 
            "category": "Solar Panel",
            "minimum_stock": 2,
            "unit_cost": 8500,
            "description": "100W solar panel for roof mounting"
        },
        {
            "part_name": "Tire - Front",
            "category": "Tires",
            "minimum_stock": 4,
            "unit_cost": 3500,
            "description": "Front wheel tire"
        },
        {
            "part_name": "Tire - Rear",
            "category": "Tires", 
            "minimum_stock": 4,
            "unit_cost": 4000,
            "description": "Rear wheel tire"
        },
        {
            "part_name": "Brake Pads",
            "category": "Brakes",
            "minimum_stock": 8,
            "unit_cost": 1200,
            "description": "Standard brake pads"
        },
        {
            "part_name": "LED Headlight",
            "category": "Electrical",
            "minimum_stock": 4,
            "unit_cost": 800,
            "description": "LED headlight assembly"
        }
    ]
    
    for part_data in default_parts:
        if not frappe.db.exists("Maintenance Parts Inventory", part_data["part_name"]):
            part = frappe.new_doc("Maintenance Parts Inventory")
            part.update(part_data)
            part.current_stock = 0  # Start with zero stock
            part.is_active = 1
            part.insert()

def setup_maintenance_roles():
    """Setup roles and permissions for maintenance system"""
    # Create Maintenance Technician role if it doesn't exist
    if not frappe.db.exists("Role", "Maintenance Technician"):
        role = frappe.new_doc("Role")
        role.role_name = "Maintenance Technician"
        role.desk_access = 1
        role.insert()

def before_uninstall():
    """Cleanup before uninstalling maintenance addon"""
    try:
        # Remove custom fields
        custom_fields = frappe.get_all("Custom Field", 
                                     filters={"dt": "TukTuk Vehicle", 
                                            "fieldname": ["like", "maintenance%"]})
        for field in custom_fields:
            frappe.delete_doc("Custom Field", field.name)
        
        print("TukTuk Maintenance addon cleanup completed!")
        
    except Exception as e:
        frappe.log_error(f"Error during maintenance addon uninstall: {str(e)}")

def create_number_cards():
    """Create Number Cards for the workspace"""
    try:
        from tuktuk_maintenance.setup.create_number_cards import create_maintenance_number_cards
        create_maintenance_number_cards()
        print("✅ Number Cards created successfully")
    except Exception as e:
        print(f"⚠️  Number Cards creation skipped: {str(e)}")
