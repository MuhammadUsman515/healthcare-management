import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "fund", "label": "Fund", "fieldtype": "Data", "width": 200},
        {"fieldname": "received", "label": "Received", "fieldtype": "Currency", "width": 150},
        {"fieldname": "utilized", "label": "Utilized", "fieldtype": "Currency", "width": 150},
        {"fieldname": "balance", "label": "Balance", "fieldtype": "Currency", "width": 150},
        {"fieldname": "utilization_pct", "label": "Utilization %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT df.title as fund,
            COALESCE(SUM(dr.amount), 0) as received,
            COALESCE(df.current_balance, 0) as balance,
            COALESCE(SUM(dr.amount), 0) - COALESCE(df.current_balance, 0) as utilized,
            ROUND((COALESCE(SUM(dr.amount), 0) - COALESCE(df.current_balance, 0)) * 100.0 / NULLIF(SUM(dr.amount), 0), 1) as utilization_pct
        FROM `tabDonation Fund` df
        LEFT JOIN `tabDonation Receipt` dr ON dr.donation_fund = df.name AND dr.docstatus = 1
        GROUP BY df.name, df.title, df.current_balance
        ORDER BY received DESC
    """, as_dict=True)
    return columns, data
