import frappe
from frappe.utils import today, add_days


def expiry_alerts():
    """Alert about drugs expiring within 30 days."""
    threshold = add_days(today(), 30)
    expiring = frappe.db.sql("""
        SELECT name, title as batch_name, expiry_date
        FROM `tabBatch`
        WHERE expiry_date <= %s AND expiry_date >= %s
        AND status = 'Active'
    """, (threshold, today()), as_dict=True)

    for batch in expiring:
        frappe.get_doc({
            "doctype": "Expiry Monitoring Rule",
            "title": f"Expiring: {batch.batch_name} on {batch.expiry_date}",
            "description": f"Batch {batch.batch_name} expires on {batch.expiry_date}",
        }).insert(ignore_permissions=True, ignore_if_duplicate=True)


def stockout_alerts():
    """Alert about drugs below reorder level."""
    low_stock = frappe.db.sql("""
        SELECT name, drug_name, current_stock, reorder_level
        FROM `tabDrug Item`
        WHERE current_stock <= reorder_level
        AND reorder_level > 0 AND is_active = 1
    """, as_dict=True)

    for drug in low_stock:
        frappe.publish_realtime(
            "stockout_alert",
            {"drug": drug.drug_name, "stock": drug.current_stock, "reorder": drug.reorder_level},
        )


def controlled_drug_daily_report():
    """Generate daily controlled drug movement report."""
    pass
