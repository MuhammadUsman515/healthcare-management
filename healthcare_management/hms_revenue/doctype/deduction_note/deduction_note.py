import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class DeductionNote(Document):
    def validate(self):
        self.validate_amount()
        self.validate_patient()
        self.validate_reason()
        self.set_defaults()

    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Deduction amount must be greater than zero."))

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Deduction Note."))

    def validate_reason(self):
        if not self.description:
            frappe.throw(_("A reason/description is mandatory for a Deduction Note."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Deduction - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"
