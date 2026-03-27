import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class PayerSettlement(Document):
    def validate(self):
        self.validate_amount()
        self.validate_patient()
        self.set_defaults()

    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Settlement amount must be greater than zero."))

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Payer Settlement."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Settlement - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"
