import frappe
from frappe import _
from frappe.model.document import Document


class DrugItem(Document):
    def validate(self):
        if self.selling_price and self.mrp and self.selling_price > self.mrp:
            frappe.throw(_("Selling price cannot exceed MRP."))
