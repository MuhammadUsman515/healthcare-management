import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class PaymentEntry(Document):
    def validate(self):
        self.validate_amount()
        self.validate_patient()
        self.set_defaults()

    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Payment amount must be greater than zero."))

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Payment Entry."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Payment - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"

    def get_patient_outstanding(self):
        """Calculate outstanding balance for the linked patient."""
        total_billed = flt(frappe.db.sql(
            """SELECT IFNULL(SUM(amount), 0) FROM `tabProvisional Bill`
            WHERE patient = %s AND status != 'Cancelled'""",
            self.patient,
        )[0][0])
        total_paid = flt(frappe.db.sql(
            """SELECT IFNULL(SUM(amount), 0) FROM `tabPayment Entry`
            WHERE patient = %s AND status = 'Completed'""",
            self.patient,
        )[0][0])
        return total_billed - total_paid
