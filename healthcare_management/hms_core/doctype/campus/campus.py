import frappe
from frappe import _
from frappe.model.document import Document


class Campus(Document):
	def before_save(self):
		if self.campus_name:
			self.campus_name = self.campus_name.strip()

	def validate(self):
		self.validate_unique_name()

	def validate_unique_name(self):
		if self.campus_name and frappe.db.exists(
			"Campus",
			{"campus_name": self.campus_name, "name": ("!=", self.name)},
		):
			frappe.throw(_("Campus {0} already exists.").format(self.campus_name))
