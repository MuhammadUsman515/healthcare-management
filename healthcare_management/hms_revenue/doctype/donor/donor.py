import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class Donor(Document):
	def validate(self):
		self.validate_title()
		self.validate_amount()
		self.validate_date()
		self.validate_status_transition()

	def validate_title(self):
		if not self.title or not self.title.strip():
			frappe.throw(_("Donor name is required."))
		self.title = self.title.strip()

	def validate_amount(self):
		if self.amount is not None and self.amount < 0:
			frappe.throw(_("Donation amount cannot be negative."))

	def validate_date(self):
		if self.date and getdate(self.date) > getdate(nowdate()):
			frappe.throw(_("Donation date cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Donor", self.name, "status")
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot change status of a cancelled donation."))

	def before_save(self):
		if not self.date:
			self.date = nowdate()
