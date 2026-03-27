import frappe
from frappe import _
from frappe.model.document import Document


class DeathSummary(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_date_not_future()
		self.validate_status_transition()
		self.validate_no_duplicate()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Death Summary."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Certifying practitioner is required for a Death Summary."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Cause of death and clinical summary must be documented."))
		self.description = self.description.strip()

	def validate_date_not_future(self):
		if self.date and frappe.utils.getdate(self.date) > frappe.utils.getdate():
			frappe.throw(_("Date of death cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Death Summary", self.name, "status")
		if old_status == "Completed" and self.status != "Completed":
			frappe.throw(_("A completed Death Summary cannot be modified. Create an amendment if corrections are needed."))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Death Summary."))

	def validate_no_duplicate(self):
		existing = frappe.db.exists(
			"Death Summary",
			{"patient": self.patient, "status": ["!=", "Cancelled"], "name": ["!=", self.name]},
		)
		if existing:
			frappe.throw(
				_("A Death Summary already exists for patient {0}.").format(self.patient)
			)

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = _("Death Summary - {0}").format(patient_name)
