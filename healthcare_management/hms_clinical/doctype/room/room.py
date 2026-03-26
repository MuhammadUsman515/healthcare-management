import frappe
from frappe import _
from frappe.model.document import Document


class Room(Document):
	def validate(self):
		self.validate_title()
		self.validate_status_transition()

	def validate_title(self):
		if not self.title or not self.title.strip():
			frappe.throw(_("Room name/number is required."))
		self.title = self.title.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Room", self.name, "status")
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot reactivate a cancelled room record."))

	def is_available(self):
		"""Check if room is currently available (Active and no patient)."""
		return self.status == "Active" and not self.patient
