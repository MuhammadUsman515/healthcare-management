import frappe
from frappe import _
from frappe.model.document import Document


class ClinicalNote(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Clinical Note."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Practitioner is required for a Clinical Note."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Clinical note description cannot be empty."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Clinical Note", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Clinical Note cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Clinical Note."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = _("Clinical Note - {0}").format(patient_name)

	def get_note_summary(self):
		"""Return a truncated summary of the clinical note description."""
		if self.description and len(self.description) > 100:
			return self.description[:100] + "..."
		return self.description or ""
