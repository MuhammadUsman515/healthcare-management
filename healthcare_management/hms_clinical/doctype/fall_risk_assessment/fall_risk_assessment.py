import frappe
from frappe import _
from frappe.model.document import Document


class FallRiskAssessment(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_date_not_future()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Fall Risk Assessment."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Assessing practitioner is required for a Fall Risk Assessment."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Fall risk assessment findings and risk level must be documented."))
		self.description = self.description.strip()

	def validate_date_not_future(self):
		if self.date and frappe.utils.getdate(self.date) > frappe.utils.getdate():
			frappe.throw(_("Fall Risk Assessment date cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Fall Risk Assessment", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Fall Risk Assessment cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Fall Risk Assessment."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Fall Risk Assessment - {0} - {1}").format(
				self.patient, self.date or frappe.utils.nowdate()
			)

	def get_latest_assessment(patient):
		"""Get the most recent fall risk assessment for a patient."""
		return frappe.get_all(
			"Fall Risk Assessment",
			filters={"patient": patient, "status": ["!=", "Cancelled"]},
			fields=["name", "date", "description", "status"],
			order_by="date desc",
			limit=1,
		)
