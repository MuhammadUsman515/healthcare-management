import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "denial_reason", "label": "Denial Reason", "fieldtype": "Data", "width": 250},
        {"fieldname": "total_denied", "label": "Denied Claims", "fieldtype": "Int", "width": 120},
        {"fieldname": "denied_amount", "label": "Denied Amount", "fieldtype": "Currency", "width": 140},
        {"fieldname": "payer", "label": "Payer", "fieldtype": "Data", "width": 150},
        {"fieldname": "denial_pct", "label": "Denial %", "fieldtype": "Percent", "width": 100},
    ]
    data = frappe.db.sql("""
        SELECT COALESCE(cs.denial_reason, 'Unknown') as denial_reason,
            COUNT(*) as total_denied,
            SUM(cs.claim_amount) as denied_amount,
            cs.payer,
            ROUND(COUNT(*) * 100.0 / NULLIF(
                (SELECT COUNT(*) FROM `tabClaim Submission` WHERE DATE(submission_date) BETWEEN %(from_date)s AND %(to_date)s), 0), 1) as denial_pct
        FROM `tabClaim Submission` cs
        WHERE cs.status = 'Denied'
            AND DATE(cs.submission_date) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY cs.denial_reason, cs.payer
        ORDER BY total_denied DESC
    """, filters, as_dict=True)
    return columns, data
