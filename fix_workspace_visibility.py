#!/usr/bin/env python3
"""
Script to fix TukTuk Maintenance workspace visibility issue
Run this script to ensure proper workspace configuration
"""

import frappe
from frappe import _

def fix_workspace_visibility():
    """Fix workspace visibility for TukTuk Manager users"""
    
    print("🔧 Fixing TukTuk Maintenance workspace visibility...")
    
    # 1. Create module definition if it doesn't exist
    if not frappe.db.exists("Module Def", "TukTuk Maintenance"):
        module_def = frappe.new_doc("Module Def")
        module_def.module_name = "TukTuk Maintenance"
        module_def.app_name = "tuktuk_maintenance"
        module_def.insert()
        print("✅ Created TukTuk Maintenance module definition")
    else:
        print("✅ TukTuk Maintenance module definition already exists")
    
    # 2. Ensure workspace is properly configured
    if frappe.db.exists("Workspace", "TukTuk Maintenance"):
        workspace = frappe.get_doc("Workspace", "TukTuk Maintenance")
        
        # Update workspace settings
        workspace.public = 1
        workspace.is_hidden = 0
        workspace.module = "TukTuk Maintenance"
        workspace.category = "Modules"
        
        # Clear any role restrictions (empty roles = available to all)
        workspace.roles = []
        
        # Save the workspace
        workspace.save()
        print("✅ Updated TukTuk Maintenance workspace configuration")
        
        # Print current workspace settings
        print(f"   - Public: {workspace.public}")
        print(f"   - Hidden: {workspace.is_hidden}")
        print(f"   - Module: {workspace.module}")
        print(f"   - Roles: {len(workspace.roles)} (empty = available to all)")
        
    else:
        print("❌ TukTuk Maintenance workspace not found!")
        return False
    
    # 3. Check if Tuktuk Manager role exists
    if frappe.db.exists("Role", "Tuktuk Manager"):
        print("✅ Tuktuk Manager role exists")
    else:
        print("❌ Tuktuk Manager role not found!")
        return False
    
    # 4. Commit all changes
    frappe.db.commit()
    print("✅ All changes committed successfully")
    
    print("\n🎉 Workspace visibility fix completed!")
    print("📝 Next steps:")
    print("   1. Clear browser cache and refresh the page")
    print("   2. Log out and log back in")
    print("   3. Check if TukTuk Maintenance workspace appears in the workspace sidebar")
    
    return True

if __name__ == "__main__":
    frappe.init()
    frappe.connect()
    fix_workspace_visibility() 