import frappe
from frappe import _
from frappe.model.document import Document


class StockAdjustment(Document):
    def on_submit(self):
        for item in (self.items or []):
            if item.batch:
                frappe.db.sql("""UPDATE `tabBatch`
                    SET quantity = %s WHERE name = %s""",
                    (item.new_quantity, item.batch))
