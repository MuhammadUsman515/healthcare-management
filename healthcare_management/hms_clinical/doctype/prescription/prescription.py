import frappe
from frappe import _
from frappe.model.document import Document


class Prescription(Document):
    def validate(self):
        if not self.items:
            frappe.throw(_("At least one prescription item is required."))

    def on_submit(self):
        self.db_set("status", "Signed")

    def on_cancel(self):
        self.db_set("status", "Cancelled")

    @frappe.whitelist()
    def send_to_pharmacy(self):
        if self.docstatus != 1:
            frappe.throw(_("Prescription must be signed/submitted first."))
        self.db_set("status", "Sent to Pharmacy")
        frappe.msgprint(_("Prescription sent to pharmacy queue."), alert=True)
