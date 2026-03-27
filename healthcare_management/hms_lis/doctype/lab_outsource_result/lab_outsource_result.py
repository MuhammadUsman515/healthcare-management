import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LabOutsourceResult(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_outsource_request_exists()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for outsource result."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for outsource result."))
		if not self.description:
			frappe.throw(_("Result data (Description) is required."))

	def validate_outsource_request_exists(self):
		"""Ensure an outsource request exists for this test."""
		request = frappe.db.exists(
			"Lab Outsource Request",
			{"lab_test": self.lab_test, "patient": self.patient, "status": ["!=", "Completed"]},
		)
		if not request and self.is_new():
			frappe.msgprint(
				_("No pending outsource request found for this Lab Test. Proceeding anyway."),
				alert=True,
			)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Ext Result - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_update(self):
		if self.status == "Completed":
			self.complete_outsource_request()

	def complete_outsource_request(self):
		"""Mark the corresponding outsource request as completed."""
		requests = frappe.get_all(
			"Lab Outsource Request",
			filters={"lab_test": self.lab_test, "patient": self.patient, "status": ["!=", "Completed"]},
			pluck="name",
		)
		for req_name in requests:
			frappe.db.set_value("Lab Outsource Request", req_name, "status", "Completed")

	@frappe.whitelist()
	def accept_result(self):
		"""Accept the external result and mark as completed."""
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("External result accepted."))
