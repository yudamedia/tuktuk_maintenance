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
    
    return columns, data, None, chart

def get_columns():
    return [
        {
            "label": _("Vehicle ID"),
            "fieldname": "tuktuk_id",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Maintenance Type"),
            "fieldname": "maintenance_type",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Date"),
            "fieldname": "completed_datetime",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Duration (Hours)"),
            "fieldname": "duration_hours",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("Parts Cost"),
            "fieldname": "parts_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Labor Cost"),
            "fieldname": "labor_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Total Cost"),
            "fieldname": "total_cost",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = []
    
    if filters.get("from_date"):
        conditions.append("tmr.completed_datetime >= %(from_date)s")
    
    if filters.get("to_date"):
        conditions.append("tmr.completed_datetime <= %(to_date)s")
    
    if filters.get("tuktuk_vehicle"):
        conditions.append("tmr.tuktuk_vehicle = %(tuktuk_vehicle)s")
    
    if filters.get("maintenance_type"):
        conditions.append("tmr.maintenance_type = %(maintenance_type)s")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Check if the maintenance table exists
    if not frappe.db.exists("DocType", "TukTuk Maintenance Record"):
        return []
    
    try:
        data = frappe.db.sql(f"""
            SELECT 
                COALESCE(tv.tuktuk_id, tmr.tuktuk_vehicle) as tuktuk_id,
                tmr.maintenance_type,
                tmr.completed_datetime,
                tmr.duration_hours,
                tmr.parts_cost,
                tmr.labor_cost,
                tmr.total_cost,
                tmr.status
            FROM `tabTukTuk Maintenance Record` tmr
            LEFT JOIN `tabTukTuk Vehicle` tv ON tmr.tuktuk_vehicle = tv.name
            WHERE {where_clause} AND tmr.docstatus = 1
            ORDER BY tmr.completed_datetime DESC
        """, filters, as_dict=1)
        
        return data
    except Exception as e:
        frappe.log_error(f"Error in Maintenance Cost Analysis: {str(e)}")
        return []

def get_chart_data(data):
    if not data:
        return None
        
    # Group by maintenance type for chart
    maintenance_costs = {}
    
    for row in data:
        mtype = row.get("maintenance_type", "Unknown")
        cost = flt(row.get("total_cost", 0))
        
        if mtype in maintenance_costs:
            maintenance_costs[mtype] += cost
        else:
            maintenance_costs[mtype] = cost
    
    if not maintenance_costs:
        return None
    
    return {
        "data": {
            "labels": list(maintenance_costs.keys()),
            "datasets": [
                {
                    "name": "Total Cost",
                    "values": list(maintenance_costs.values())
                }
            ]
        },
        "type": "donut",
        "height": 300
    }
