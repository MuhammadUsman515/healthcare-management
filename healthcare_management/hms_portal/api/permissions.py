import frappe


def has_lab_report_permission(doc, ptype=None, user=None):
    """Website permission check for lab reports."""
    if not user:
        user = frappe.session.user
    if user == "Guest":
        return False

    patient = frappe.db.get_value("Patient", {"user": user}, "name")
    if not patient:
        return False

    return doc.patient == patient and doc.status == "Released"
