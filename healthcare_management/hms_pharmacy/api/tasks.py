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
    """Generate daily controlled drug movement report and email to pharmacy head."""
    yesterday = add_days(today(), -1)

    # Gather all controlled drug dispensing from the previous day
    movements = frappe.db.sql("""
        SELECT
            ds.name AS dispense_slip,
            dsi.drug_name,
            dsi.drug_item,
            dsi.quantity,
            ds.patient_name,
            ds.practitioner_name,
            ds.pharmacist,
            ds.creation
        FROM `tabDispense Slip` ds
        INNER JOIN `tabDispense Slip Item` dsi ON dsi.parent = ds.name
        INNER JOIN `tabDrug Item` di ON di.name = dsi.drug_item
        WHERE di.is_controlled = 1
        AND DATE(ds.creation) = %s
        AND ds.docstatus = 1
        ORDER BY ds.creation
    """, yesterday, as_dict=True)

    if not movements:
        return

    # Build report table
    rows = ""
    total_qty = 0
    for m in movements:
        total_qty += m.quantity or 0
        rows += f"""
        <tr>
            <td>{m.dispense_slip}</td>
            <td>{m.drug_name}</td>
            <td>{m.quantity}</td>
            <td>{m.patient_name}</td>
            <td>{m.practitioner_name or '-'}</td>
            <td>{m.pharmacist or '-'}</td>
            <td>{frappe.utils.format_datetime(m.creation, "HH:mm")}</td>
        </tr>"""

    message = f"""
    <h3>Controlled Drug Movement Report - {yesterday}</h3>
    <p>Total controlled dispensing events: {len(movements)} | Total units dispensed: {total_qty}</p>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>Dispense Slip</th><th>Drug</th><th>Qty</th>
                <th>Patient</th><th>Prescriber</th><th>Pharmacist</th><th>Time</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    <p><em>This is an automated report. Any discrepancies must be investigated immediately
    and reported to the Chief Pharmacist.</em></p>
    """

    # Send to pharmacy heads and healthcare administrators
    recipients = set()
    for role in ("Pharmacist", "Healthcare Administrator"):
        users = frappe.get_all(
            "Has Role",
            filters={"role": role, "parenttype": "User"},
            pluck="parent",
        )
        recipients.update(users)

    active_recipients = [
        u for u in recipients
        if frappe.db.get_value("User", u, "enabled")
    ]

    if active_recipients:
        frappe.sendmail(
            recipients=active_recipients,
            subject=f"Controlled Drug Daily Report - {yesterday}",
            message=message,
        )
