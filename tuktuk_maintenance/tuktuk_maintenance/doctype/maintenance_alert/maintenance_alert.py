# Copyright (c) 2025, Yuda Media and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MaintenanceAlert(Document):
	def validate(self):
		if self.status == "Acknowledged" and not self.acknowledged_by:
			self.acknowledged_by = frappe.session.user
			self.acknowledged_date = frappe.utils.now()
		
		if self.status == "Resolved" and not self.resolved_date:
			self.resolved_date = frappe.utils.now()
	
	def on_submit(self):
		self.send_notifications()
	
	def send_notifications(self):
		# Send notifications based on alert type and priority
		if self.priority in ["High", "Critical"]:
			# Send immediate notification
			frappe.publish_realtime(
				event="maintenance_alert",
				message={
					"alert_type": self.alert_type,
					"message": self.alert_message,
					"priority": self.priority,
					"vehicle": self.tuktuk_vehicle
				},
				user=self.assigned_to
			)
