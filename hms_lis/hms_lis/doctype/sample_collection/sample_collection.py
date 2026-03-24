import frappe
from frappe import _
from frappe.model.document import Document


class SampleCollection(Document):
    def before_save(self):
        if not self.barcode:
            self.barcode = self.name

    def on_submit(self):
        self.db_set("status", "Accepted")
        if self.lab_order:
            frappe.db.set_value("Lab Order", self.lab_order, "status", "Collected")
            frappe.db.sql("""
                UPDATE `tabLab Test` SET status = 'Sample Collected'
                WHERE lab_order = %s AND status = 'Ordered'
            """, self.lab_order)
            frappe.db.commit()

    @frappe.whitelist()
    def reject_sample(self, reason, notes=None):
        self.db_set("status", "Rejected")
        self.db_set("rejection_reason", reason)
        if notes:
            self.db_set("rejection_notes", notes)
        frappe.msgprint(_("Sample rejected: {0}").format(reason), indicator="red")
