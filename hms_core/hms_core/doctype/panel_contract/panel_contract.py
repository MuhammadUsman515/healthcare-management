import frappe
from frappe import _
from frappe.model.document import Document


class PanelContract(Document):
    def validate(self):
        if self.valid_to < self.valid_from:
            frappe.throw(_("Valid To date must be after Valid From date."))

    def on_submit(self):
        self.db_set("status", "Active")

    def on_cancel(self):
        self.db_set("status", "Terminated")
