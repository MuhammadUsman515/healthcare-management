import frappe
from frappe import _
from frappe.model.document import Document


class ClaimSubmission(Document):
    def validate(self):
        if self.claim_amount and self.claim_amount <= 0:
            frappe.throw(_("Claim amount must be greater than zero."))

    def on_submit(self):
        self.status = "Submitted"

    @frappe.whitelist()
    def mark_approved(self, approved_amount):
        self.status = "Approved"
        self.approved_amount = approved_amount
        self.save()
        if self.final_bill:
            frappe.db.sql("""UPDATE `tabFinal Bill`
                SET insurance_covered = COALESCE(insurance_covered, 0) + %s
                WHERE name = %s""", (approved_amount, self.final_bill))
        frappe.msgprint(_("Claim approved for {0}.").format(approved_amount))

    @frappe.whitelist()
    def mark_denied(self, denial_reason):
        self.status = "Denied"
        self.denial_reason = denial_reason
        self.save()
        frappe.msgprint(_("Claim denied: {0}").format(denial_reason))
