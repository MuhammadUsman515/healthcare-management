import frappe
from frappe import _
from frappe.model.document import Document


class Deposit(Document):
    def validate(self):
        if self.amount and self.amount <= 0:
            frappe.throw(_("Deposit amount must be greater than zero."))
        if not self.balance:
            self.balance = self.amount

    @frappe.whitelist()
    def adjust_against_bill(self, bill, amount):
        if amount > self.balance:
            frappe.throw(_("Adjustment amount exceeds available balance."))
        self.balance -= amount
        if self.balance <= 0:
            self.status = "Exhausted"
        self.save()
        frappe.get_doc({
            "doctype": "Deposit Adjustment",
            "deposit": self.name,
            "against_bill": bill,
            "amount": amount,
            "patient": self.patient,
        }).insert(ignore_permissions=True)
        frappe.msgprint(_("Deposit adjusted by {0} against {1}.").format(amount, bill))
