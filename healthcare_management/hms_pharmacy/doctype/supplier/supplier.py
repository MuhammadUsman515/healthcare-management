import frappe
from frappe import _
from frappe.model.document import Document


class Supplier(Document):
	def validate(self):
		self.validate_title()
		self.sync_status_and_active()
		self.validate_duplicate_title()

	def validate_title(self):
		if not self.title or not self.title.strip():
			frappe.throw(_("Supplier name is required."))
		self.title = self.title.strip()

	def sync_status_and_active(self):
		if self.status == "Inactive":
			self.is_active = 0
		elif self.status == "Active":
			self.is_active = 1

	def validate_duplicate_title(self):
		if self.title and frappe.db.exists(
			"Supplier",
			{"title": self.title, "name": ("!=", self.name)},
		):
			frappe.throw(_("Supplier {0} already exists.").format(self.title))
