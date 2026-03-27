import frappe
from frappe import _
from frappe.model.document import Document


class CarePlan(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()
		self.validate_no_duplicate_active_plan()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Care Plan."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Practitioner is required for a Care Plan."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Care plan details and goals are required."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Care Plan", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Care Plan cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Care Plan."))

	def validate_no_duplicate_active_plan(self):
		if self.status != "Active":
			return
		existing = frappe.db.exists(
			"Care Plan",
			{"patient": self.patient, "status": "Active", "name": ["!=", self.name]},
		)
		if existing:
			frappe.throw(
				_("An active Care Plan already exists for patient {0}. Complete or cancel the existing plan first.").format(
					self.patient
				)
			)

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Care Plan - {0}").format(self.patient)

	def mark_completed(self):
		"""Mark the care plan as completed."""
		self.status = "Completed"
		self.save()
