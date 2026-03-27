import frappe
from frappe import _
from frappe.model.document import Document


class InpatientMedicationOrder(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for an Inpatient Medication Order."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Ordering practitioner is required for an Inpatient Medication Order."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Medication details (drug, dosage, frequency, route) must be specified."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Inpatient Medication Order", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Inpatient Medication Order cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Inpatient Medication Order."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Medication Order - {0} - {1}").format(
				self.patient, self.date or frappe.utils.nowdate()
			)

	def mark_completed(self):
		"""Mark the medication order as completed (fully administered)."""
		self.status = "Completed"
		self.save()

	def get_active_orders_for_patient(patient):
		"""Get all active medication orders for a patient."""
		return frappe.get_all(
			"Inpatient Medication Order",
			filters={"patient": patient, "status": "Active"},
			fields=["name", "date", "practitioner", "description"],
			order_by="date desc",
		)
