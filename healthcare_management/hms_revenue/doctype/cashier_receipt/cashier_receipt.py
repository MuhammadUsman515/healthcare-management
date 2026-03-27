import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class CashierReceipt(Document):
    def validate(self):
        self.validate_amount()
        self.validate_patient()
        self.set_defaults()

    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Receipt amount must be greater than zero."))

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Cashier Receipt."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Receipt - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"

    @frappe.whitelist()
    def get_print_data(self):
        """Return formatted receipt data for printing."""
        patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") if self.patient else None
        return {
            "receipt_no": self.name,
            "patient": self.patient,
            "patient_name": patient_name,
            "amount": self.amount,
            "date": self.date,
        }
