import frappe
from frappe import _
from frappe.model.document import Document


class PortalLabAccessPolicy(Document):
	def validate(self):
		self.set_title_if_empty()
		self.validate_no_conflicting_policy()

	def set_title_if_empty(self):
		if not self.title:
			parts = []
			if self.lab_test:
				parts.append(self.lab_test)
			if self.patient:
				parts.append(self.patient)
			self.title = "Policy - " + " / ".join(parts) if parts else "Policy - Global"

	def validate_no_conflicting_policy(self):
		"""Prevent duplicate active policies for the same scope."""
		if self.is_new() and self.status == "Active":
			filters = {"status": "Active"}
			if self.lab_test:
				filters["lab_test"] = self.lab_test
			if self.patient:
				filters["patient"] = self.patient
			existing = frappe.db.exists("Portal Lab Access Policy", filters)
			if existing:
				frappe.throw(_("An active access policy already exists for this scope."))

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate this policy."""
		self.status = "Inactive"
		self.save()

	@staticmethod
	def is_access_allowed(patient, lab_test=None):
		"""Check if portal access is allowed for a patient/test combination."""
		# Check for patient-specific denial
		denied = frappe.db.exists(
			"Portal Lab Access Policy",
			{"patient": patient, "status": "Inactive"},
		)
		if denied:
			return False
		# Check for test-specific policy
		if lab_test:
			policy = frappe.db.exists(
				"Portal Lab Access Policy",
				{"lab_test": lab_test, "status": "Active"},
			)
			if policy:
				return True
		# Default: allow
		return True
