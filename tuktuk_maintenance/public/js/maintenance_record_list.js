// tuktuk_maintenance/public/js/maintenance_record_list.js
// Enhanced list view for maintenance records

frappe.listview_settings['TukTuk Maintenance Record'] = {
    add_fields: ["status", "priority", "maintenance_type", "total_cost", "scheduled_date", "tuktuk_vehicle"],
    
    get_indicator: function(doc) {
        const status_colors = {
            "Open": "orange",
            "In Progress": "blue", 
            "Completed": "green",
            "Cancelled": "red"
        };
        
        return [__(doc.status), status_colors[doc.status] || "gray", "status,=," + doc.status];
    },
    
    onload: function(listview) {
        // Add custom buttons
        listview.page.add_menu_item(__("Generate Maintenance Report"), function() {
            generate_maintenance_report();
        });
        
        listview.page.add_menu_item(__("Check Due Maintenance"), function() {
            check_due_maintenance();
        });
        
        // Add filters
        listview.page.add_field({
            fieldtype: "Select",
            label: "Priority",
            fieldname: "priority_filter",
            options: "\nLow\nMedium\nHigh\nCritical",
            change: function() {
                const priority = this.get_value();
                if (priority) {
                    listview.filter_area.add([[listview.doctype, "priority", "=", priority]]);
                }
            }
        });
    },
    
    formatters: {
        total_cost: function(value) {
            if (value) {
                return tuktuk_maintenance.format_currency(value);
            }
            return "";
        },
        
        scheduled_date: function(value) {
            if (value) {
                const date = frappe.datetime.str_to_obj(value);
                const now = new Date();
                
                if (date < now) {
                    return `<span class="text-danger">${frappe.datetime.str_to_user(value)}</span>`;
                }
                return frappe.datetime.str_to_user(value);
            }
            return "";
        }
    }
};

function generate_maintenance_report() {
    frappe.set_route('query-report', 'Maintenance Cost Analysis');
}

function check_due_maintenance() {
    frappe.call({
        method: 'tuktuk_maintenance.api.maintenance.generate_maintenance_alerts',
        callback: function(r) {
            if (r.message && r.message.success) {
                frappe.show_alert({
                    message: `Generated ${r.message.alerts_created} maintenance alerts`,
                    indicator: 'green'
                });
                cur_list.refresh();
            }
        }
    });
}
