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


def create_subsidy_ledger(doc, method=None):
    """Create a Patient Subsidy Ledger entry when a welfare approval is submitted."""
    if doc.decision != "Approved" or not doc.approved_amount:
        return

    if frappe.db.exists("Patient Subsidy Ledger", {"welfare_approval": doc.name}):
        return

    frappe.get_doc({
        "doctype": "Patient Subsidy Ledger",
        "patient": doc.patient,
        "welfare_case": doc.welfare_case,
        "welfare_approval": doc.name,
        "amount": doc.approved_amount,
        "transaction_type": "Subsidy",
        "posting_date": frappe.utils.today(),
        "remarks": _("Auto-created from Welfare Approval {0}").format(doc.name),
    }).insert(ignore_permissions=True)
