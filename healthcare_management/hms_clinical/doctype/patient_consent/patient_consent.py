import frappe
from frappe import _
from frappe.model.document import Document


class PatientConsent(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_date_not_future()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Patient Consent record."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Practitioner who obtained consent is required."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Consent details and scope must be documented."))
		self.description = self.description.strip()

	def validate_date_not_future(self):
		if self.date and frappe.utils.getdate(self.date) > frappe.utils.getdate():
			frappe.throw(_("Consent date cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Patient Consent", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Patient Consent cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Patient Consent."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Patient Consent - {0}").format(self.patient)

	def is_active_consent(self):
		"""Check if this consent is currently active."""
		return self.status == "Active"
