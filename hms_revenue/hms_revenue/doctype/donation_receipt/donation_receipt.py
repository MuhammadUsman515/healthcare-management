import frappe
from frappe import _
from frappe.model.document import Document


class DonationReceipt(Document):
    def on_submit(self):
        if self.donation_fund:
            frappe.db.sql("""
                UPDATE `tabDonation Fund` SET current_balance = current_balance + %s
                WHERE name = %s
            """, (self.amount, self.donation_fund))
            frappe.db.commit()


def send_donor_acknowledgment(doc, method=None):
    if doc.donor:
        pass  # Email/SMS acknowledgment
