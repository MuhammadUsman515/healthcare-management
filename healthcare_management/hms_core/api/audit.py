import frappe

AUDITABLE_DOCTYPES = [
    "Patient", "Encounter", "Prescription", "Lab Test", "Result Authorization",
    "Vital Signs", "Inpatient Admission", "Discharge Summary", "Final Bill",
    "Donation Receipt", "Welfare Approval Decision", "Patient Subsidy Ledger",
    "Dispense Slip", "POS Invoice", "Cashier Receipt", "Payment Entry",
]


def log_document_event(doc, method=None):
    """Log document changes for auditable healthcare records."""
    if doc.doctype not in AUDITABLE_DOCTYPES:
        return

    try:
        frappe.get_doc({
            "doctype": "Data Access Log",
            "data_access_log_name": f"{doc.doctype} - {doc.name}",
            "description": f"{method or 'unknown'} by {frappe.session.user}",
            "is_active": 1,
        }).insert(ignore_permissions=True)
    except Exception:
        pass
