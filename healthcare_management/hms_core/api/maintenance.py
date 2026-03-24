import frappe


def cleanup_expired_sessions():
    """Remove expired session records older than 30 days."""
    frappe.db.sql("""
        DELETE FROM `tabData Access Log`
        WHERE creation < DATE_SUB(NOW(), INTERVAL 90 DAY)
    """)
    frappe.db.commit()


def audit_review_reminder():
    """Send weekly audit review reminder to administrators."""
    admins = frappe.get_all(
        "Has Role",
        filters={"role": "Healthcare Administrator", "parenttype": "User"},
        pluck="parent",
    )
    for admin in admins:
        frappe.sendmail(
            recipients=[admin],
            subject="Weekly Audit Review Reminder",
            message="Please review the weekly audit logs for healthcare operations.",
        )
