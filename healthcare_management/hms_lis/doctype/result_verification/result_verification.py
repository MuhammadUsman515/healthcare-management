import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class ResultVerification(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_result_exists()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for result verification."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for result verification."))

	def validate_result_exists(self):
		"""Ensure a completed result entry exists before verification."""
		result = frappe.db.exists(
			"Result Entry",
			{"lab_test": self.lab_test, "patient": self.patient, "status": "Completed"},
		)
		if not result:
			frappe.throw(
				_("No completed Result Entry found for Lab Test {0} and Patient {1}.").format(
					self.lab_test, self.patient
				)
			)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Verification - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def on_update(self):
		if self.status == "Completed":
			self.mark_result_verified()

	def mark_result_verified(self):
		"""Publish event so downstream processes know the result is verified."""
		frappe.publish_realtime(
			"result_verified",
			{"name": self.name, "patient": self.patient, "lab_test": self.lab_test},
			after_commit=True,
		)

	@frappe.whitelist()
	def approve(self):
		"""Approve and complete verification."""
		if self.status == "Completed":
			frappe.throw(_("Verification is already completed."))
		self.status = "Completed"
		self.description = (self.description or "") + f"\nApproved by {frappe.session.user}"
		self.save()

	@frappe.whitelist()
	def reject(self, reason=None):
		"""Reject the result and revert to active for re-entry."""
		self.status = "Inactive"
		self.description = (self.description or "") + f"\nRejected: {reason or 'No reason given'}"
		self.save()
		frappe.msgprint(_("Result verification rejected. Result must be re-entered."))
