import frappe
from frappe import _
from frappe.model.document import Document


class Refund(Document):
    def validate(self):
        if self.amount and self.amount <= 0:
            frappe.throw(_("Refund amount must be greater than zero."))

    def on_submit(self):
        if self.against_bill:
            frappe.db.sql("""UPDATE `tabFinal Bill`
                SET amount_paid = amount_paid - %s,
                    balance_due = balance_due + %s
                WHERE name = %s""", (self.amount, self.amount, self.against_bill))
