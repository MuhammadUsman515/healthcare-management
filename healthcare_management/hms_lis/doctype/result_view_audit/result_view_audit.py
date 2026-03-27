import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ResultViewAudit(Document):
	def validate(self):
		self.set_defaults()

	def set_defaults(self):
		if not self.date:
			self.date = now_datetime()
		if not self.title:
			self.title = f"View - {self.patient or 'Unknown'} - {frappe.session.user}"
		if not self.description:
			self.description = f"Result viewed by {frappe.session.user}"

	def before_insert(self):
		"""Audit records should always be Active on creation and not editable."""
		self.status = "Active"

	def on_trash(self):
		"""Prevent deletion of audit records except by administrators."""
		if "Healthcare Administrator" not in frappe.get_roles(frappe.session.user):
			frappe.throw(_("Audit records cannot be deleted."))

	@staticmethod
	def log_view(patient, lab_test):
		"""Create an audit log entry for a result view."""
		doc = frappe.new_doc("Result View Audit")
		doc.patient = patient
		doc.lab_test = lab_test
		doc.date = now_datetime()
		doc.description = f"Result viewed by {frappe.session.user}"
		doc.insert(ignore_permissions=True)
		return doc.name

	@staticmethod
	def get_audit_trail(patient=None, lab_test=None, limit=50):
		"""Retrieve audit trail filtered by patient and/or lab test."""
		filters = {}
		if patient:
			filters["patient"] = patient
		if lab_test:
			filters["lab_test"] = lab_test
		return frappe.get_all(
			"Result View Audit",
			filters=filters,
			fields=["name", "title", "patient", "lab_test", "date", "description"],
			order_by="date desc",
			limit_page_length=limit,
		)
