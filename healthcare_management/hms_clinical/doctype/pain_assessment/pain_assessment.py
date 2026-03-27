import frappe
from frappe import _
from frappe.model.document import Document


class PainAssessment(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_date_not_future()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Pain Assessment."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Assessing practitioner is required for a Pain Assessment."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Pain assessment details (location, severity, character) must be documented."))
		self.description = self.description.strip()

	def validate_date_not_future(self):
		if self.date and frappe.utils.getdate(self.date) > frappe.utils.getdate():
			frappe.throw(_("Pain Assessment date cannot be in the future."))

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Pain Assessment", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Pain Assessment cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Pain Assessment."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Pain Assessment - {0} - {1}").format(
				self.patient, self.date or frappe.utils.nowdate()
			)

	def get_patient_pain_history(self):
		"""Return all pain assessments for this patient, ordered by date."""
		return frappe.get_all(
			"Pain Assessment",
			filters={"patient": self.patient, "status": ["!=", "Cancelled"]},
			fields=["name", "date", "practitioner", "description", "status"],
			order_by="date desc",
		)
