import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access your appointments.", frappe.PermissionError)
    context.no_cache = 1
