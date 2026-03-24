import frappe
from frappe import _
from frappe.model.document import Document


class Prescription(Document):
    def validate(self):
        self.validate_duration()

    def validate_duration(self):
        if self.duration and self.duration <= 0:
            frappe.throw(_("Duration must be a positive number."))

    def before_submit(self):
        if not self.drug_name or not self.dosage:
            frappe.throw(_("Drug Name and Dosage are required before submitting."))
