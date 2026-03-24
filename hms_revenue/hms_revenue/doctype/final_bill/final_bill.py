import frappe
from frappe import _
from frappe.model.document import Document


class FinalBill(Document):
    def validate(self):
        self.calculate_patient_payable()

    def calculate_patient_payable(self):
        self.patient_payable = (
            (self.total_charges or 0)
            - (self.discount_amount or 0)
            + (self.tax_amount or 0)
            - (self.insurance_covered or 0)
            - (self.welfare_subsidy or 0)
        )
        self.balance_due = self.patient_payable - (self.amount_paid or 0) - (self.deposit_used or 0)

    def on_submit(self):
        if self.balance_due <= 0:
            self.db_set("status", "Paid")
        elif self.amount_paid and self.amount_paid > 0:
            self.db_set("status", "Partially Paid")
        elif self.insurance_covered:
            self.db_set("status", "Insurance Pending")
        else:
            self.db_set("status", "Pending")

        if self.admission:
            frappe.db.set_value("Inpatient Admission", self.admission, "status", "Billing Clearance")

    def on_cancel(self):
        self.db_set("status", "Cancelled")


def post_to_ledger(doc, method=None):
    """Hook: Post bill to accounting ledger."""
    pass
