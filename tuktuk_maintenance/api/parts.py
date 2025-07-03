"""
Parts Inventory Management API
"""

import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def check_parts_inventory():
    """Check parts inventory levels and generate alerts for low stock"""
    try:
        low_stock_parts = frappe.db.sql("""
            SELECT name, part_name, current_stock, minimum_stock, supplier
            FROM `tabMaintenance Parts Inventory`
            WHERE current_stock <= minimum_stock
            AND is_active = 1
        """, as_dict=True)
        
        alerts_created = 0
        for part in low_stock_parts:
            # Check if alert already exists
            existing_alert = frappe.db.exists("Maintenance Alert", {
                "alert_type": "Parts Low Stock",
                "alert_message": ["like", f"%{part.part_name}%"],
                "status": ["in", ["Open", "Acknowledged"]]
            })
            
            if not existing_alert:
                alert = frappe.new_doc("Maintenance Alert")
                alert.alert_type = "Parts Low Stock" 
                alert.alert_message = f"Low stock: {part.part_name} ({part.current_stock} remaining, minimum: {part.minimum_stock})"
                alert.priority = "Medium"
                alert.status = "Open"
                alert.insert()
                alerts_created += 1
        
        return {
            "success": True,
            "low_stock_parts": len(low_stock_parts),
            "alerts_created": alerts_created
        }
        
    except Exception as e:
        frappe.log_error(f"Error checking parts inventory: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def update_parts_stock(part_name, quantity_used, maintenance_record=None):
    """Update parts stock when used in maintenance"""
    try:
        part = frappe.get_doc("Maintenance Parts Inventory", part_name)
        part.current_stock = flt(part.current_stock) - flt(quantity_used)
        
        if part.current_stock < 0:
            frappe.throw(_("Insufficient stock for {0}. Available: {1}").format(
                part.part_name, part.current_stock + flt(quantity_used)
            ))
        
        part.save()
        
        # Check if stock fell below minimum
        if part.current_stock <= part.minimum_stock:
            check_parts_inventory()
        
        return {
            "success": True,
            "new_stock_level": part.current_stock,
            "message": f"Stock updated for {part.part_name}"
        }
        
    except Exception as e:
        frappe.log_error(f"Error updating parts stock: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def order_parts(part_name, quantity, supplier=None, urgent=False):
    """Create parts order request"""
    try:
        # This would integrate with ERPNext's Purchase Order system
        # For now, create a simple order record
        
        order = frappe.new_doc("Purchase Order")  # Using ERPNext's standard doctype
        order.supplier = supplier or "Default Supplier"
        order.transaction_date = frappe.utils.nowdate()
        
        # Add item
        order.append("items", {
            "item_code": part_name,
            "qty": quantity,
            "schedule_date": frappe.utils.add_days(frappe.utils.nowdate(), 1 if urgent else 7)
        })
        
        order.insert()
        
        return {
            "success": True,
            "order_id": order.name,
            "message": f"Parts order created for {part_name}"
        }
        
    except Exception as e:
        frappe.log_error(f"Error creating parts order: {str(e)}")
        return {"success": False, "error": str(e)}
