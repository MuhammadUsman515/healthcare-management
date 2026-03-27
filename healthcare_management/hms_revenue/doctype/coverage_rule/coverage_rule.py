import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CoverageRule(Document):
    def validate(self):
        self.validate_title()
        self.validate_amount()
        self.set_defaults()

    def validate_title(self):
        if not self.title:
            frappe.throw(_("Coverage Rule title is required."))

    def validate_amount(self):
        if flt(self.amount) < 0:
            frappe.throw(_("Coverage amount cannot be negative."))

    def set_defaults(self):
        if not self.status:
            self.status = "Active"

    def is_applicable(self, patient=None, service_amount=0):
        """Check if this coverage rule applies to a given patient and service amount."""
        if self.status != "Active":
            return False
        if self.patient and patient and self.patient != patient:
            return False
        if flt(self.amount) > 0 and flt(service_amount) > flt(self.amount):
            return False
        return True
