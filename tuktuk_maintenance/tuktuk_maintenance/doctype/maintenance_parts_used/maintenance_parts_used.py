# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class MaintenancePartsUsed(Document):
	def validate(self):
		self.calculate_total_cost()
		self.get_unit_cost_from_inventory()
	
	def calculate_total_cost(self):
		if self.quantity and self.unit_cost:
			self.total_cost = flt(self.quantity) * flt(self.unit_cost)
	
	def get_unit_cost_from_inventory(self):
		if self.part_name and not self.unit_cost:
			unit_cost = frappe.db.get_value("Maintenance Parts Inventory", self.part_name, "unit_cost")
			if unit_cost:
				self.unit_cost = unit_cost
