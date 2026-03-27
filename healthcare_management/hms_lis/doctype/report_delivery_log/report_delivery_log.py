import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ReportDeliveryLog(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for delivery log."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for delivery log."))

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Delivered - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_trash(self):
		"""Prevent deletion of delivery logs."""
		frappe.throw(_("Delivery logs cannot be deleted for audit purposes."))

	@staticmethod
	def log_delivery(patient, lab_test, method="Print"):
		"""Create a delivery log entry."""
		doc = frappe.new_doc("Report Delivery Log")
		doc.patient = patient
		doc.lab_test = lab_test
		doc.description = f"Report delivered via {method} by {frappe.session.user}"
		doc.status = "Completed"
		doc.insert(ignore_permissions=True)
		return doc.name

	@staticmethod
	def get_delivery_history(patient, limit=20):
		"""Get delivery history for a patient."""
		return frappe.get_all(
			"Report Delivery Log",
			filters={"patient": patient},
			fields=["name", "title", "lab_test", "date", "description", "status"],
			order_by="date desc",
			limit_page_length=limit,
		)
