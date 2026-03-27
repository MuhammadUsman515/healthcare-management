import frappe
from frappe import _
from frappe.model.document import Document


class ReferralLetter(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Referral Letter."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Referring practitioner is required for a Referral Letter."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Referral letter content (clinical summary and reason for referral) is required."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Referral Letter", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Referral Letter cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Referral Letter."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = _("Referral Letter - {0}").format(patient_name)
