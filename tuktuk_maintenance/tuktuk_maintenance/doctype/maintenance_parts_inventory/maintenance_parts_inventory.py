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
		# Only create alerts if this is not a new record (avoid alerts during initial setup)
		if (flt(self.current_stock) <= flt(self.minimum_stock) and 
		    not self.is_new() and 
		    self.has_value_changed("current_stock")):
			
			# Create low stock alert only when stock actually drops
			existing_alert = frappe.db.exists("Maintenance Alert", {
				"alert_type": "Parts Low Stock",
				"alert_message": ["like", f"%{self.part_name}%"],
				"status": ["in", ["Open", "Acknowledged"]]
			})
			
			if not existing_alert:
				try:
					alert = frappe.new_doc("Maintenance Alert")
					alert.alert_type = "Parts Low Stock"
					alert.alert_message = f"Low stock: {self.part_name} ({self.current_stock} remaining)"
					alert.priority = "Medium"
					alert.status = "Open"
					# For parts alerts, we don't need a specific vehicle
					# Set a placeholder or make tuktuk_vehicle optional in the doctype
					alert.insert()
				except Exception as e:
					# Log the error but don't prevent saving the parts record
					frappe.log_error(f"Could not create low stock alert for {self.part_name}: {str(e)}")
					pass