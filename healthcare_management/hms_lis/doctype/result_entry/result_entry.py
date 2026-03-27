import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ResultEntry(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_not_duplicate_active()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for result entry."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for result entry."))
		if not self.description:
			frappe.throw(_("Result value (Description) is required."))

	def validate_not_duplicate_active(self):
		if self.is_new():
			existing = frappe.db.exists(
				"Result Entry",
				{"lab_test": self.lab_test, "patient": self.patient, "status": "Active"},
			)
			if existing:
				frappe.throw(
					_("An active Result Entry already exists for this patient and lab test.")
				)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Result - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_update(self):
		if self.status == "Completed":
			self.check_critical_value()

	def check_critical_value(self):
		"""Check if result warrants a critical value alert."""
		frappe.publish_realtime(
			"result_entered",
			{
				"name": self.name,
				"patient": self.patient,
				"lab_test": self.lab_test,
				"result": self.description,
			},
			after_commit=True,
		)

	@frappe.whitelist()
	def mark_completed(self):
		"""Finalize this result entry."""
		if self.status == "Completed":
			frappe.throw(_("Result Entry is already completed."))
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("Result Entry marked as completed."))
