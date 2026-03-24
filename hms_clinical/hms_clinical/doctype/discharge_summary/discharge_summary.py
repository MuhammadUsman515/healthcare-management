import frappe
from frappe import _
from frappe.model.document import Document


class DischargeSummary(Document):
    def on_submit(self):
        if self.admission:
            admission = frappe.get_doc("Inpatient Admission", self.admission)
            admission.db_set("discharge_summary", self.name)
            admission.db_set("status", "Billing Clearance")
            frappe.msgprint(_("Admission status updated to Billing Clearance."))
