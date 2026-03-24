import frappe


def get_branch_name(branch):
    """Jinja method to get branch display name."""
    if not branch:
        return ""
    return frappe.db.get_value("Hospital Branch", branch, "branch_name") or branch


def get_department_name(department):
    """Jinja method to get department display name."""
    if not department:
        return ""
    return frappe.db.get_value("Department", department, "department_name") or department


@frappe.whitelist()
def get_active_branches(company=None):
    """Get all active branches, optionally filtered by company."""
    filters = {"is_active": 1}
    if company:
        filters["company"] = company
    return frappe.get_all(
        "Hospital Branch",
        filters=filters,
        fields=["name", "branch_name", "branch_type", "city"],
        order_by="branch_name",
    )


@frappe.whitelist()
def get_departments(branch=None, department_type=None):
    """Get departments with optional filters."""
    filters = {"is_active": 1}
    if branch:
        filters["branch"] = branch
    if department_type:
        filters["department_type"] = department_type
    return frappe.get_all(
        "Department",
        filters=filters,
        fields=["name", "department_name", "department_type"],
        order_by="department_name",
    )
