import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, getdate


class PayerContract(Document):
    def validate(self):
        self.validate_title()
        self.validate_date()
        self.set_defaults()

    def validate_title(self):
        if not self.title:
            frappe.throw(_("Contract title is required."))

    def validate_date(self):
        if self.date and getdate(self.date) < getdate(nowdate()):
            frappe.msgprint(_("Contract date is in the past."), indicator="orange", alert=True)

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"

    def is_active(self):
        """Check if contract is currently active."""
        return self.status == "Active"
