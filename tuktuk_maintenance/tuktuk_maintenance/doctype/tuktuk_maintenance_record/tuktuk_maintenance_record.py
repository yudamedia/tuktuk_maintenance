# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime

class TukTukMaintenanceRecord(Document):
	def validate(self):
		self.calculate_costs()
		self.validate_dates()
	
	def on_submit(self):
		self.update_vehicle_status()
		self.update_parts_inventory()
		self.calculate_duration()
	
	def calculate_costs(self):
		# Calculate total parts cost
		parts_cost = 0
		for part in self.parts_used:
			if part.quantity and part.unit_cost:
				part.total_cost = flt(part.quantity) * flt(part.unit_cost)
				parts_cost += part.total_cost
		
		self.parts_cost = parts_cost
		
		# Calculate labor cost
		if self.labor_hours and self.labor_rate:
			self.labor_cost = flt(self.labor_hours) * flt(self.labor_rate)
		
		# Calculate total cost
		self.total_cost = flt(self.parts_cost) + flt(self.labor_cost)
	
	def validate_dates(self):
		if self.started_datetime and self.completed_datetime:
			if self.completed_datetime < self.started_datetime:
				frappe.throw("Completed date cannot be before started date")
	
	def update_vehicle_status(self):
		if self.status == "Completed":
			vehicle = frappe.get_doc("TukTuk Vehicle", self.tuktuk_vehicle)
			if vehicle.status == "Maintenance":
				vehicle.status = "Available"
				vehicle.save()
	
	def update_parts_inventory(self):
		for part in self.parts_used:
			if part.part_name and part.quantity:
				part_doc = frappe.get_doc("Maintenance Parts Inventory", part.part_name)
				part_doc.current_stock = flt(part_doc.current_stock) - flt(part.quantity)
				if part_doc.current_stock < 0:
					frappe.throw(f"Insufficient stock for {part.part_name}")
				part_doc.save()
	
	def calculate_duration(self):
		if self.started_datetime and self.completed_datetime:
			duration = (self.completed_datetime - self.started_datetime).total_seconds() / 3600
			self.duration_hours = duration
			self.save()
