import frappe
from frappe import _
from frappe.model.document import Document


class DispenseSlip(Document):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        total = sum(
            (item.quantity or 0) * (item.rate or 0) for item in self.items
        )
        self.total_amount = total
        self.net_amount = total - (self.discount_amount or 0)

    def on_submit(self):
        self.db_set("status", "Dispensed")
        self.update_stock()
        self.update_prescription_status()

    def on_cancel(self):
        self.db_set("status", "Cancelled")
        self.reverse_stock()

    def update_stock(self):
        for item in self.items:
            if item.drug_item and item.batch_no:
                frappe.db.sql("""
                    UPDATE `tabBatch` SET stock_qty = stock_qty - %s
                    WHERE name = %s
                """, (item.quantity, item.batch_no))
            if item.drug_item:
                frappe.db.sql("""
                    UPDATE `tabDrug Item` SET current_stock = current_stock - %s
                    WHERE name = %s
                """, (item.quantity, item.drug_item))
        frappe.db.commit()

    def reverse_stock(self):
        for item in self.items:
            if item.drug_item:
                frappe.db.sql("""
                    UPDATE `tabDrug Item` SET current_stock = current_stock + %s
                    WHERE name = %s
                """, (item.quantity, item.drug_item))
        frappe.db.commit()

    def update_prescription_status(self):
        if self.prescription:
            all_dispensed = not frappe.db.exists("Prescription Item", {
                "parent": self.prescription, "is_dispensed": 0,
            })
            new_status = "Fully Dispensed" if all_dispensed else "Partially Dispensed"
            frappe.db.set_value("Prescription", self.prescription, "status", new_status)
