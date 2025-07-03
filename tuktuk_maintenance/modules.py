def get_data():
    return [
        {
            "label": "TukTuk Maintenance",
            "icon": "fa fa-wrench",
            "items": [
                {
                    "type": "doctype",
                    "name": "TukTuk Maintenance Record",
                    "label": "Maintenance Records",
                    "description": "Track maintenance activities"
                },
                {
                    "type": "doctype", 
                    "name": "Maintenance Schedule",
                    "label": "Maintenance Schedule",
                    "description": "Schedule preventive maintenance"
                },
                {
                    "type": "doctype",
                    "name": "Maintenance Parts Inventory",
                    "label": "Parts Inventory",
                    "description": "Manage spare parts"
                },
                {
                    "type": "report",
                    "name": "Maintenance Cost Analysis",
                    "label": "Cost Analysis",
                    "description": "Analyze maintenance costs"
                },
                {
                    "type": "report", 
                    "name": "Battery Health Report",
                    "label": "Battery Health",
                    "description": "Monitor battery performance"
                }
            ]
        }
    ]
