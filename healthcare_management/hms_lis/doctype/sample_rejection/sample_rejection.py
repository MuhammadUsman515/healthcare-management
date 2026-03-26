import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SampleRejection(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_not_already_rejected()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for sample rejection."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for sample rejection."))
		if not self.description:
			frappe.throw(_("Rejection reason (Description) is required."))

	def validate_not_already_rejected(self):
		if self.is_new():
			existing = frappe.db.exists(
				"Sample Rejection",
				{"lab_test": self.lab_test, "patient": self.patient, "status": "Active"},
			)
			if existing:
				frappe.throw(_("An active rejection already exists for this Lab Test and Patient."))

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Rejected - {patient_name}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_submit(self):
		self.update_lab_test_status()

	def on_update(self):
		if self.status == "Completed":
			self.update_lab_test_status()

	def update_lab_test_status(self):
		"""Flag the linked lab test that its sample was rejected."""
		if self.lab_test and frappe.db.exists("Lab Test", self.lab_test):
			frappe.db.set_value("Lab Test", self.lab_test, "status", "Rejected")

	@frappe.whitelist()
	def request_recollection(self):
		"""Mark rejection as completed and signal recollection is needed."""
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("Sample marked for recollection."))
