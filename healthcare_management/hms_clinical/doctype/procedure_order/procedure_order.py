import frappe
from frappe import _
from frappe.model.document import Document


class ProcedureOrder(Document):
	def validate(self):
		self.validate_patient()
		self.validate_practitioner()
		self.validate_description()
		self.validate_date()
		self.validate_status_transition()

	def validate_patient(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a Procedure Order."))

	def validate_practitioner(self):
		if not self.practitioner:
			frappe.throw(_("Ordering practitioner is required for a Procedure Order."))

	def validate_description(self):
		if not self.description or not self.description.strip():
			frappe.throw(_("Procedure details are required."))
		self.description = self.description.strip()

	def validate_date(self):
		if self.date and frappe.utils.getdate(self.date) < frappe.utils.getdate():
			frappe.msgprint(
				_("Procedure Order date {0} is in the past.").format(self.date),
				indicator="orange",
				alert=True,
			)

	def validate_status_transition(self):
		if self.is_new():
			return
		old_status = frappe.db.get_value("Procedure Order", self.name, "status")
		if old_status == "Completed" and self.status not in ("Completed", "Cancelled"):
			frappe.throw(_("A completed Procedure Order cannot be reverted to {0}.").format(self.status))
		if old_status == "Cancelled" and self.status != "Cancelled":
			frappe.throw(_("Cannot modify a cancelled Procedure Order."))

	def before_save(self):
		if self.is_new() and not self.date:
			self.date = frappe.utils.nowdate()
		if not self.title:
			self.title = _("Procedure Order - {0}").format(self.patient)

	def mark_completed(self):
		"""Mark the procedure order as completed."""
		self.status = "Completed"
		self.save()
