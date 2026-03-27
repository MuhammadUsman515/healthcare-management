import frappe
from frappe import _
from frappe.model.document import Document


class ProgressNote(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Progress Note."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Practitioner is required for a Progress Note."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Progress note content cannot be empty."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Progress Note", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Progress Note cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Progress Note."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Progress Note - {0} - {1}").format(
				self.patient, self.date or frappe.utils.nowdate()
			)

	def get_patient_progress_notes(self):
		"""Return all progress notes for this patient, ordered by date."""
		return frappe.get_all(
			"Progress Note",
			filters={"patient": self.patient, "status": ["!=", "Cancelled"]},
			fields=["name", "date", "practitioner", "description", "status"],
			order_by="date desc",
		)
