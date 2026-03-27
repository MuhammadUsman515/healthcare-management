import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ResultValue(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a result value."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for a result value."))
		if not self.description:
			frappe.throw(_("Result value (Description) is required."))

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Value - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@staticmethod
	def get_latest_value(patient, lab_test):
		"""Get the most recent result value for a patient and lab test."""
		values = frappe.get_all(
			"Result Value",
			filters={"patient": patient, "lab_test": lab_test},
			fields=["name", "description", "date", "status"],
			order_by="date desc",
			limit=1,
		)
		return values[0] if values else None

	@staticmethod
	def get_patient_history(patient, lab_test=None, limit=50):
		"""Get result value history for a patient, optionally filtered by test."""
		filters = {"patient": patient}
		if lab_test:
			filters["lab_test"] = lab_test
		return frappe.get_all(
			"Result Value",
			filters=filters,
			fields=["name", "title", "lab_test", "description", "date", "status"],
			order_by="date desc",
			limit_page_length=limit,
		)
