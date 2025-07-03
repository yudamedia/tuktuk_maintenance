"""
Maintenance Analytics and Reporting API
"""

import frappe
from frappe.utils import nowdate, add_days, add_months
from datetime import datetime

@frappe.whitelist()
def get_cost_breakdown(period="monthly", vehicle=None):
    """Get maintenance cost breakdown analysis"""
    try:
        # Determine date range
        if period == "weekly":
            start_date = add_days(nowdate(), -7)
        elif period == "monthly":
            start_date = add_months(nowdate(), -1)
        elif period == "quarterly":
            start_date = add_months(nowdate(), -3)
        else:
            start_date = add_months(nowdate(), -12)
        
        filters = ["completed_datetime >= %s", "docstatus = 1"]
        params = [start_date]
        
        if vehicle:
            filters.append("tuktuk_vehicle = %s")
            params.append(vehicle)
        
        # Cost by maintenance type
        cost_by_type = frappe.db.sql(f"""
            SELECT 
                maintenance_type,
                COUNT(*) as count,
                SUM(total_cost) as total_cost,
                AVG(total_cost) as avg_cost,
                SUM(duration_hours) as total_hours
            FROM `tabTukTuk Maintenance Record`
            WHERE {' AND '.join(filters)}
            GROUP BY maintenance_type
            ORDER BY total_cost DESC
        """, params, as_dict=True)
        
        # Cost by vehicle
        cost_by_vehicle = frappe.db.sql(f"""
            SELECT 
                tmr.tuktuk_vehicle,
                tv.tuktuk_id,
                COUNT(*) as maintenance_count,
                SUM(tmr.total_cost) as total_cost,
                AVG(tmr.total_cost) as avg_cost
            FROM `tabTukTuk Maintenance Record` tmr
            JOIN `tabTukTuk Vehicle` tv ON tmr.tuktuk_vehicle = tv.name
            WHERE {' AND '.join(filters)}
            GROUP BY tmr.tuktuk_vehicle
            ORDER BY total_cost DESC
        """, params, as_dict=True)
        
        # Monthly trend
        monthly_trend = frappe.db.sql(f"""
            SELECT 
                DATE_FORMAT(completed_datetime, '%%Y-%%m') as month,
                COUNT(*) as count,
                SUM(total_cost) as total_cost
            FROM `tabTukTuk Maintenance Record`
            WHERE {' AND '.join(filters)}
            GROUP BY DATE_FORMAT(completed_datetime, '%%Y-%%m')
            ORDER BY month
        """, params, as_dict=True)
        
        return {
            "success": True,
            "data": {
                "cost_by_type": cost_by_type,
                "cost_by_vehicle": cost_by_vehicle,
                "monthly_trend": monthly_trend,
                "period": period,
                "start_date": start_date
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting cost breakdown: {str(e)}")
        return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_downtime_analysis(period="monthly"):
    """Get vehicle downtime analysis"""
    try:
        if period == "weekly":
            start_date = add_days(nowdate(), -7)
        elif period == "monthly":
            start_date = add_months(nowdate(), -1)
        else:
            start_date = add_months(nowdate(), -3)
        
        # Downtime by vehicle
        downtime_by_vehicle = frappe.db.sql("""
            SELECT 
                tmr.tuktuk_vehicle,
                tv.tuktuk_id,
                SUM(tmr.duration_hours) as total_downtime_hours,
                COUNT(*) as maintenance_events,
                AVG(tmr.duration_hours) as avg_downtime_per_event
            FROM `tabTukTuk Maintenance Record` tmr
            JOIN `tabTukTuk Vehicle` tv ON tmr.tuktuk_vehicle = tv.name
            WHERE tmr.completed_datetime >= %s
            AND tmr.docstatus = 1
            GROUP BY tmr.tuktuk_vehicle
            ORDER BY total_downtime_hours DESC
        """, [start_date], as_dict=True)
        
        # Downtime by maintenance type
        downtime_by_type = frappe.db.sql("""
            SELECT 
                maintenance_type,
                SUM(duration_hours) as total_downtime_hours,
                COUNT(*) as count,
                AVG(duration_hours) as avg_downtime
            FROM `tabTukTuk Maintenance Record`
            WHERE completed_datetime >= %s
            AND docstatus = 1
            GROUP BY maintenance_type
            ORDER BY total_downtime_hours DESC
        """, [start_date], as_dict=True)
        
        # Calculate impact on revenue (estimated)
        # Assume average revenue per hour based on base system data
        avg_revenue_per_hour = frappe.db.sql("""
            SELECT AVG(daily_target) / 18 as avg_hourly_revenue
            FROM `tabTukTuk Settings`
        """, as_dict=True)
        
        estimated_revenue_loss = 0
        if avg_revenue_per_hour and avg_revenue_per_hour[0].get('avg_hourly_revenue'):
            total_downtime = sum([d.total_downtime_hours for d in downtime_by_vehicle])
            estimated_revenue_loss = total_downtime * avg_revenue_per_hour[0]['avg_hourly_revenue']
        
        return {
            "success": True,
            "data": {
                "downtime_by_vehicle": downtime_by_vehicle,
                "downtime_by_type": downtime_by_type,
                "estimated_revenue_loss": estimated_revenue_loss,
                "period": period
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error getting downtime analysis: {str(e)}")
        return {"success": False, "error": str(e)}
