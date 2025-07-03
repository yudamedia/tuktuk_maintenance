"""
Boot session for TukTuk Maintenance
Ensures proper CSS and JS loading
"""

import frappe

def boot_session(bootinfo):
    """Add maintenance-specific context to boot"""
    
    # Force CSS loading for maintenance workspace
    if not bootinfo.get("tuktuk_maintenance_css_loaded"):
        bootinfo["tuktuk_maintenance_css_loaded"] = True
        
        # Add maintenance workspace CSS
        if "additional_css" not in bootinfo:
            bootinfo["additional_css"] = []
        
        bootinfo["additional_css"].append("/assets/tuktuk_maintenance/css/maintenance_workspace.css")
    
    # Add maintenance workspace identification
    bootinfo["maintenance_workspace_active"] = True
    
    return bootinfo