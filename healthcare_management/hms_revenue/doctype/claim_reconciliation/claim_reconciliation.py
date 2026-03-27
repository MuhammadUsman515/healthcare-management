import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class ClaimReconciliation(Document):
    def validate(self):
        self.validate_patient()
        self.validate_amount()
        self.set_defaults()

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for Claim Reconciliation."))

    def validate_amount(self):
        if flt(self.amount) < 0:
            frappe.throw(_("Reconciliation amount cannot be negative."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Claim Recon - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"

    def get_variance(self, claimed_amount):
        """Return variance between claimed and reconciled amounts."""
        return flt(claimed_amount) - flt(self.amount)
