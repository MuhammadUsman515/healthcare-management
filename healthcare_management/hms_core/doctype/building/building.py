import frappe
from frappe import _
from frappe.model.document import Document


class Building(Document):
	def before_save(self):
		if self.building_name:
			self.building_name = self.building_name.strip()

	def validate(self):
		self.validate_unique_name()

	def validate_unique_name(self):
		if self.building_name and frappe.db.exists(
			"Building",
			{"building_name": self.building_name, "name": ("!=", self.name)},
		):
			frappe.throw(_("Building {0} already exists.").format(self.building_name))
