import frappe
from frappe.utils import today, add_days, getdate, date_diff, flt, fmt_money


def outstanding_aging_update():
    """Update aging buckets for all outstanding receivables (Final Bills)."""
    outstanding_bills = frappe.get_all(
        "Final Bill",
        filters={"docstatus": 1, "outstanding_amount": [">", 0]},
        fields=["name", "posting_date", "outstanding_amount", "patient",
                "patient_name", "payer_type"],
    )

    current_date = getdate(today())
    aging_buckets = {"0-30": 0, "31-60": 0, "61-90": 0, "91-120": 0, "120+": 0}
    updated = 0

    for bill in outstanding_bills:
        days = date_diff(current_date, bill.posting_date)

        if days <= 30:
            bucket = "0-30"
        elif days <= 60:
            bucket = "31-60"
        elif days <= 90:
            bucket = "61-90"
        elif days <= 120:
            bucket = "91-120"
        else:
            bucket = "120+"

        aging_buckets[bucket] += flt(bill.outstanding_amount)

        frappe.db.set_value("Final Bill", bill.name, {
            "aging_days": days,
            "aging_bucket": bucket,
        }, update_modified=False)
        updated += 1

    if updated:
        frappe.db.commit()

    # Log a summary for dashboard consumption
    if outstanding_bills:
        frappe.log_error(
            title="Daily Aging Update Summary",
            message=(
                f"Updated {updated} bills.\n"
                + "\n".join(f"  {k}: {fmt_money(v)}" for k, v in aging_buckets.items())
            ),
        )


def claim_follow_up_reminder():
    """Remind billing staff about insurance claims pending more than 30 days."""
    threshold = add_days(today(), -30)
    pending_claims = frappe.get_all(
        "Claim Submission",
        filters={
            "status": ["in", ["Submitted", "Active", "Under Review"]],
            "submission_date": ["<", threshold],
        },
        fields=["name", "patient_name", "insurance_company", "claim_amount",
                "submission_date", "status"],
        order_by="submission_date asc",
    )

    if not pending_claims:
        return

    rows = ""
    total_amount = 0
    for claim in pending_claims:
        days_pending = date_diff(today(), claim.submission_date)
        total_amount += flt(claim.claim_amount)
        rows += f"""
        <tr>
            <td>{claim.name}</td>
            <td>{claim.patient_name}</td>
            <td>{claim.insurance_company or '-'}</td>
            <td>{fmt_money(claim.claim_amount)}</td>
            <td>{claim.submission_date}</td>
            <td>{days_pending} days</td>
            <td>{claim.status}</td>
        </tr>"""

    message = f"""
    <h3>Insurance Claims Pending Follow-Up</h3>
    <p>{len(pending_claims)} claims pending over 30 days.
    Total outstanding: {fmt_money(total_amount)}</p>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>Claim</th><th>Patient</th><th>Insurer</th><th>Amount</th>
                <th>Submitted</th><th>Pending</th><th>Status</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """

    billing_users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", ["Cashier", "Healthcare Administrator"]],
                 "parenttype": "User"},
        pluck="parent",
    )
    active_users = [
        u for u in set(billing_users)
        if frappe.db.get_value("User", u, "enabled")
    ]

    if active_users:
        frappe.sendmail(
            recipients=active_users,
            subject=f"Claims Follow-Up: {len(pending_claims)} claims pending >30 days",
            message=message,
        )


def fund_utilization_report():
    """Generate weekly fund utilization summary for welfare and donation funds."""
    week_start = add_days(today(), -7)

    # Donations received this week
    donations = frappe.db.sql("""
        SELECT
            COALESCE(fund_type, 'General') AS fund_type,
            COUNT(*) AS count,
            SUM(amount) AS total
        FROM `tabDonation Receipt`
        WHERE docstatus = 1
        AND DATE(creation) >= %s
        GROUP BY fund_type
    """, week_start, as_dict=True)

    # Welfare disbursements this week
    disbursements = frappe.db.sql("""
        SELECT
            COALESCE(subsidy_type, 'General') AS subsidy_type,
            COUNT(*) AS count,
            SUM(approved_amount) AS total
        FROM `tabWelfare Approval Decision`
        WHERE docstatus = 1
        AND DATE(creation) >= %s
        AND decision = 'Approved'
        GROUP BY subsidy_type
    """, week_start, as_dict=True)

    # Current fund balances
    balances = frappe.db.sql("""
        SELECT
            COALESCE(fund_type, 'General') AS fund_type,
            SUM(credit - debit) AS balance
        FROM `tabPatient Subsidy Ledger`
        WHERE docstatus = 1
        GROUP BY fund_type
    """, as_dict=True)

    donation_rows = ""
    for d in donations:
        donation_rows += f"<tr><td>{d.fund_type}</td><td>{d.count}</td><td>{fmt_money(d.total)}</td></tr>"

    disbursement_rows = ""
    for d in disbursements:
        disbursement_rows += f"<tr><td>{d.subsidy_type}</td><td>{d.count}</td><td>{fmt_money(d.total)}</td></tr>"

    balance_rows = ""
    for b in balances:
        balance_rows += f"<tr><td>{b.fund_type}</td><td>{fmt_money(b.balance)}</td></tr>"

    message = f"""
    <h3>Weekly Fund Utilization Report ({week_start} to {today()})</h3>

    <h4>Donations Received</h4>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead><tr><th>Fund Type</th><th>Count</th><th>Total</th></tr></thead>
        <tbody>{donation_rows or '<tr><td colspan="3">No donations this week</td></tr>'}</tbody>
    </table>

    <h4>Welfare Disbursements (Approved)</h4>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead><tr><th>Subsidy Type</th><th>Count</th><th>Total</th></tr></thead>
        <tbody>{disbursement_rows or '<tr><td colspan="3">No disbursements this week</td></tr>'}</tbody>
    </table>

    <h4>Current Fund Balances</h4>
    <table border="1" cellpadding="4" cellspacing="0" style="border-collapse: collapse;">
        <thead><tr><th>Fund Type</th><th>Balance</th></tr></thead>
        <tbody>{balance_rows or '<tr><td colspan="2">No fund data available</td></tr>'}</tbody>
    </table>
    """

    admin_users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", ["Healthcare Administrator", "Welfare Officer",
                                   "Welfare Committee"]],
                 "parenttype": "User"},
        pluck="parent",
    )
    active_users = [
        u for u in set(admin_users)
        if frappe.db.get_value("User", u, "enabled")
    ]

    if active_users:
        frappe.sendmail(
            recipients=active_users,
            subject=f"Weekly Fund Utilization Report - {today()}",
            message=message,
        )
