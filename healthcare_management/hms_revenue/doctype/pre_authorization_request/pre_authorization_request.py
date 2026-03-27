import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class PreAuthorizationRequest(Document):
    def validate(self):
        self.validate_patient()
        self.validate_amount()
        self.validate_description()
        self.set_defaults()

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Pre-Authorization Request."))

    def validate_amount(self):
        if flt(self.amount) <= 0:
            frappe.throw(_("Requested authorization amount must be greater than zero."))

    def validate_description(self):
        if not self.description:
            frappe.throw(_("Clinical justification is required for pre-authorization."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Pre-Auth - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"

    @frappe.whitelist()
    def approve(self):
        """Mark pre-authorization as approved."""
        if self.status == "Cancelled":
            frappe.throw(_("Cannot approve a cancelled request."))
        self.status = "Completed"
        self.save()
        frappe.msgprint(_("Pre-Authorization Request approved."))

    @frappe.whitelist()
    def deny(self, reason=None):
        """Mark pre-authorization as denied."""
        self.status = "Cancelled"
        if reason:
            self.description = (self.description or "") + f"\nDenial Reason: {reason}"
        self.save()
        frappe.msgprint(_("Pre-Authorization Request denied."))
