import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LabQualityControl(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient and not self.lab_test:
			frappe.throw(_("At least one of Patient or Lab Test must be specified."))

	def set_title_if_empty(self):
		if not self.title:
			parts = []
			if self.lab_test:
				parts.append(self.lab_test)
			if self.patient:
				parts.append(frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient)
			self.title = "QC - " + " / ".join(parts)

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_update(self):
		if self.status == "Completed":
			self.notify_lab_supervisor()

	def notify_lab_supervisor(self):
		"""Send notification to Lab Supervisor when QC is completed."""
		frappe.publish_realtime(
			"lab_qc_completed",
			{"name": self.name, "title": self.title, "lab_test": self.lab_test},
			after_commit=True,
		)

	@frappe.whitelist()
	def mark_completed(self):
		"""Mark this QC record as completed."""
		if self.status == "Completed":
			frappe.throw(_("Quality Control record is already completed."))
		self.status = "Completed"
		self.save()

	@staticmethod
	def get_active_qc_for_test(lab_test):
		"""Return active QC records for a given lab test."""
		return frappe.get_all(
			"Lab Quality Control",
			filters={"lab_test": lab_test, "status": "Active"},
			fields=["name", "title", "date", "description"],
			order_by="date desc",
		)
