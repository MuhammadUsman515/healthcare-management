import frappe
from frappe import _
from frappe.model.document import Document


class ReferenceRange(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()
		self.validate_no_duplicate()

	def validate_mandatory_fields(self):
		if not self.lab_test:
			frappe.throw(_("Lab Test is required to define a reference range."))
		if not self.description:
			frappe.throw(
				_("Description must contain the reference range values (e.g. normal low/high).")
			)

	def set_title_if_empty(self):
		if not self.title:
			self.title = f"Ref Range - {self.lab_test}"

	def validate_no_duplicate(self):
		"""Prevent duplicate active reference ranges for the same test and patient group."""
		if self.is_new() and self.status == "Active":
			filters = {"lab_test": self.lab_test, "status": "Active"}
			if self.patient:
				filters["patient"] = self.patient
			existing = frappe.db.exists("Reference Range", filters)
			if existing:
				frappe.throw(
					_("An active Reference Range already exists for Lab Test {0}.").format(self.lab_test)
				)

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate this reference range."""
		self.status = "Inactive"
		self.save()
		frappe.msgprint(_("Reference Range deactivated."))

	@staticmethod
	def get_active_range(lab_test, patient=None):
		"""Retrieve the active reference range for a lab test, optionally patient-specific."""
		filters = {"lab_test": lab_test, "status": "Active"}
		if patient:
			patient_range = frappe.db.get_value(
				"Reference Range", {**filters, "patient": patient}, "name"
			)
			if patient_range:
				return frappe.get_doc("Reference Range", patient_range)
		return frappe.get_last_doc("Reference Range", filters=filters, order_by="date desc")
