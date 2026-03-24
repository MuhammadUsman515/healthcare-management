import frappe
from frappe.utils import now_datetime, add_to_date


def tat_breach_alerts():
    """Alert when lab tests breach expected TAT."""
    breached = frappe.db.sql("""
        SELECT lt.name, lt.test_name, lt.patient_name, lt.order_date,
               ltt.expected_tat_hours
        FROM `tabLab Test` lt
        LEFT JOIN `tabLab Test Template` ltt ON lt.test_template = ltt.name
        WHERE lt.status IN ('Ordered', 'Sample Collected', 'In Process', 'Result Entered')
        AND lt.order_date < DATE_SUB(NOW(), INTERVAL COALESCE(ltt.expected_tat_hours, 24) HOUR)
    """, as_dict=True)

    for test in breached:
        frappe.get_doc({
            "doctype": "Critical Value Alert",
            "title": f"TAT Breach: {test.test_name} - {test.patient_name}",
            "lab_test": test.name,
            "description": f"Expected TAT: {test.expected_tat_hours or 24}h. Ordered: {test.order_date}",
            "status": "Active",
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)


def pending_authorization_reminder():
    """Remind supervisors about pending authorizations."""
    pending = frappe.db.count("Lab Test", {"status": "Verified"})
    if pending > 0:
        supervisors = frappe.get_all(
            "Has Role",
            filters={"role": "Lab Supervisor", "parenttype": "User"},
            pluck="parent",
        )
        for user in supervisors:
            frappe.publish_realtime(
                "pending_lab_auth",
                {"count": pending},
                user=user,
            )


def qc_daily_review():
    """Generate daily QC review summary."""
    pass
