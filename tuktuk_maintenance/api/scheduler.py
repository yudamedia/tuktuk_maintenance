"""
Scheduled Tasks for Maintenance Management
"""

import frappe
from frappe.utils import nowdate, add_days, get_datetime
from tuktuk_maintenance.api.maintenance import generate_maintenance_alerts, update_battery_health

def check_scheduled_maintenance():
    """Check for scheduled maintenance and create records if needed"""
    try:
        # Get due maintenance schedules
        due_schedules = frappe.db.sql("""
            SELECT name, tuktuk_vehicle, maintenance_type, next_due_date, frequency_days
            FROM `tabMaintenance Schedule`
            WHERE is_active = 1
            AND next_due_date <= %s
        """, [nowdate()], as_dict=True)
        
        for schedule in due_schedules:
            # Check if maintenance record already exists
            existing = frappe.db.exists("TukTuk Maintenance Record", {
                "tuktuk_vehicle": schedule.tuktuk_vehicle,
                "maintenance_schedule": schedule.name,
                "status": ["in", ["Open", "In Progress"]]
            })
            
            if not existing:
                # Create maintenance record
                maintenance_record = frappe.new_doc("TukTuk Maintenance Record")
                maintenance_record.tuktuk_vehicle = schedule.tuktuk_vehicle
                maintenance_record.maintenance_type = schedule.maintenance_type
                maintenance_record.maintenance_schedule = schedule.name
                maintenance_record.scheduled_date = get_datetime()
                maintenance_record.issue_description = f"Scheduled {schedule.maintenance_type}"
                maintenance_record.priority = "Medium"
                maintenance_record.status = "Open"
                maintenance_record.insert()
                
                # Update next due date
                schedule_doc = frappe.get_doc("Maintenance Schedule", schedule.name)
                schedule_doc.last_maintenance = nowdate()
                schedule_doc.next_due_date = add_days(nowdate(), schedule.frequency_days)
                schedule_doc.save()
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error in scheduled maintenance check: {str(e)}")

def update_battery_metrics():
    """Update battery health metrics for all vehicles"""
    try:
        # Get all active vehicles with recent telematics data
        vehicles = frappe.db.sql("""
            SELECT name, tuktuk_id, battery_level, battery_voltage, last_reported
            FROM `tabTukTuk Vehicle`
            WHERE status != 'Offline'
            AND last_reported >= %s
        """, [add_days(get_datetime(), -1)], as_dict=True)
        
        for vehicle in vehicles:
            # Calculate estimated health based on voltage and usage patterns
            estimated_health = calculate_battery_health_estimate(vehicle)
            
            if estimated_health:
                update_battery_health(vehicle.name, {
                    "battery_percentage": vehicle.battery_level,
                    "voltage": vehicle.battery_voltage,
                    "health_percentage": estimated_health,
                    "reading_type": "Automatic"
                })
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error updating battery metrics: {str(e)}")

def calculate_battery_health_estimate(vehicle):
    """Calculate estimated battery health based on available data"""
    try:
        # Get historical battery data
        historical_data = frappe.db.sql("""
            SELECT battery_level, voltage_reading, reading_date
            FROM `tabBattery Health Log`
            WHERE tuktuk_vehicle = %s
            AND reading_date >= %s
            ORDER BY reading_date DESC
            LIMIT 10
        """, [vehicle.name, add_days(get_datetime(), -30)], as_dict=True)
        
        if len(historical_data) < 3:
            return 100  # Default for new vehicles
        
        # Simple health estimation based on voltage degradation
        voltage_readings = [d.voltage_reading for d in historical_data if d.voltage_reading]
        if len(voltage_readings) >= 3:
            avg_voltage = sum(voltage_readings) / len(voltage_readings)
            # Assuming 48V system, calculate health percentage
            nominal_voltage = 48.0
            health_percentage = min(100, (avg_voltage / nominal_voltage) * 100)
            return max(50, health_percentage)  # Minimum 50% to avoid false alarms
        
        return 85  # Default moderate health
        
    except Exception as e:
        frappe.log_error(f"Error calculating battery health: {str(e)}")
        return None

def update_maintenance_schedules():
    """Update maintenance schedules and check for overdue items"""
    try:
        # Update schedules based on completed maintenance
        completed_maintenance = frappe.db.sql("""
            SELECT name, tuktuk_vehicle, maintenance_schedule, completed_datetime, maintenance_type
            FROM `tabTukTuk Maintenance Record`
            WHERE docstatus = 1
            AND completed_datetime >= %s
            AND maintenance_schedule IS NOT NULL
        """, [add_days(nowdate(), -1)], as_dict=True)
        
        for maintenance in completed_maintenance:
            if maintenance.maintenance_schedule:
                schedule_doc = frappe.get_doc("Maintenance Schedule", maintenance.maintenance_schedule)
                schedule_doc.last_maintenance = maintenance.completed_datetime.date()
                
                # Calculate next due date based on frequency
                if schedule_doc.schedule_type == "Time-based":
                    schedule_doc.next_due_date = add_days(
                        maintenance.completed_datetime.date(), 
                        schedule_doc.frequency_days
                    )
                
                schedule_doc.save()
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error updating maintenance schedules: {str(e)}")

def generate_maintenance_reports():
    """Generate weekly maintenance reports"""
    try:
        # Generate summary data for the week
        week_start = add_days(nowdate(), -7)
        
        maintenance_summary = frappe.db.sql("""
            SELECT 
                COUNT(*) as total_maintenance,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as pending,
                SUM(total_cost) as total_cost,
                AVG(duration_hours) as avg_duration
            FROM `tabTukTuk Maintenance Record`
            WHERE creation >= %s
        """, [week_start], as_dict=True)
        
        # Vehicle availability impact
        availability_impact = frappe.db.sql("""
            SELECT 
                COUNT(DISTINCT tuktuk_vehicle) as vehicles_affected,
                SUM(duration_hours) as total_downtime_hours
            FROM `tabTukTuk Maintenance Record`
            WHERE creation >= %s
            AND status = 'Completed'
        """, [week_start], as_dict=True)
        
        # Generate report document (if reporting system exists)
        # This would integrate with ERPNext's reporting system
        
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error(f"Error generating maintenance reports: {str(e)}")

