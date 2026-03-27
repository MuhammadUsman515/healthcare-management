import frappe
from frappe import _
from frappe.model.document import Document


class DietOrder(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_status_transition()
		self.validate_no_duplicate_active_order()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Diet Order."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Ordering practitioner is required for a Diet Order."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Diet type and instructions must be specified."))
		self.description = self.description.strip()

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Diet Order", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Diet Order cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Diet Order."))

	def validate_no_duplicate_active_order(self):
		if self.status != "Active":
			return
		existing = frappe.db.exists(
			"Diet Order",
			{"patient": self.patient, "status": "Active", "name": ["!=", self.name]},
		)
		if existing:
			frappe.msgprint(
				_("Patient {0} already has an active Diet Order. Consider cancelling the previous order.").format(
					self.patient
				),
				indicator="orange",
				alert=True,
			)

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Diet Order - {0}").format(self.patient)

	def mark_completed(self):
		"""Mark the diet order as completed."""
		self.status = "Completed"
		self.save()
