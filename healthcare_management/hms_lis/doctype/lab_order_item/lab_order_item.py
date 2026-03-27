import frappe
from frappe import _
from frappe.model.document import Document


class LabOrderItem(Document):
	def validate(self):
		self.validate_test_name()
		self.set_test_name_from_template()

	def validate_test_name(self):
		if not self.test_name and not self.test_template:
			frappe.throw(_("Either Test Name or Test Template is required."))

	def set_test_name_from_template(self):
		"""Auto-populate test_name from template if not manually set."""
		if self.test_template and not self.test_name:
			self.test_name = frappe.db.get_value(
				"Lab Test Template", self.test_template, "lab_test_name"
			) or self.test_template

	def before_save(self):
		self.set_sample_type_from_template()

	def set_sample_type_from_template(self):
		"""Auto-fill sample type from template if available."""
		if self.test_template and not self.sample_type:
			sample = frappe.db.get_value(
				"Lab Test Template", self.test_template, "sample"
			)
			if sample:
				sample_map = {
					"Blood": "Blood",
					"Serum": "Serum",
					"Plasma": "Plasma",
					"Urine": "Urine",
				}
				self.sample_type = sample_map.get(sample, "Other")
