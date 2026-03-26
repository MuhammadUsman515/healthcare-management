import frappe
from frappe import _
from frappe.model.document import Document


class PrescriptionFulfillment(Document):
    def on_submit(self):
        self.update_prescription_status()

    def update_prescription_status(self):
        if self.prescription:
            frappe.db.set_value("Prescription", self.prescription,
                "fulfillment_status", "Dispensed")
