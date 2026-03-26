import frappe
from frappe import _
from frappe.model.document import Document


class Guardian(Document):
	def validate(self):
		self.validate_title()
		self.validate_patient()

	def validate_title(self):
		if not self.title or not self.title.strip():
			frappe.throw(_("Guardian name is required."))
		self.title = self.title.strip()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a guardian record."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
