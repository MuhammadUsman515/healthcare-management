import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access your profile.", frappe.PermissionError)

    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        frappe.throw("No patient record linked to your account.")

    context.patient = frappe.get_doc("Patient", patient)
    context.no_cache = 1
