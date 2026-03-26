import frappe
from frappe import _
from frappe.model.document import Document


class Floor(Document):
	def before_save(self):
		if self.floor_name:
			self.floor_name = self.floor_name.strip()

	def validate(self):
		self.validate_unique_name()

	def validate_unique_name(self):
		if self.floor_name and frappe.db.exists(
			"Floor",
			{"floor_name": self.floor_name, "name": ("!=", self.name)},
		):
			frappe.throw(_("Floor {0} already exists.").format(self.floor_name))
