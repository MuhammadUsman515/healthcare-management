import frappe
from frappe import _
from frappe.model.document import Document


class Uom(Document):
	def before_save(self):
		if self.uom_name:
			self.uom_name = self.uom_name.strip()

	def validate(self):
		self.validate_unique_name()

	def validate_unique_name(self):
		if self.uom_name and frappe.db.exists(
			"Uom",
			{"uom_name": self.uom_name, "name": ("!=", self.name)},
		):
			frappe.throw(_("UOM {0} already exists.").format(self.uom_name))
