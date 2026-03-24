import frappe
from frappe import _
from frappe.model.document import Document


class POSInvoice(Document):
    def validate(self):
        self.calculate_totals()

    def calculate_totals(self):
        self.total_amount = sum((i.quantity or 0) * (i.rate or 0) for i in self.items)
        self.grand_total = self.total_amount - (self.discount_amount or 0) + (self.tax_amount or 0)
        if self.amount_paid:
            self.change_amount = max(0, self.amount_paid - self.grand_total)

    def on_submit(self):
        if self.amount_paid and self.amount_paid >= self.grand_total:
            self.db_set("status", "Paid")
        else:
            self.db_set("status", "Partially Paid")

    def on_cancel(self):
        self.db_set("status", "Cancelled")
