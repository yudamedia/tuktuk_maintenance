# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate

class MaintenanceSchedule(Document):
	def validate(self):
		self.calculate_next_due_date()
	
	def calculate_next_due_date(self):
		if self.schedule_type == "Time-based" and self.frequency_days:
			if self.last_maintenance:
				self.next_due_date = add_days(self.last_maintenance, self.frequency_days)
			elif not self.next_due_date:
				self.next_due_date = add_days(nowdate(), self.frequency_days)
