import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PatientPortalProfile(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_unique_profile()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a portal profile."))

	def validate_unique_profile(self):
		"""Only one active portal profile per patient."""
		if self.is_new() and self.status == "Active":
			existing = frappe.db.exists(
				"Patient Portal Profile",
				{"patient": self.patient, "status": "Active"},
			)
			if existing:
				frappe.throw(
					_("An active portal profile already exists for patient {0}.").format(self.patient)
				)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Portal - {patient_name}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate portal access for this patient."""
		self.status = "Inactive"
		self.save()
		frappe.msgprint(_("Portal access deactivated for patient."))

	@frappe.whitelist()
	def activate(self):
		"""Activate portal access for this patient."""
		self.status = "Active"
		self.save()
		frappe.msgprint(_("Portal access activated for patient."))

	@staticmethod
	def get_profile(patient):
		"""Get the active portal profile for a patient."""
		name = frappe.db.get_value(
			"Patient Portal Profile",
			{"patient": patient, "status": "Active"},
			"name",
		)
		if name:
			return frappe.get_doc("Patient Portal Profile", name)
		return None
