import frappe
from frappe import _

def execute():
    """Create TukTuk Maintenance module definition"""
    
    # Create module definition if it doesn't exist
    if not frappe.db.exists("Module Def", "TukTuk Maintenance"):
        module_def = frappe.new_doc("Module Def")
        module_def.module_name = "TukTuk Maintenance"
        module_def.app_name = "tuktuk_maintenance"
        module_def.insert()
        print("✅ Created TukTuk Maintenance module definition")
    else:
        print("✅ TukTuk Maintenance module definition already exists")
    
    # Ensure the workspace is properly configured
    if frappe.db.exists("Workspace", "TukTuk Maintenance"):
        workspace = frappe.get_doc("Workspace", "TukTuk Maintenance")
        workspace.public = 1
        workspace.is_hidden = 0
        workspace.module = "TukTuk Maintenance"
        workspace.save()
        print("✅ Updated TukTuk Maintenance workspace configuration")
    
    # Commit the changes
    frappe.db.commit() 