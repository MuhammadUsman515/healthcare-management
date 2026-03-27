import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LabOutsourceRequest(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_not_duplicate()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for an outsource request."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for an outsource request."))

	def validate_not_duplicate(self):
		if self.is_new():
			existing = frappe.db.exists(
				"Lab Outsource Request",
				{"lab_test": self.lab_test, "patient": self.patient, "status": "Active"},
			)
			if existing:
				frappe.throw(
					_("An active outsource request already exists for this Lab Test and Patient.")
				)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Outsource - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@frappe.whitelist()
	def mark_sent(self):
		"""Mark request as sent to external lab."""
		self.status = "Inactive"
		self.description = (self.description or "") + f"\nSent to external lab at {now_datetime()}"
		self.save()
		frappe.msgprint(_("Request marked as sent."))

	@frappe.whitelist()
	def mark_completed(self):
		"""Mark outsource request as completed when result is received."""
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("Outsource request completed."))
