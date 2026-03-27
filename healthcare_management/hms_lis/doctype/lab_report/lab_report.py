import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LabReport(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_results_verified()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a lab report."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for a lab report."))

	def validate_results_verified(self):
		"""Warn if results have not been verified before generating a report."""
		if self.is_new():
			verified = frappe.db.exists(
				"Result Verification",
				{"lab_test": self.lab_test, "patient": self.patient, "status": "Completed"},
			)
			if not verified:
				frappe.msgprint(
					_("Warning: No verified result found for this Lab Test. Report may be preliminary."),
					alert=True,
				)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Report - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_update(self):
		if self.status == "Completed":
			self.log_delivery()

	def log_delivery(self):
		"""Publish report finalized event for downstream delivery tracking."""
		frappe.publish_realtime(
			"lab_report_finalized",
			{"name": self.name, "patient": self.patient, "lab_test": self.lab_test},
			after_commit=True,
		)

	@frappe.whitelist()
	def finalize(self):
		"""Finalize the report."""
		if self.status == "Completed":
			frappe.throw(_("Report is already finalized."))
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("Lab Report finalized."))

	@staticmethod
	def get_reports_for_patient(patient, limit=20):
		"""Get lab reports for a patient."""
		return frappe.get_all(
			"Lab Report",
			filters={"patient": patient},
			fields=["name", "title", "lab_test", "status", "date"],
			order_by="date desc",
			limit_page_length=limit,
		)
