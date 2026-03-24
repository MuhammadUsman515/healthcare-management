import frappe
from frappe.utils import today, add_days


def outstanding_aging_update():
    """Update aging of outstanding receivables."""
    pass


def claim_follow_up_reminder():
    """Remind about insurance claims pending more than 30 days."""
    threshold = add_days(today(), -30)
    pending = frappe.get_all("Claim Submission", filters={
        "status": "Active",
        "date": ["<", threshold],
    }, pluck="name")
    for claim in pending:
        pass  # notification logic


def fund_utilization_report():
    """Generate weekly fund utilization summary."""
    pass
