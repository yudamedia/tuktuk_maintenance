app_name = "tuktuk_maintenance"
app_title = "TukTuk Maintenance"
app_publisher = "Yuda Media"
app_description = "Maintenance Management Addon for Sunny TukTuk Fleet"
app_email = "yuda@graphicshop.co.ke"
app_license = "MIT"
app_version = "0.1.0"

# App styling - FIXED: Proper CSS path and loading order
app_include_css = [
    "/assets/tuktuk_maintenance/css/maintenance_workspace.css"
]

app_include_js = [
    "/assets/tuktuk_maintenance/js/maintenance.js"
]

# Website includes for proper loading


app_icon = "fa fa-wrench"
app_color = "orange"

# Whitelisted API methods
whitelisted_methods = [
    "tuktuk_maintenance.api.maintenance.create_maintenance_record",
    "tuktuk_maintenance.api.maintenance.schedule_maintenance",
    "tuktuk_maintenance.api.maintenance.update_battery_health",
    "tuktuk_maintenance.api.maintenance.get_maintenance_dashboard",
    "tuktuk_maintenance.api.maintenance.generate_maintenance_alerts"
]

# Scheduled tasks
scheduler_events = {
    "cron": {
        "*/30 * * * *": [
            "tuktuk_maintenance.api.scheduler.check_scheduled_maintenance"
        ],
        "0 * * * *": [
            "tuktuk_maintenance.api.scheduler.update_battery_metrics"
        ]
    },
    "daily": [
        "tuktuk_maintenance.api.scheduler.generate_maintenance_alerts",
        "tuktuk_maintenance.api.scheduler.update_maintenance_schedules"
    ]
}

# Installation hooks
after_install = "tuktuk_maintenance.setup.install.after_install"

# Client scripts for enhanced UI
doctype_js = {
    "TukTuk Vehicle": "public/js/vehicle_maintenance_ext.js",
    "TukTuk Driver": "public/js/driver_maintenance_ext.js"
}

doctype_list_js = {
    "TukTuk Maintenance Record": "public/js/maintenance_record_list.js",
    "Maintenance Schedule": "public/js/maintenance_schedule_list.js"
}

# Document event hooks - integrate with base system
doc_events = {
    "TukTuk Vehicle": {
        "validate": "tuktuk_maintenance.api.hooks.vehicle_validate",
        "on_update": "tuktuk_maintenance.api.hooks.vehicle_on_update"
    },
    "TukTuk Maintenance Record": {
        "on_submit": "tuktuk_maintenance.api.hooks.maintenance_on_submit",
        "on_cancel": "tuktuk_maintenance.api.hooks.maintenance_on_cancel"
    }
}

# Custom permissions
permission_query_conditions = {
    "TukTuk Maintenance Record": "tuktuk_maintenance.api.permissions.maintenance_query_conditions",
    "Battery Health Log": "tuktuk_maintenance.api.permissions.battery_health_query_conditions", 
    "Maintenance Parts Inventory": "tuktuk_maintenance.api.permissions.parts_inventory_query_conditions",
    "Maintenance Alert": "tuktuk_maintenance.api.permissions.maintenance_alert_query_conditions"
}

# Custom fields to extend base doctypes (will be created during installation)
custom_fields = {
    "TukTuk Vehicle": [
        {
            "fieldname": "maintenance_tab",
            "fieldtype": "Tab Break",
            "label": "Maintenance",
            "insert_after": "location_tab"
        },
        {
            "fieldname": "maintenance_info_section",
            "fieldtype": "Section Break", 
            "label": "Maintenance Information",
            "insert_after": "maintenance_tab"
        },
        {
            "fieldname": "last_maintenance_date",
            "fieldtype": "Date",
            "label": "Last Maintenance",
            "insert_after": "maintenance_info_section"
        },
        {
            "fieldname": "next_maintenance_due",
            "fieldtype": "Date",
            "label": "Next Maintenance Due", 
            "insert_after": "last_maintenance_date"
        },
        {
            "fieldname": "maintenance_status",
            "fieldtype": "Select",
            "label": "Maintenance Status",
            "options": "Good\nNeeds Attention\nCritical\nOverdue",
            "default": "Good",
            "insert_after": "next_maintenance_due"
        },
        {
            "fieldname": "column_break_maintenance",
            "fieldtype": "Column Break",
            "insert_after": "maintenance_status"
        },
        {
            "fieldname": "total_maintenance_cost",
            "fieldtype": "Currency",
            "label": "Total Maintenance Cost",
            "read_only": 1,
            "insert_after": "column_break_maintenance"
        }
    ]
}

# Boot session - ensures CSS loads properly
boot_session = "tuktuk_maintenance.boot.boot_session"

# Fixtures for workspace and charts
fixtures = [
    {
        "doctype": "Number Card",
        "filters": [
            ["name", "in", [
                "Total Maintenance Records",
                "Active Maintenance", 
                "Critical Alerts",
                "Low Battery Health"
            ]]
        ]
    },
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["TukTuk Maintenance"]]
        ]
    }
]