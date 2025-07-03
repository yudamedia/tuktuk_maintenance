"""
Document Event Hooks for Integration with Base System
"""

import frappe
from frappe.utils import flt, get_datetime

def vehicle_validate(doc, method):
    """Validate vehicle document with maintenance considerations"""
    # Check if vehicle is assigned but in maintenance
    if doc.status == "Assigned" and frappe.db.exists("TukTuk Maintenance Record", {
        "tuktuk_vehicle": doc.name,
        "status": ["in", ["Open", "In Progress"]]
    }):
        frappe.throw("Cannot assign vehicle that has pending maintenance")

def vehicle_on_update(doc, method):
    """Handle vehicle updates that affect maintenance"""
    # If battery level drops critically, create maintenance alert
    if doc.battery_level and flt(doc.battery_level) < 20:
        existing_alert = frappe.db.exists("Maintenance Alert", {
            "tuktuk_vehicle": doc.name,
            "alert_type": "Battery Warning",
            "status": ["in", ["Open", "Acknowledged"]]
        })
        
        if not existing_alert:
            from tuktuk_maintenance.api.maintenance import create_maintenance_alert
            create_maintenance_alert(
                tuktuk_vehicle=doc.name,
                alert_type="Battery Warning",
                message=f"Critical battery level: {doc.battery_level}%",
                priority="High"
            )

def maintenance_on_submit(doc, method):
    """Handle maintenance record submission"""
    # Update vehicle status back to available if maintenance completed
    if doc.status == "Completed":
        vehicle = frappe.get_doc("TukTuk Vehicle", doc.tuktuk_vehicle)
        if vehicle.status == "Maintenance":
            vehicle.status = "Available"
            vehicle.save()
        
        # Update parts inventory
        for part in doc.parts_used:
            from tuktuk_maintenance.api.parts import update_parts_stock
            update_parts_stock(part.part_name, part.quantity, doc.name)
        
        # Calculate and update duration
        if doc.started_datetime and doc.completed_datetime:
            duration = (doc.completed_datetime - doc.started_datetime).total_seconds() / 3600
            doc.duration_hours = duration
        
        # Update next maintenance date if specified
        if doc.next_maintenance_date:
            vehicle = frappe.get_doc("TukTuk Vehicle", doc.tuktuk_vehicle)
            vehicle.next_maintenance_due = doc.next_maintenance_date
            vehicle.last_maintenance_date = doc.completed_datetime.date()
            vehicle.save()

def maintenance_on_cancel(doc, method):
    """Handle maintenance record cancellation"""
    # Restore parts inventory
    for part in doc.parts_used:
        part_doc = frappe.get_doc("Maintenance Parts Inventory", part.part_name)
        part_doc.current_stock = flt(part_doc.current_stock) + flt(part.quantity)
        part_doc.save()
