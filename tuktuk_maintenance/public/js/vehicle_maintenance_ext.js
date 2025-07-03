// tuktuk_maintenance/public/js/vehicle_maintenance_ext.js
// Extends TukTuk Vehicle form with maintenance functionality

frappe.ui.form.on('TukTuk Vehicle', {
    refresh: function(frm) {
        if (frm.doc.name) {
            // Add maintenance buttons
            add_maintenance_buttons(frm);
            
            // Load maintenance summary
            load_maintenance_summary(frm);
            
            // Show maintenance alerts
            show_vehicle_maintenance_alerts(frm);
        }
    },

    battery_level: function(frm) {
        // Check if battery level is critically low
        if (frm.doc.battery_level && frm.doc.battery_level < 20) {
            frappe.show_alert({
                message: 'Critical battery level detected. Consider maintenance check.',
                indicator: 'red'
            });
        }
    }
});

function add_maintenance_buttons(frm) {
    // Quick maintenance record button
    frm.add_custom_button(__('Create Maintenance'), function() {
        create_maintenance_dialog(frm);
    }, __('Maintenance'));

    // View maintenance history
    frm.add_custom_button(__('Maintenance History'), function() {
        frappe.route_options = {
            "tuktuk_vehicle": frm.doc.name
        };
        frappe.set_route("List", "TukTuk Maintenance Record");
    }, __('Maintenance'));

    // Schedule maintenance
    frm.add_custom_button(__('Schedule Maintenance'), function() {
        schedule_maintenance_dialog(frm);
    }, __('Maintenance'));

    // Battery health log
    frm.add_custom_button(__('Battery Health'), function() {
        frappe.route_options = {
            "tuktuk_vehicle": frm.doc.name
        };
        frappe.set_route("List", "Battery Health Log");
    }, __('Maintenance'));
}

function create_maintenance_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: 'Create Maintenance Record',
        fields: [
            {
                label: 'Maintenance Type',
                fieldname: 'maintenance_type',
                fieldtype: 'Select',
                options: 'Scheduled\nEmergency\nRepair\nBattery Service\nSolar Panel\nTire Service\nBrake Service\nGeneral Inspection',
                reqd: 1
            },
            {
                label: 'Priority',
                fieldname: 'priority',
                fieldtype: 'Select',
                options: 'Low\nMedium\nHigh\nCritical',
                default: 'Medium',
                reqd: 1
            },
            {
                label: 'Issue Description',
                fieldname: 'issue_description',
                fieldtype: 'Text',
                reqd: 1
            },
            {
                label: 'Scheduled Date',
                fieldname: 'scheduled_date',
                fieldtype: 'Datetime',
                default: frappe.datetime.now_datetime(),
                reqd: 1
            }
        ],
        primary_action_label: 'Create',
        primary_action: function(values) {
            frappe.call({
                method: 'tuktuk_maintenance.api.maintenance.create_maintenance_record',
                args: {
                    tuktuk_vehicle: frm.doc.name,
                    maintenance_type: values.maintenance_type,
                    issue_description: values.issue_description,
                    priority: values.priority,
                    scheduled_date: values.scheduled_date
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: 'Maintenance record created successfully',
                            indicator: 'green'
                        });
                        dialog.hide();
                        frm.reload_doc();
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function schedule_maintenance_dialog(frm) {
    const dialog = new frappe.ui.Dialog({
        title: 'Schedule Maintenance',
        fields: [
            {
                label: 'Maintenance Type',
                fieldname: 'maintenance_type',
                fieldtype: 'Select',
                options: 'Daily Check\nWeekly Service\nMonthly Service\nQuarterly Service\nBattery Check\nSolar Panel Cleaning\nTire Rotation\nBrake Inspection',
                reqd: 1
            },
            {
                label: 'Frequency (Days)',
                fieldname: 'frequency_days',
                fieldtype: 'Int',
                default: 30,
                reqd: 1
            },
            {
                label: 'Next Due Date',
                fieldname: 'next_due_date',
                fieldtype: 'Date',
                default: frappe.datetime.add_days(frappe.datetime.nowdate(), 30),
                reqd: 1
            },
            {
                label: 'Description',
                fieldname: 'description',
                fieldtype: 'Text'
            }
        ],
        primary_action_label: 'Schedule',
        primary_action: function(values) {
            frappe.call({
                method: 'tuktuk_maintenance.api.maintenance.schedule_maintenance',
                args: {
                    tuktuk_vehicle: frm.doc.name,
                    maintenance_type: values.maintenance_type,
                    due_date: values.next_due_date,
                    frequency_days: values.frequency_days
                },
                callback: function(r) {
                    if (r.message && r.message.success) {
                        frappe.show_alert({
                            message: 'Maintenance scheduled successfully',
                            indicator: 'green'
                        });
                        dialog.hide();
                    }
                }
            });
        }
    });
    
    dialog.show();
}

function load_maintenance_summary(frm) {
    // Load maintenance summary for the vehicle
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'TukTuk Maintenance Record',
            filters: {
                tuktuk_vehicle: frm.doc.name
            },
            fields: ['status', 'total_cost', 'maintenance_type'],
            limit: 100
        },
        callback: function(r) {
            if (r.message) {
                const summary = calculate_maintenance_summary(r.message);
                display_maintenance_summary(frm, summary);
            }
        }
    });
}

function calculate_maintenance_summary(records) {
    const summary = {
        total_records: records.length,
        total_cost: 0,
        open_records: 0,
        completed_records: 0,
        maintenance_types: {}
    };

    records.forEach(record => {
        summary.total_cost += (record.total_cost || 0);
        
        if (record.status === 'Open' || record.status === 'In Progress') {
            summary.open_records++;
        } else if (record.status === 'Completed') {
            summary.completed_records++;
        }

        if (record.maintenance_type) {
            summary.maintenance_types[record.maintenance_type] = 
                (summary.maintenance_types[record.maintenance_type] || 0) + 1;
        }
    });

    return summary;
}

function display_maintenance_summary(frm, summary) {
    const maintenance_html = `
        <div class="maintenance-summary-card">
            <div class="row">
                <div class="col-md-3">
                    <div class="text-center">
                        <h4>${summary.total_records}</h4>
                        <small class="text-muted">Total Records</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4>${summary.open_records}</h4>
                        <small class="text-muted">Open/In Progress</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4>${summary.completed_records}</h4>
                        <small class="text-muted">Completed</small>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center">
                        <h4>${tuktuk_maintenance.format_currency(summary.total_cost)}</h4>
                        <small class="text-muted">Total Cost</small>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add to maintenance tab if it exists
    if (frm.fields_dict.maintenance_tab) {
        $(frm.fields_dict.maintenance_tab.wrapper).prepend(maintenance_html);
    }
}

function show_vehicle_maintenance_alerts(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Maintenance Alert',
            filters: {
                tuktuk_vehicle: frm.doc.name,
                status: ['in', ['Open', 'Acknowledged']]
            },
            fields: ['alert_message', 'priority', 'due_date'],
            limit: 5
        },
        callback: function(r) {
            if (r.message && r.message.length > 0) {
                let alerts_html = '<div class="maintenance-alerts"><h5>Active Maintenance Alerts</h5>';
                
                r.message.forEach(alert => {
                    const priority_class = alert.priority === 'Critical' ? 'danger' : 
                                         alert.priority === 'High' ? 'warning' : 'info';
                    
                    alerts_html += `
                        <div class="alert alert-${priority_class} alert-dismissible">
                            <strong>${alert.priority}:</strong> ${alert.alert_message}
                            ${alert.due_date ? `<br><small>Due: ${alert.due_date}</small>` : ''}
                        </div>
                    `;
                });
                
                alerts_html += '</div>';
                
                if (frm.fields_dict.maintenance_tab) {
                    $(frm.fields_dict.maintenance_tab.wrapper).prepend(alerts_html);
                }
            }
        }
    });
}
