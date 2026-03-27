import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ResultAmendmentLog(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for an amendment log."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for an amendment log."))
		if not self.description:
			frappe.throw(_("Amendment details (Description) are required."))

	def set_title_if_empty(self):
		if not self.title:
			self.title = f"Amendment - {self.lab_test} - {frappe.session.user}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def before_insert(self):
		"""Always log the user who created the amendment."""
		self.description = (
			f"Amended by {frappe.session.user} at {now_datetime()}\n"
			+ (self.description or "")
		)

	def on_trash(self):
		"""Prevent deletion of amendment logs."""
		frappe.throw(_("Amendment logs cannot be deleted for regulatory compliance."))

	@staticmethod
	def log_amendment(patient, lab_test, reason):
		"""Create an amendment log entry."""
		doc = frappe.new_doc("Result Amendment Log")
		doc.patient = patient
		doc.lab_test = lab_test
		doc.description = reason
		doc.insert(ignore_permissions=True)
		return doc.name

	@staticmethod
	def get_amendments(lab_test, patient=None):
		"""Get amendment history for a lab test."""
		filters = {"lab_test": lab_test}
		if patient:
			filters["patient"] = patient
		return frappe.get_all(
			"Result Amendment Log",
			filters=filters,
			fields=["name", "title", "date", "description"],
			order_by="date desc",
		)
