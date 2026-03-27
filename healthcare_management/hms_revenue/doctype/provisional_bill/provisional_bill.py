import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate, flt


class ProvisionalBill(Document):
    def validate(self):
        self.validate_amount()
        self.validate_patient()
        self.set_defaults()

    def validate_amount(self):
        if flt(self.amount) < 0:
            frappe.throw(_("Bill amount cannot be negative."))

    def validate_patient(self):
        if not self.patient:
            frappe.throw(_("Patient is required for a Provisional Bill."))

    def set_defaults(self):
        if not self.date:
            self.date = nowdate()
        if not self.status:
            self.status = "Active"
        if not self.title:
            self.title = f"Provisional Bill - {self.patient}"

    def before_submit(self):
        self.status = "Completed"

    def on_cancel(self):
        self.status = "Cancelled"

    @frappe.whitelist()
    def convert_to_final_bill(self):
        """Create a Final Bill from this Provisional Bill."""
        if self.status == "Cancelled":
            frappe.throw(_("Cannot convert a cancelled Provisional Bill."))

        final_bill = frappe.new_doc("Final Bill")
        final_bill.patient = self.patient
        final_bill.amount = self.amount
        final_bill.description = self.description
        final_bill.date = nowdate()
        final_bill.insert(ignore_permissions=True)

        self.status = "Completed"
        self.save()

        frappe.msgprint(_("Final Bill {0} created.").format(final_bill.name))
        return final_bill.name
