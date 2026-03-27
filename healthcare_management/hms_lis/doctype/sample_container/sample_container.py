import frappe
from frappe import _
from frappe.model.document import Document


class SampleContainer(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.title and not self.lab_test:
			frappe.throw(_("Either Title or Lab Test must be specified for a sample container."))

	def set_title_if_empty(self):
		if not self.title:
			self.title = f"Container - {self.lab_test}"

	@frappe.whitelist()
	def deactivate(self):
		"""Deactivate this container type."""
		self.status = "Inactive"
		self.save()

	@frappe.whitelist()
	def activate(self):
		"""Re-activate this container type."""
		self.status = "Active"
		self.save()

	@staticmethod
	def get_container_for_test(lab_test):
		"""Get the active container specification for a given lab test."""
		return frappe.get_all(
			"Sample Container",
			filters={"lab_test": lab_test, "status": "Active"},
			fields=["name", "title", "description"],
			limit=1,
		)
