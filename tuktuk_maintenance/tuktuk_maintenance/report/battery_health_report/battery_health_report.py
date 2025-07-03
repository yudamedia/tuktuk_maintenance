# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    if not filters:
        filters = {}
    
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data) if data else None
    summary = get_summary_data(data) if data else []
    
    return columns, data, None, chart, summary

def get_columns():
    return [
        {
            "label": _("Vehicle ID"),
            "fieldname": "tuktuk_id",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Reading Date"),
            "fieldname": "reading_date",
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "label": _("Battery Level (%)"),
            "fieldname": "battery_percentage",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "label": _("Health (%)"),
            "fieldname": "health_percentage",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Voltage (V)"),
            "fieldname": "voltage_reading",
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "label": _("Temperature (°C)"),
            "fieldname": "temperature",
            "fieldtype": "Float",
            "precision": 1,
            "width": 120
        },
        {
            "label": _("Health Status"),
            "fieldname": "health_status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Estimated Range (km)"),
            "fieldname": "estimated_range_km",
            "fieldtype": "Float",
            "precision": 1,
            "width": 140
        }
    ]

def get_data(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("bhl.reading_date >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("bhl.reading_date <= %(to_date)s")
    
    if filters.get("tuktuk_vehicle"):
        conditions.append("bhl.tuktuk_vehicle = %(tuktuk_vehicle)s")
    
    if filters.get("health_status"):
        conditions.append("bhl.health_status = %(health_status)s")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Check if the battery health table exists
    if not frappe.db.exists("DocType", "Battery Health Log"):
        return []
    
    try:
        # Get latest reading for each vehicle if no date filters
        if not filters.get("from_date") and not filters.get("to_date"):
            data = frappe.db.sql(f"""
                SELECT 
                    COALESCE(tv.tuktuk_id, bhl.tuktuk_vehicle) as tuktuk_id,
                    bhl.reading_date,
                    bhl.battery_percentage,
                    bhl.health_percentage,
                    bhl.voltage_reading,
                    bhl.temperature,
                    bhl.health_status,
                    bhl.estimated_range_km
                FROM `tabBattery Health Log` bhl
                INNER JOIN (
                    SELECT tuktuk_vehicle, MAX(reading_date) as latest_date
                    FROM `tabBattery Health Log`
                    WHERE {where_clause}
                    GROUP BY tuktuk_vehicle
                ) latest ON bhl.tuktuk_vehicle = latest.tuktuk_vehicle 
                        AND bhl.reading_date = latest.latest_date
                LEFT JOIN `tabTukTuk Vehicle` tv ON bhl.tuktuk_vehicle = tv.name
                ORDER BY bhl.health_percentage ASC
            """, filters, as_dict=1)
        else:
            data = frappe.db.sql(f"""
                SELECT 
                    COALESCE(tv.tuktuk_id, bhl.tuktuk_vehicle) as tuktuk_id,
                    bhl.reading_date,
                    bhl.battery_percentage,
                    bhl.health_percentage,
                    bhl.voltage_reading,
                    bhl.temperature,
                    bhl.health_status,
                    bhl.estimated_range_km
                FROM `tabBattery Health Log` bhl
                LEFT JOIN `tabTukTuk Vehicle` tv ON bhl.tuktuk_vehicle = tv.name
                WHERE {where_clause}
                ORDER BY bhl.reading_date DESC
            """, filters, as_dict=1)
        
        return data
    except Exception as e:
        frappe.log_error(f"Error in Battery Health Report: {str(e)}")
        return []

def get_chart_data(data):
    if not data:
        return None
        
    # Health status distribution
    health_distribution = {}
    
    for row in data:
        status = row.get("health_status", "Unknown")
        if status in health_distribution:
            health_distribution[status] += 1
        else:
            health_distribution[status] = 1
    
    if not health_distribution:
        return None
    
    return {
        "data": {
            "labels": list(health_distribution.keys()),
            "datasets": [
                {
                    "name": "Vehicle Count",
                    "values": list(health_distribution.values())
                }
            ]
        },
        "type": "pie",
        "height": 300
    }

def get_summary_data(data):
    if not data:
        return []
    
    total_vehicles = len(data)
    avg_health = sum([flt(row.get("health_percentage", 0)) for row in data]) / total_vehicles if total_vehicles > 0 else 0
    critical_count = len([row for row in data if row.get("health_status") == "Critical"])
    poor_count = len([row for row in data if row.get("health_status") == "Poor"])
    
    return [
        {
            "label": _("Total Vehicles Monitored"),
            "value": total_vehicles,
            "datatype": "Int"
        },
        {
            "label": _("Average Fleet Health"),
            "value": f"{avg_health:.1f}%",
            "datatype": "Data"
        },
        {
            "label": _("Critical Health Vehicles"),
            "value": critical_count,
            "datatype": "Int"
        },
        {
            "label": _("Poor Health Vehicles"),
            "value": poor_count,
            "datatype": "Int"
        }
    ]
