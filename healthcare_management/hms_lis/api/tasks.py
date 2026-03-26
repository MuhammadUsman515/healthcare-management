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
    """Generate daily QC review summary and email to lab supervisors."""
    from frappe.utils import today, fmt_money

    qc_runs = frappe.get_all(
        "QC Run",
        filters={"date": today()},
        fields=["name", "analyzer", "test_template", "status", "mean_value",
                "sd_value", "cv_percent", "westgard_violation"],
    )

    if not qc_runs:
        return

    failed_runs = [r for r in qc_runs if r.status in ("Failed", "Rejected")]
    violation_runs = [r for r in qc_runs if r.westgard_violation]

    summary_rows = ""
    for run in qc_runs:
        indicator = "red" if run.status in ("Failed", "Rejected") else "green"
        violation = run.westgard_violation or "None"
        summary_rows += f"""
        <tr>
            <td>{run.name}</td>
            <td>{run.analyzer or '-'}</td>
            <td>{run.test_template or '-'}</td>
            <td style="color: {indicator};">{run.status}</td>
            <td>{run.mean_value or '-'}</td>
            <td>{run.sd_value or '-'}</td>
            <td>{run.cv_percent or '-'}%</td>
            <td>{violation}</td>
        </tr>"""

    message = f"""
    <h3>Daily QC Review Summary - {today()}</h3>
    <p>Total QC Runs: {len(qc_runs)} | Passed: {len(qc_runs) - len(failed_runs)}
    | Failed: {len(failed_runs)} | Westgard Violations: {len(violation_runs)}</p>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>QC Run</th><th>Analyzer</th><th>Test</th><th>Status</th>
                <th>Mean</th><th>SD</th><th>CV%</th><th>Violation</th>
            </tr>
        </thead>
        <tbody>{summary_rows}</tbody>
    </table>
    """

    supervisors = frappe.get_all(
        "Has Role",
        filters={"role": "Lab Supervisor", "parenttype": "User"},
        pluck="parent",
    )
    active_supervisors = [
        u for u in set(supervisors)
        if frappe.db.get_value("User", u, "enabled")
    ]

    if active_supervisors:
        frappe.sendmail(
            recipients=active_supervisors,
            subject=f"Daily QC Review Summary - {today()}",
            message=message,
        )
