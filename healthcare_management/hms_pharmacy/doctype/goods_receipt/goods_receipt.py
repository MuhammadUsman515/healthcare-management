import frappe
from frappe import _
from frappe.model.document import Document


class GoodsReceipt(Document):
    def on_submit(self):
        self.update_batch_stock()

    def update_batch_stock(self):
        for item in (self.items or []):
            if item.batch:
                frappe.db.sql("""UPDATE `tabBatch` SET quantity = quantity + %s
                    WHERE name = %s""", (item.quantity, item.batch))
            else:
                batch = frappe.get_doc({
                    "doctype": "Batch",
                    "drug_item": item.drug_item,
                    "batch_no": item.batch_no,
                    "quantity": item.quantity,
                    "expiry_date": item.expiry_date,
                    "store": self.store,
                    "supplier": self.supplier,
                })
                batch.insert(ignore_permissions=True)
