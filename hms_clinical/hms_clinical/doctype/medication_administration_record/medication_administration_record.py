import frappe
from frappe import _
from frappe.model.document import Document


class MedicationAdministrationRecord(Document):
    def validate(self):
        if self.status == "Administered" and not self.administered_time:
            self.administered_time = frappe.utils.now_datetime()
            self.administered_by = frappe.session.user
