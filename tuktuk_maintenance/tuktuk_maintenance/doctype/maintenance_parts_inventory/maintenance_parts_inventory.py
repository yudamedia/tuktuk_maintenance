# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MaintenancePartsInventory(Document):
	def validate(self):
		self.calculate_total_value()
		self.check_stock_levels()
	
	def calculate_total_value(self):
		if self.current_stock and self.unit_cost:
			self.total_value = flt(self.current_stock) * flt(self.unit_cost)
	
	def check_stock_levels(self):
		if flt(self.current_stock) <= flt(self.minimum_stock):
			# Create low stock alert
			existing_alert = frappe.db.exists("Maintenance Alert", {
				"alert_type": "Parts Low Stock",
				"alert_message": ["like", f"%{self.part_name}%"],
				"status": ["in", ["Open", "Acknowledged"]]
			})
			
			if not existing_alert:
				alert = frappe.new_doc("Maintenance Alert")
				alert.alert_type = "Parts Low Stock"
				alert.alert_message = f"Low stock: {self.part_name} ({self.current_stock} remaining)"
				alert.priority = "Medium"
				alert.status = "Open"
				alert.insert()
