# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, add_days, nowdate

class BatteryHealthLog(Document):
	def validate(self):
		self.calculate_capacity_retention()
		self.determine_health_status()
		self.calculate_degradation_rate()
	
	def calculate_capacity_retention(self):
		# Fixed: Use correct field names from JSON definition
		if self.capacity_ah and self.original_capacity_ah:
			self.capacity_retention = (flt(self.capacity_ah) / flt(self.original_capacity_ah)) * 100
	
	def determine_health_status(self):
		if self.health_percentage:
			health = flt(self.health_percentage)
			if health >= 90:
				self.health_status = "Excellent"
			elif health >= 80:
				self.health_status = "Good"
			elif health >= 70:
				self.health_status = "Fair"
			elif health >= 60:
				self.health_status = "Poor"
			else:
				self.health_status = "Critical"
	
	def calculate_degradation_rate(self):
		# Get previous reading to calculate degradation
		previous_reading = frappe.db.sql("""
			SELECT health_percentage, reading_date 
			FROM `tabBattery Health Log`
			WHERE tuktuk_vehicle = %s AND reading_date < %s
			ORDER BY reading_date DESC
			LIMIT 1
		""", [self.tuktuk_vehicle, self.reading_date], as_dict=True)
		
		if previous_reading and self.health_percentage:
			prev_health = flt(previous_reading[0].health_percentage)
			current_health = flt(self.health_percentage)
			
			if prev_health > current_health:
				days_diff = (self.reading_date.date() - previous_reading[0].reading_date.date()).days
				if days_diff > 0:
					monthly_degradation = ((prev_health - current_health) / days_diff) * 30
					self.degradation_rate = monthly_degradation
					
					# Predict end of life (when health drops to 50%)
					if monthly_degradation > 0:
						months_to_eol = (current_health - 50) / monthly_degradation
						self.predicted_eol_date = add_days(nowdate(), int(months_to_eol * 30))
	
	def on_submit(self):
		self.update_vehicle_battery_info()
		self.create_health_alerts()
	
	def update_vehicle_battery_info(self):
		vehicle = frappe.get_doc("TukTuk Vehicle", self.tuktuk_vehicle)
		vehicle.battery_level = self.battery_percentage
		if self.voltage_reading:
			vehicle.battery_voltage = self.voltage_reading
		vehicle.last_reported = self.reading_date
		vehicle.save()
	
	def create_health_alerts(self):
		if self.health_percentage and flt(self.health_percentage) < 70:
			priority = "Critical" if flt(self.health_percentage) < 60 else "High"
			
			# Check if alert already exists
			existing_alert = frappe.db.exists("Maintenance Alert", {
				"tuktuk_vehicle": self.tuktuk_vehicle,
				"alert_type": "Low Battery Health",
				"status": ["in", ["Open", "Acknowledged"]]
			})
			
			if not existing_alert:
				alert = frappe.new_doc("Maintenance Alert")
				alert.tuktuk_vehicle = self.tuktuk_vehicle
				alert.alert_type = "Low Battery Health"
				alert.alert_message = f"Battery health is {self.health_percentage}% - Service recommended"
				alert.priority = priority
				alert.status = "Open"
				alert.insert()