import frappe


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw("Please login to view lab results.", frappe.PermissionError)
    context.no_cache = 1
