import frappe
from frappe import _
from frappe.model.document import Document


class LabMachineMapping(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_unique_mapping()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for machine mapping."))
		if not self.title and not self.description:
			frappe.throw(_("Machine identifier (Title or Description) is required."))

	def validate_unique_mapping(self):
		"""Ensure no duplicate active mapping for the same lab test."""
		if self.is_new() and self.status == "Active":
			existing = frappe.db.exists(
				"Lab Machine Mapping",
				{"lab_test": self.lab_test, "status": "Active", "title": self.title},
			)
			if existing:
				frappe.throw(
					_("An active mapping already exists for Lab Test {0} with machine {1}.").format(
						self.lab_test, self.title
					)
				)

	def set_title_if_empty(self):
		if not self.title and self.description:
			self.title = f"Mapping - {self.lab_test}"

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate this machine mapping."""
		self.status = "Inactive"
		self.save()

	@staticmethod
	def get_machine_for_test(lab_test):
		"""Get the active machine mapping for a lab test."""
		mappings = frappe.get_all(
			"Lab Machine Mapping",
			filters={"lab_test": lab_test, "status": "Active"},
			fields=["name", "title", "description"],
			limit=1,
		)
		return mappings[0] if mappings else None
