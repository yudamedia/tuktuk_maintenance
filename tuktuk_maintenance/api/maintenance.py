"""
Core Maintenance API Functions
Integrates with the base tuktuk_management system
"""

import frappe
from frappe import _
from datetime import datetime, timedelta
from frappe.utils import nowdate, add_days, get_datetime
import json

@frappe.whitelist()
def create_maintenance_record(tuktuk_vehicle, maintenance_type, issue_description, priority="Medium", scheduled_date=None):
    """Create a new maintenance record"""
    try:
        if not scheduled_date:
            scheduled_date = get_datetime()
        
        maintenance_record = frappe.new_doc("TukTuk Maintenance Record")
        maintenance_record.tuktuk_vehicle = tuktuk_vehicle
        maintenance_record.maintenance_type = maintenance_type
        maintenance_record.issue_description = issue_description
        maintenance_record.priority = priority
        maintenance_record.scheduled_date = scheduled_date
        maintenance_record.status = "Open"
        
        maintenance_record.insert()
        
        # Update vehicle status to maintenance if high priority
        if priority in ["High", "Critical"]:
            update_vehicle_maintenance_status(tuktuk_vehicle, "Maintenance")
        
        # Create alert if critical
        if priority == "Critical":
            create_maintenance_alert(
                tuktuk_vehicle=tuktuk_vehicle,
                alert_type="Critical Issue",
                message=f"Critical maintenance required: {issue_description}",
                priority="Critical"
            )
        
        return {
            "success": True,
            "maintenance_record": maintenance_record.name,
            "message": "Maintenance record created successfully"
        }
    
    except Exception as e:
        frappe.log_error(f"Error creating maintenance record: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def schedule_maintenance(tuktuk_vehicle, maintenance_type, due_date, frequency_days=30):
    """Schedule recurring maintenance for a vehicle"""
    try:
        schedule = frappe.new_doc("Maintenance Schedule")
        schedule.tuktuk_vehicle = tuktuk_vehicle
        schedule.maintenance_type = maintenance_type
        schedule.schedule_type = "Time-based"
        schedule.frequency_days = frequency_days
        schedule.next_due_date = due_date
        schedule.is_active = 1
        
        schedule.insert()
        
        return {
            "success": True,
            "schedule": schedule.name,
            "message": "Maintenance scheduled successfully"
        }
    
    except Exception as e:
        frappe.log_error(f"Error scheduling maintenance: {str(e)}")
        return {"success": False, "error": str(e)}

def daily_maintenance_check():
    """Daily scheduled task for maintenance checks"""
    try:
        # Only run if maintenance doctypes exist
        if not frappe.db.exists("DocType", "TukTuk Maintenance Record"):
            return
            
        # Basic daily maintenance check logic
        frappe.logger().info("Running daily maintenance check...")
        
        # Check for overdue maintenance
        overdue_count = frappe.db.count("TukTuk Maintenance Record", {
            "status": "Open",
            "scheduled_date": ["<", frappe.utils.now()]
        })
        
        if overdue_count > 0:
            frappe.logger().info(f"Found {overdue_count} overdue maintenance records")
            
    except Exception as e:
        frappe.log_error(f"Error in daily maintenance check: {str(e)}")

@frappe.whitelist()
def update_battery_health(tuktuk_vehicle, health_data):
    """Update battery health metrics and create log entry"""
    try:
        if isinstance(health_data, str):
            health_data = json.loads(health_data)
        
        # Create battery health log
        health_log = frappe.new_doc("Battery Health Log")
        health_log.tuktuk_vehicle = tuktuk_vehicle
        health_log.reading_date = get_datetime()
        health_log.reading_type = health_data.get("reading_type", "Automatic")
        
        # Battery metrics
        health_log.battery_percentage = health_data.get("battery_percentage")
        health_log.voltage_reading = health_data.get("voltage")
        health_log.temperature = health_data.get("temperature")
        health_log.charging_cycles = health_data.get("charging_cycles")
        health_log.health_percentage = health_data.get("health_percentage")
        
        # Calculate capacity retention if data available
        # Fixed: Use correct field names from JSON definition
        if health_data.get("current_capacity") and health_data.get("original_capacity"):
            health_log.capacity_ah = health_data.get("current_capacity")  # Fixed field name
            health_log.original_capacity_ah = health_data.get("original_capacity")
            health_log.capacity_retention = (health_data.get("current_capacity") / health_data.get("original_capacity")) * 100
        
        # Determine health status
        health_percentage = health_data.get("health_percentage", 100)
        if health_percentage >= 90:
            health_log.health_status = "Excellent"
        elif health_percentage >= 80:
            health_log.health_status = "Good"
        elif health_percentage >= 70:
            health_log.health_status = "Fair"
        elif health_percentage >= 60:
            health_log.health_status = "Poor"
        else:
            health_log.health_status = "Critical"
        
        health_log.insert()
        
        # Update vehicle battery level in base system
        vehicle_doc = frappe.get_doc("TukTuk Vehicle", tuktuk_vehicle)
        vehicle_doc.battery_level = health_data.get("battery_percentage")
        if health_data.get("voltage"):
            vehicle_doc.battery_voltage = health_data.get("voltage")
        vehicle_doc.last_reported = get_datetime()
        vehicle_doc.save()
        
        # Create alerts for low battery health
        if health_percentage < 70:
            create_maintenance_alert(
                tuktuk_vehicle=tuktuk_vehicle,
                alert_type="Low Battery Health",
                message=f"Battery health is {health_percentage}% - Service recommended",
                priority="High" if health_percentage < 60 else "Medium"
            )
        
        return {
            "success": True,
            "health_log": health_log.name,
            "health_status": health_log.health_status
        }
    
    except Exception as e:
        frappe.log_error(f"Error updating battery health: {str(e)}")
        return {"success": False, "error": str(e)}
        
@frappe.whitelist()
def get_maintenance_dashboard():
    """Get maintenance dashboard data"""
    try:
        # Active maintenance records
        active_maintenance = frappe.db.count("TukTuk Maintenance Record", 
                                           {"status": ["in", ["Open", "In Progress"]]})
        
        # Overdue maintenance
        overdue_maintenance = frappe.db.count("TukTuk Maintenance Record", 
                                            {"status": "Open", 
                                             "scheduled_date": ["<", get_datetime()]})
        
        # Vehicles in maintenance
        vehicles_in_maintenance = frappe.db.count("TukTuk Vehicle", {"status": "Maintenance"})
        
        # Critical alerts
        critical_alerts = frappe.db.count("Maintenance Alert", 
                                        {"status": ["in", ["Open", "Acknowledged"]], 
                                         "priority": "Critical"})
        
        # Battery health summary
        battery_health_summary = frappe.db.sql("""
            SELECT 
                AVG(bhl.health_percentage) as avg_health,
                COUNT(DISTINCT bhl.tuktuk_vehicle) as vehicles_tracked,
                COUNT(CASE WHEN bhl.health_percentage < 70 THEN 1 END) as low_health_count
            FROM `tabBattery Health Log` bhl
            INNER JOIN (
                SELECT tuktuk_vehicle, MAX(reading_date) as latest_date
                FROM `tabBattery Health Log`
                GROUP BY tuktuk_vehicle
            ) latest ON bhl.tuktuk_vehicle = latest.tuktuk_vehicle 
                    AND bhl.reading_date = latest.latest_date
        """, as_dict=True)
        
        # Recent maintenance costs
        recent_costs = frappe.db.sql("""
            SELECT SUM(total_cost) as total_cost
            FROM `tabTukTuk Maintenance Record`
            WHERE completed_datetime >= %s
            AND docstatus = 1
        """, [add_days(nowdate(), -30)], as_dict=True)
        
        return {
            "success": True,
            "data": {
                "active_maintenance": active_maintenance,
                "overdue_maintenance": overdue_maintenance,
                "vehicles_in_maintenance": vehicles_in_maintenance,
                "critical_alerts": critical_alerts,
                "battery_health": battery_health_summary[0] if battery_health_summary else {},
                "monthly_cost": recent_costs[0].get("total_cost", 0) if recent_costs else 0
            }
        }
    
    except Exception as e:
        frappe.log_error(f"Error fetching maintenance dashboard: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def generate_maintenance_alerts():
    """Generate maintenance alerts based on schedules and conditions"""
    try:
        alerts_created = 0
        
        # Check for due maintenance schedules
        due_schedules = frappe.db.sql("""
            SELECT name, tuktuk_vehicle, maintenance_type, next_due_date, advance_notice_days
            FROM `tabMaintenance Schedule`
            WHERE is_active = 1
            AND next_due_date <= %s
            AND NOT EXISTS (
                SELECT 1 FROM `tabMaintenance Alert`
                WHERE tuktuk_vehicle = `tabMaintenance Schedule`.tuktuk_vehicle
                AND alert_type = 'Scheduled Maintenance'
                AND status IN ('Open', 'Acknowledged')
            )
        """, [add_days(nowdate(), 7)], as_dict=True)
        
        for schedule in due_schedules:
            create_maintenance_alert(
                tuktuk_vehicle=schedule.tuktuk_vehicle,
                alert_type="Scheduled Maintenance",
                message=f"{schedule.maintenance_type} due on {schedule.next_due_date}",
                priority="Medium",
                due_date=schedule.next_due_date
            )
            alerts_created += 1
        
        # Check for overdue maintenance
        overdue_maintenance = frappe.db.sql("""
            SELECT name, tuktuk_vehicle, maintenance_type, scheduled_date
            FROM `tabTukTuk Maintenance Record`
            WHERE status = 'Open'
            AND scheduled_date < %s
            AND NOT EXISTS (
                SELECT 1 FROM `tabMaintenance Alert`
                WHERE tuktuk_vehicle = `tabTukTuk Maintenance Record`.tuktuk_vehicle
                AND alert_type = 'Overdue Maintenance'
                AND status IN ('Open', 'Acknowledged')
            )
        """, [get_datetime()], as_dict=True)
        
        for maintenance in overdue_maintenance:
            create_maintenance_alert(
                tuktuk_vehicle=maintenance.tuktuk_vehicle,
                alert_type="Overdue Maintenance",
                message=f"Overdue: {maintenance.maintenance_type} was due {maintenance.scheduled_date}",
                priority="High"
            )
            alerts_created += 1
        
        return {
            "success": True,
            "alerts_created": alerts_created,
            "message": f"Generated {alerts_created} maintenance alerts"
        }
    
    except Exception as e:
        frappe.log_error(f"Error generating maintenance alerts: {str(e)}")
        return {"success": False, "error": str(e)}

def create_maintenance_alert(tuktuk_vehicle, alert_type, message, priority="Medium", due_date=None):
    """Helper function to create maintenance alerts"""
    try:
        alert = frappe.new_doc("Maintenance Alert")
        alert.tuktuk_vehicle = tuktuk_vehicle
        alert.alert_type = alert_type
        alert.alert_message = message
        alert.priority = priority
        alert.status = "Open"
        
        if due_date:
            alert.due_date = due_date
        
        alert.insert()
        
        # Send notifications if configured
        send_maintenance_notification(alert)
        
        return alert.name
    
    except Exception as e:
        frappe.log_error(f"Error creating maintenance alert: {str(e)}")
        return None

def send_maintenance_notification(alert):
    """Send notifications for maintenance alerts"""
    try:
        # Get vehicle and driver information
        vehicle = frappe.get_doc("TukTuk Vehicle", alert.tuktuk_vehicle)
        
        # Find assigned driver
        driver = frappe.db.get_value("TukTuk Driver", 
                                   {"assigned_tuktuk": alert.tuktuk_vehicle, "status": "Active"}, 
                                   ["name", "driver_name", "phone_number"])
        
        notification_message = f"Maintenance Alert: {alert.alert_message} for TukTuk {vehicle.tuktuk_id}"
        
        # Send in-app notification
        notification = frappe.new_doc("Notification Log")
        notification.subject = f"Maintenance Alert - {alert.alert_type}"
        notification.message = notification_message
        notification.for_user = driver[0] if driver else None
        notification.type = "Alert"
        notification.insert()
        
        # TODO: Integrate with SMS/Email notifications based on settings
        
    except Exception as e:
        frappe.log_error(f"Error sending maintenance notification: {str(e)}")

def update_vehicle_maintenance_status(tuktuk_vehicle, status):
    """Update vehicle status for maintenance operations"""
    try:
        vehicle = frappe.get_doc("TukTuk Vehicle", tuktuk_vehicle)
        vehicle.status = status
        vehicle.save()
        
        # If setting to maintenance, check if driver needs reassignment
        if status == "Maintenance":
            check_driver_reassignment(tuktuk_vehicle)
        
    except Exception as e:
        frappe.log_error(f"Error updating vehicle maintenance status: {str(e)}")

def check_driver_reassignment(tuktuk_vehicle):
    """Check if driver needs temporary vehicle reassignment during maintenance"""
    try:
        # Get assigned driver
        driver = frappe.db.get_value("TukTuk Driver", 
                                   {"assigned_tuktuk": tuktuk_vehicle, "status": "Active"})
        
        if driver:
            # Check for available vehicles for temporary assignment
            available_vehicles = frappe.db.get_list("TukTuk Vehicle", 
                                                  filters={"status": "Available"},
                                                  fields=["name", "tuktuk_id"])
            
            if available_vehicles:
                # Create notification for driver about temporary reassignment option
                notification = frappe.new_doc("Notification Log")
                notification.subject = "Vehicle Maintenance - Temporary Assignment Available"
                notification.message = f"Your TukTuk is in maintenance. Temporary vehicles available for rental."
                notification.for_user = driver
                notification.type = "Info"
                notification.insert()
        
    except Exception as e:
        frappe.log_error(f"Error checking driver reassignment: {str(e)}")
