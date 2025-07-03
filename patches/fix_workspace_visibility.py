"""
Patch to fix workspace visibility
Save this as: tuktuk_maintenance/patches/fix_workspace_visibility.py
Then add to patches.txt: tuktuk_maintenance.patches.fix_workspace_visibility.execute
"""

import frappe
from frappe import _

def execute():
    """Execute workspace visibility fix"""
    
    print("🔧 Applying workspace visibility patch...")
    
    # 1. Create Module Definition if missing
    if not frappe.db.exists("Module Def", "TukTuk Maintenance"):
        try:
            module_def = frappe.new_doc("Module Def")
            module_def.module_name = "TukTuk Maintenance"
            module_def.app_name = "tuktuk_maintenance"
            module_def.insert()
            print("✅ Created Module Definition: TukTuk Maintenance")
        except Exception as e:
            print(f"❌ Failed to create Module Definition: {e}")
    
    # 2. Fix workspace configuration
    if frappe.db.exists("Workspace", "TukTuk Maintenance"):
        try:
            # Update directly in database to avoid any validation issues
            frappe.db.sql("""
                UPDATE `tabWorkspace`
                SET 
                    public = 1,
                    is_hidden = 0,
                    module = 'TukTuk Maintenance',
                    category = 'Modules',
                    disabled = 0
                WHERE name = 'TukTuk Maintenance'
            """)
            
            # Clear any role restrictions
            frappe.db.sql("""
                DELETE FROM `tabHas Role`
                WHERE parent = 'TukTuk Maintenance'
                AND parenttype = 'Workspace'
            """)
            
            print("✅ Updated workspace configuration in database")
            
        except Exception as e:
            print(f"❌ Failed to update workspace: {e}")
    else:
        print("❌ Workspace 'TukTuk Maintenance' not found")
    
    # 3. Ensure Tuktuk Manager role exists and has desk access
    if not frappe.db.exists("Role", "Tuktuk Manager"):
        try:
            role = frappe.new_doc("Role")
            role.role_name = "Tuktuk Manager"
            role.desk_access = 1
            role.insert()
            print("✅ Created Tuktuk Manager role")
        except Exception as e:
            print(f"❌ Failed to create role: {e}")
    else:
        # Ensure desk access is enabled
        frappe.db.sql("""
            UPDATE `tabRole`
            SET desk_access = 1
            WHERE name = 'Tuktuk Manager'
        """)
        print("✅ Ensured Tuktuk Manager has desk access")
    
    # 4. Check and fix workspace permissions
    workspace_data = frappe.db.get_value("Workspace", "TukTuk Maintenance", 
                                        ["public", "is_hidden", "module", "category", "disabled"], 
                                        as_dict=True)
    
    if workspace_data:
        print(f"✅ Workspace configuration verified:")
        print(f"   Public: {workspace_data.public}")
        print(f"   Hidden: {workspace_data.is_hidden}")
        print(f"   Module: {workspace_data.module}")
        print(f"   Category: {workspace_data.category}")
        print(f"   Disabled: {workspace_data.disabled}")
    
    # 5. Clear cache to ensure changes take effect
    frappe.clear_cache()
    print("✅ Cache cleared")
    
    # 6. Commit all changes
    frappe.db.commit()
    print("✅ All changes committed")
    
    print("\n🎉 Workspace visibility patch completed!")
    print("📝 Users should now:")
    print("   1. Log out and log back in")
    print("   2. Clear browser cache")
    print("   3. Check if TukTuk Maintenance appears in workspace sidebar")

if __name__ == "__main__":
    execute()