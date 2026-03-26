import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class Diagnosis(Document):
	def validate(self):
		self.validate_title()
		self.validate_date()
		self.validate_status_transition()

	def validate_title(self):
		if not self.title or not self.title.strip():
			frappe.throw(_("Diagnosis title is required."))
		self.title = self.title.strip()

	def validate_date(self):
		if self.date and getdate(self.date) > getdate(nowdate()):
			frappe.throw(_("Diagnosis date cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Diagnosis", self.name, "status")
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot change status of a cancelled diagnosis."))

	def before_save(self):
		self.sync_status()

	def sync_status(self):
		"""Keep title as the display field."""
		if not self.title:
			self.title = _("Untitled Diagnosis")
