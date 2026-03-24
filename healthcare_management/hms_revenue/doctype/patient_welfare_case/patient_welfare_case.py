import frappe
from frappe import _
from frappe.model.document import Document


class PatientWelfareCase(Document):
    def validate(self):
        self.check_documents()

    def check_documents(self):
        self.documents_complete = int(
            self.cnic_verified and self.income_proof and self.medical_report
        )

    def on_submit(self):
        self.db_set("status", "Submitted")

    @frappe.whitelist()
    def approve_welfare(self, amount, fund_source, remarks=None):
        """Committee approval."""
        frappe.only_for(["Welfare Committee", "Healthcare Administrator"])
        self.db_set("status", "Approved")
        self.db_set("approved_amount", amount)
        self.db_set("fund_source", fund_source)
        self.db_set("committee_decision", "Approved")
        self.db_set("committee_date", frappe.utils.today())
        if remarks:
            self.db_set("committee_remarks", remarks)

        # Create subsidy ledger
        frappe.get_doc({
            "doctype": "Patient Subsidy Ledger",
            "title": f"Welfare Subsidy - {self.patient_name}",
            "patient": self.patient,
            "description": f"Approved: {amount} from {fund_source}. Case: {self.name}",
            "status": "Active",
        }).insert(ignore_permissions=True)

        # Deduct from fund
        frappe.db.sql("""
            UPDATE `tabDonation Fund` SET current_balance = current_balance - %s
            WHERE name = %s
        """, (amount, fund_source))
        frappe.db.commit()

        frappe.msgprint(_("Welfare case approved for {0}").format(amount))

    @frappe.whitelist()
    def reject_welfare(self, reason):
        frappe.only_for(["Welfare Committee", "Healthcare Administrator"])
        self.db_set("status", "Rejected")
        self.db_set("committee_decision", "Rejected")
        self.db_set("committee_remarks", reason)
        self.db_set("committee_date", frappe.utils.today())
