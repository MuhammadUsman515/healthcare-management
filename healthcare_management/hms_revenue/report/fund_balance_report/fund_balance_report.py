import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Fund", "fieldtype": "Link", "options": "Donation Fund", "width": 200},
        {"fieldname": "title", "label": "Fund Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "total_received", "label": "Total Received", "fieldtype": "Currency", "width": 140},
        {"fieldname": "total_disbursed", "label": "Total Disbursed", "fieldtype": "Currency", "width": 140},
        {"fieldname": "current_balance", "label": "Current Balance", "fieldtype": "Currency", "width": 140},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""
        SELECT df.name, df.title,
            COALESCE((SELECT SUM(dr.amount) FROM `tabDonation Receipt` dr
                WHERE dr.donation_fund = df.name AND dr.docstatus = 1), 0) as total_received,
            COALESCE((SELECT SUM(wd.amount) FROM `tabWelfare Disbursement` wd
                WHERE wd.donation_fund = df.name AND wd.docstatus = 1), 0) as total_disbursed,
            COALESCE(df.current_balance, 0) as current_balance,
            df.status
        FROM `tabDonation Fund` df
        ORDER BY current_balance DESC
    """, as_dict=True)
    return columns, data
