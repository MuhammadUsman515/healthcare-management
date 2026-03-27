import frappe
from frappe import _
from frappe.model.document import Document


class AdmissionRequest(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()
		self.validate_no_duplicate_active_request()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for an Admission Request."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Requesting practitioner is required for an Admission Request."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Reason for admission is required."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Admission Request", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Admission Request cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Admission Request."))

	def validate_no_duplicate_active_request(self):
		if self.status != "Active":
			return
		existing = frappe.db.exists(
			"Admission Request",
			{"patient": self.patient, "status": "Active", "name": ["!=", self.name]},
		)
		if existing:
			frappe.throw(
				_("An active Admission Request already exists for patient {0}.").format(self.patient)
			)

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Admission Request - {0}").format(self.patient)

	def approve(self):
		"""Mark the admission request as completed (approved)."""
		self.status = "Completed"
		self.save()
