"""
Create Number Cards for TukTuk Maintenance during installation
"""

import frappe

def create_maintenance_number_cards():
    """Create Number Cards for TukTuk Maintenance workspace"""
    
    number_cards = [
        {
            "number_card_name": "Total Maintenance Records",
            "label": "Total Maintenance Records",
            "document_type": "TukTuk Maintenance Record", 
            "function": "Count",
            "filters_json": "[]",
            "is_public": 1,
            "show_percentage_stats": 1,
            "stats_time_interval": "Daily"
        },
        {
            "number_card_name": "Active Maintenance",
            "label": "Active Maintenance",
            "document_type": "TukTuk Maintenance Record",
            "function": "Count", 
            "filters_json": '[["TukTuk Maintenance Record","status","in",["Open","In Progress"],false]]',
            "is_public": 1,
            "show_percentage_stats": 1,
            "stats_time_interval": "Daily"
        },
        {
            "number_card_name": "Critical Alerts", 
            "label": "Critical Alerts",
            "document_type": "Maintenance Alert",
            "function": "Count",
            "filters_json": '[["Maintenance Alert","priority","=","Critical",false],["Maintenance Alert","status","in",["Open","Acknowledged"],false]]',
            "is_public": 1,
            "show_percentage_stats": 1,
            "stats_time_interval": "Daily"
        },
        {
            "number_card_name": "Low Battery Health",
            "label": "Low Battery Health", 
            "document_type": "Battery Health Log",
            "function": "Count",
            "filters_json": '[["Battery Health Log","health_status","in",["Poor","Critical"],false]]',
            "is_public": 1,
            "show_percentage_stats": 1,
            "stats_time_interval": "Daily"
        }
    ]
    
    created_cards = 0
    for card_data in number_cards:
        try:
            # Check if card already exists
            if not frappe.db.exists("Number Card", card_data["number_card_name"]):
                card = frappe.new_doc("Number Card")
                card.update(card_data)
                card.insert()
                created_cards += 1
                print(f"✅ Created Number Card: {card_data['number_card_name']}")
            else:
                print(f"⏭️  Number Card already exists: {card_data['number_card_name']}")
        except Exception as e:
            print(f"❌ Error creating Number Card {card_data['number_card_name']}: {str(e)}")
    
    frappe.db.commit()
    print(f"\n🎉 Created {created_cards} Number Cards successfully!")
    
    return created_cards

if __name__ == "__main__":
    create_maintenance_number_cards()
