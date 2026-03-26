import frappe
from frappe import _
from frappe.model.document import Document


class WelfareApprovalDecision(Document):
    def on_submit(self):
        self.update_welfare_case()

    def update_welfare_case(self):
        if self.welfare_case:
            if self.decision == "Approved":
                frappe.db.set_value("Patient Welfare Case", self.welfare_case, {
                    "status": "Approved",
                    "approved_amount": self.approved_amount,
                })
            else:
                frappe.db.set_value("Patient Welfare Case", self.welfare_case, {
                    "status": "Rejected",
                })
