import frappe
from frappe import _
from frappe.model.document import Document


class Payer(Document):
	def before_save(self):
		if self.payer_name:
			self.payer_name = self.payer_name.strip()

	def validate(self):
		self.validate_unique_name()

	def validate_unique_name(self):
		if self.payer_name and frappe.db.exists(
			"Payer",
			{"payer_name": self.payer_name, "name": ("!=", self.name)},
		):
			frappe.throw(_("Payer {0} already exists.").format(self.payer_name))

	def get_active_payers():
		"""Return list of active payers for use in filters."""
		return frappe.get_all(
			"Payer", filters={"is_active": 1}, pluck="payer_name", order_by="payer_name"
		)
