import frappe
from frappe import _

def execute():
    """Create TukTuk Maintenance workspace"""
    
    workspace_name = "TukTuk Maintenance"
    
    # Check if workspace already exists
    if frappe.db.exists("Workspace", workspace_name):
        print(f"✅ Workspace '{workspace_name}' already exists")
        return
    
    try:
        # Create new workspace
        workspace = frappe.new_doc("Workspace")
        workspace.name = workspace_name
        workspace.label = workspace_name
        workspace.category = "Modules"
        workspace.module = "TukTuk Maintenance"
        workspace.icon = "🔧"
        workspace.is_standard = 1
        workspace.public = 1
        workspace.title = workspace_name
        workspace.sequence_id = 2.0
        
        # Set the content (dashboard layout)
        workspace.content = '[{"id":"header_title","type":"header","data":{"text":"<span class=\\"h4\\">TukTuk Maintenance Dashboard</span>","col":12}},{"id":"_2M0EP2sfb","type":"number_card","data":{"number_card_name":"Total Maintenance Records","col":3}},{"id":"hXhM_DwW2F","type":"number_card","data":{"number_card_name":"Active Maintenance","col":3}},{"id":"32xM_R8vPw","type":"number_card","data":{"number_card_name":"Critical Alerts","col":3}},{"id":"44xM_R8vPw","type":"number_card","data":{"number_card_name":"Low Battery Health","col":3}},{"id":"spacer_1","type":"spacer","data":{"col":12}},{"id":"button_row_1","type":"shortcut","data":{"shortcut_name":"Maintenance Records","col":3}},{"id":"button_row_2","type":"shortcut","data":{"shortcut_name":"Battery Health","col":3}},{"id":"button_row_3","type":"shortcut","data":{"shortcut_name":"Parts Inventory","col":3}},{"id":"button_row_4","type":"shortcut","data":{"shortcut_name":"Maintenance Alerts","col":3}},{"id":"spacer_2","type":"spacer","data":{"col":12}},{"id":"quick_lists_1","type":"quick_list","data":{"quick_list_name":"Overdue Maintenance","col":4}},{"id":"quick_lists_2","type":"quick_list","data":{"quick_list_name":"Low Stock Parts","col":4}},{"id":"quick_lists_3","type":"quick_list","data":{"quick_list_name":"Recent Battery Readings","col":4}}]'
        
        # Add number cards
        number_cards = [
            {
                "document_type": "TukTuk Maintenance Record",
                "label": "Total Maintenance Records",
                "number_card_name": "Total Maintenance Records",
                "function": "Count",
                "filters_json": "[]",
                "is_public": 1
            },
            {
                "document_type": "TukTuk Maintenance Record", 
                "label": "Active Maintenance",
                "number_card_name": "Active Maintenance",
                "function": "Count",
                "filters_json": '[[\"TukTuk Maintenance Record\",\"status\",\"in\",[\"Open\",\"In Progress\"],false]]',
                "is_public": 1
            },
            {
                "document_type": "Maintenance Alert",
                "label": "Critical Alerts", 
                "number_card_name": "Critical Alerts",
                "function": "Count",
                "filters_json": '[[\"Maintenance Alert\",\"priority\",\"=\",\"Critical\",false],[\"Maintenance Alert\",\"status\",\"in\",[\"Open\",\"Acknowledged\"],false]]',
                "is_public": 1
            },
            {
                "document_type": "Battery Health Log",
                "label": "Low Battery Health",
                "number_card_name": "Low Battery Health", 
                "function": "Count",
                "filters_json": '[[\"Battery Health Log\",\"health_status\",\"in\",[\"Poor\",\"Critical\"],false]]',
                "is_public": 1
            }
        ]
        
        for card in number_cards:
            workspace.append("number_cards", card)
        
        # Add shortcuts
        shortcuts = [
            {
                "type": "DocType",
                "link_to": "TukTuk Maintenance Record",
                "label": "Maintenance Records",
                "color": "orange",
                "stats_filter": '[[\"TukTuk Maintenance Record\",\"status\",\"in\",[\"Open\",\"In Progress\"],false]]',
                "format": "{} Active"
            },
            {
                "type": "DocType", 
                "link_to": "Battery Health Log",
                "label": "Battery Health",
                "color": "green",
                "stats_filter": "[]",
                "format": "{} Records"
            },
            {
                "type": "DocType",
                "link_to": "Maintenance Parts Inventory", 
                "label": "Parts Inventory",
                "color": "blue",
                "stats_filter": "[]",
                "format": "{} Items"
            },
            {
                "type": "DocType",
                "link_to": "Maintenance Alert",
                "label": "Maintenance Alerts",
                "color": "red", 
                "stats_filter": '[[\"Maintenance Alert\",\"priority\",\"=\",\"Critical\",false]]',
                "format": "{} Critical"
            }
        ]
        
        for shortcut in shortcuts:
            workspace.append("shortcuts", shortcut)
        
        # Add quick lists
        quick_lists = [
            {
                "document_type": "TukTuk Maintenance Record",
                "label": "Overdue Maintenance",
                "quick_list_name": "Overdue Maintenance",
                "quick_list_filter": '[[\"status\",\"=\",\"Open\"],[\"scheduled_date\",\"<\",\"Today\"]]'
            },
            {
                "document_type": "Maintenance Parts Inventory",
                "label": "Low Stock Parts", 
                "quick_list_name": "Low Stock Parts",
                "quick_list_filter": '[[\"current_stock\",\"<=\",\"minimum_stock\"]]'
            },
            {
                "document_type": "Battery Health Log",
                "label": "Recent Battery Readings",
                "quick_list_name": "Recent Battery Readings", 
                "quick_list_filter": "[]"
            }
        ]
        
        for quick_list in quick_lists:
            workspace.append("quick_lists", quick_list)
        
        # Add sidebar links
        links = [
            {
                "label": "Maintenance Operations",
                "type": "Card Break"
            },
            {
                "type": "DocType",
                "link_to": "TukTuk Maintenance Record",
                "label": "TukTuk Maintenance Record"
            },
            {
                "type": "DocType", 
                "link_to": "Maintenance Schedule",
                "label": "Maintenance Schedule"
            },
            {
                "type": "DocType",
                "link_to": "Battery Health Log", 
                "label": "Battery Health Log"
            },
            {
                "type": "DocType",
                "link_to": "Maintenance Alert",
                "label": "Maintenance Alert"
            },
            {
                "label": "Inventory Management", 
                "type": "Card Break"
            },
            {
                "type": "DocType",
                "link_to": "Maintenance Parts Inventory",
                "label": "Maintenance Parts Inventory"
            },
            {
                "label": "Reports & Analytics",
                "type": "Card Break"
            },
            {
                "type": "Report",
                "link_to": "Maintenance Cost Analysis", 
                "label": "Maintenance Cost Analysis",
                "is_query_report": 1
            },
            {
                "type": "Report",
                "link_to": "Battery Health Report",
                "label": "Battery Health Report",
                "is_query_report": 1
            }
        ]
        
        for link in links:
            workspace.append("links", link)
        
        # Save the workspace
        workspace.insert()
        
        print(f"✅ Successfully created '{workspace_name}' workspace")
        
    except Exception as e:
        print(f"❌ Error creating workspace: {str(e)}")
        frappe.log_error(f"Workspace creation error: {str(e)}")
