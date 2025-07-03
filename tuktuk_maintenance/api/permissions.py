"""
Permissions API for TukTuk Maintenance
Handles query conditions for different user roles
"""

import frappe

def maintenance_query_conditions(user):
    """
    Return query conditions for TukTuk Maintenance Record based on user permissions
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Tuktuk Manager can see all records
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Tuktuk Manager" in frappe.get_roles(user):
        return ""
    
    # Fleet Supervisor can see all records
    if "Fleet Supervisor" in frappe.get_roles(user):
        return ""
    
    # Maintenance Technician can see records assigned to them or created by them
    if "Maintenance Technician" in frappe.get_roles(user):
        return f"""(
            `tabTukTuk Maintenance Record`.`assigned_to` = '{frappe.db.escape(user)}' 
            OR `tabTukTuk Maintenance Record`.`owner` = '{frappe.db.escape(user)}'
        )"""
    
    # Driver can see records for their assigned vehicle only
    if "Driver" in frappe.get_roles(user):
        # Get driver's assigned vehicle
        assigned_vehicle = frappe.db.get_value("TukTuk Driver", 
                                             {"user": user, "status": "Active"}, 
                                             "assigned_tuktuk")
        if assigned_vehicle:
            return f"`tabTukTuk Maintenance Record`.`tuktuk_vehicle` = '{frappe.db.escape(assigned_vehicle)}'"
        else:
            # If no assigned vehicle, can't see any records
            return "1=0"
    
    # Default: can't see any maintenance records
    return "1=0"

def battery_health_query_conditions(user):
    """
    Return query conditions for Battery Health Log based on user permissions
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Tuktuk Manager can see all records
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Tuktuk Manager" in frappe.get_roles(user):
        return ""
    
    # Fleet Supervisor can see all records
    if "Fleet Supervisor" in frappe.get_roles(user):
        return ""
    
    # Maintenance Technician can see all battery health records
    if "Maintenance Technician" in frappe.get_roles(user):
        return ""
    
    # Driver can see records for their assigned vehicle only
    if "Driver" in frappe.get_roles(user):
        # Get driver's assigned vehicle
        assigned_vehicle = frappe.db.get_value("TukTuk Driver", 
                                             {"user": user, "status": "Active"}, 
                                             "assigned_tuktuk")
        if assigned_vehicle:
            return f"`tabBattery Health Log`.`tuktuk_vehicle` = '{frappe.db.escape(assigned_vehicle)}'"
        else:
            # If no assigned vehicle, can't see any records
            return "1=0"
    
    # Default: can't see any battery health records
    return "1=0"

def parts_inventory_query_conditions(user):
    """
    Return query conditions for Maintenance Parts Inventory based on user permissions
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Tuktuk Manager can see all records
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Tuktuk Manager" in frappe.get_roles(user):
        return ""
    
    # Fleet Supervisor and Maintenance Technician can see all parts
    if "Fleet Supervisor" in frappe.get_roles(user) or "Maintenance Technician" in frappe.get_roles(user):
        return ""
    
    # Drivers and others can't see parts inventory
    return "1=0"

def maintenance_alert_query_conditions(user):
    """
    Return query conditions for Maintenance Alert based on user permissions
    """
    if not user:
        user = frappe.session.user
    
    # System Manager and Tuktuk Manager can see all alerts
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return ""
    
    if "Tuktuk Manager" in frappe.get_roles(user):
        return ""
    
    # Fleet Supervisor can see all alerts
    if "Fleet Supervisor" in frappe.get_roles(user):
        return ""
    
    # Maintenance Technician can see alerts assigned to them
    if "Maintenance Technician" in frappe.get_roles(user):
        return f"""(
            `tabMaintenance Alert`.`assigned_to` = '{frappe.db.escape(user)}' 
            OR `tabMaintenance Alert`.`assigned_to` IS NULL
        )"""
    
    # Driver can see alerts for their assigned vehicle only
    if "Driver" in frappe.get_roles(user):
        # Get driver's assigned vehicle
        assigned_vehicle = frappe.db.get_value("TukTuk Driver", 
                                             {"user": user, "status": "Active"}, 
                                             "assigned_tuktuk")
        if assigned_vehicle:
            return f"`tabMaintenance Alert`.`tuktuk_vehicle` = '{frappe.db.escape(assigned_vehicle)}'"
        else:
            # If no assigned vehicle, can't see any alerts
            return "1=0"
    
    # Default: can't see any alerts
    return "1=0"
