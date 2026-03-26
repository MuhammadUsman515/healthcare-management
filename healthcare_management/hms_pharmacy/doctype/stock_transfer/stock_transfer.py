import frappe
from frappe import _
from frappe.model.document import Document


class StockTransfer(Document):
    def validate(self):
        if self.from_store == self.to_store:
            frappe.throw(_("Source and destination store cannot be the same."))

    def on_submit(self):
        for item in (self.items or []):
            if item.batch:
                frappe.db.sql("""UPDATE `tabBatch` SET store = %s
                    WHERE name = %s""", (self.to_store, item.batch))
