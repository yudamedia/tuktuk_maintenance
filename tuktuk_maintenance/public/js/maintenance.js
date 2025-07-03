// tuktuk_maintenance/public/js/maintenance.js
// Main JavaScript for maintenance system

tuktuk_maintenance = {
    // Initialize maintenance system
    init: function() {
        this.setup_dashboard_widgets();
        this.setup_maintenance_alerts();
    },

    // Setup dashboard widgets
    setup_dashboard_widgets: function() {
        if (frappe.get_route()[0] === 'Workspaces' && frappe.get_route()[1] === 'TukTuk Maintenance') {
            this.load_maintenance_dashboard();
        }
    },

    // Load maintenance dashboard data
    load_maintenance_dashboard: function() {
        frappe.call({
            method: 'tuktuk_maintenance.api.maintenance.get_maintenance_dashboard',
            callback: function(r) {
                if (r.message && r.message.success) {
                    tuktuk_maintenance.render_dashboard_widgets(r.message.data);
                }
            }
        });
    },

    // Render dashboard widgets
    render_dashboard_widgets: function(data) {
        // Update maintenance summary cards
        $('.maintenance-summary').each(function() {
            const card_type = $(this).data('type');
            const value = data[card_type] || 0;
            $(this).find('.widget-content').text(value);
        });

        // Update battery health indicator
        if (data.battery_health && data.battery_health.avg_health) {
            const health = Math.round(data.battery_health.avg_health);
            $('.battery-health-indicator').html(`
                <div class="progress">
                    <div class="progress-bar ${this.get_health_color(health)}" 
                         style="width: ${health}%">${health}%</div>
                </div>
            `);
        }

        // Update cost information
        if (data.monthly_cost) {
            $('.monthly-cost-value').text(
                'KSH ' + parseFloat(data.monthly_cost).toLocaleString('en-KE')
            );
        }
    },

    // Get health color based on percentage
    get_health_color: function(health) {
        if (health >= 90) return 'bg-success';
        if (health >= 70) return 'bg-warning';
        return 'bg-danger';
    },

    // Setup maintenance alerts
    setup_maintenance_alerts: function() {
        // Check for maintenance alerts on page load
        this.check_maintenance_alerts();
        
        // Set up periodic alert checking
        setInterval(() => {
            this.check_maintenance_alerts();
        }, 300000); // Check every 5 minutes
    },

    // Check for maintenance alerts
    check_maintenance_alerts: function() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Maintenance Alert',
                filters: {
                    status: ['in', ['Open', 'Acknowledged']],
                    priority: ['in', ['High', 'Critical']]
                },
                fields: ['name', 'alert_message', 'priority', 'tuktuk_vehicle'],
                limit: 5
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    tuktuk_maintenance.show_maintenance_alerts(r.message);
                }
            }
        });
    },

    // Show maintenance alerts
    show_maintenance_alerts: function(alerts) {
        alerts.forEach(alert => {
            const indicator = alert.priority === 'Critical' ? 'red' : 'orange';
            
            frappe.show_alert({
                message: `Maintenance Alert: ${alert.alert_message}`,
                indicator: indicator
            }, 10);
        });
    },

    // Create maintenance record helper
    create_maintenance_record: function(tuktuk_vehicle, maintenance_type, description) {
        frappe.call({
            method: 'tuktuk_maintenance.api.maintenance.create_maintenance_record',
            args: {
                tuktuk_vehicle: tuktuk_vehicle,
                maintenance_type: maintenance_type,
                issue_description: description
            },
            callback: function(r) {
                if (r.message && r.message.success) {
                    frappe.show_alert({
                        message: 'Maintenance record created successfully',
                        indicator: 'green'
                    });
                    // Refresh current page if it's a maintenance list
                    if (cur_list && cur_list.doctype === 'TukTuk Maintenance Record') {
                        cur_list.refresh();
                    }
                } else {
                    frappe.show_alert({
                        message: r.message.error || 'Error creating maintenance record',
                        indicator: 'red'
                    });
                }
            }
        });
    },

    // Format currency for display
    format_currency: function(amount) {
        if (!amount) return 'KSH 0';
        return 'KSH ' + parseFloat(amount).toLocaleString('en-KE', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        });
    },

    // Get maintenance status color
    get_maintenance_status_color: function(status) {
        const colors = {
            'Open': 'orange',
            'In Progress': 'blue',
            'Completed': 'green',
            'Cancelled': 'red'
        };
        return colors[status] || 'grey';
    }
};

// Initialize when page loads
$(document).ready(function() {
    tuktuk_maintenance.init();
});
