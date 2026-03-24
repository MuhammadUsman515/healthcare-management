import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "total_billed", "label": "Total Billed", "fieldtype": "Currency", "width": 150},
        {"fieldname": "collected", "label": "Collected", "fieldtype": "Currency", "width": 150},
        {"fieldname": "outstanding", "label": "Outstanding", "fieldtype": "Currency", "width": 150},
        {"fieldname": "bills_count", "label": "Bills", "fieldtype": "Int", "width": 80},
    ]
    data = frappe.db.sql("""
        SELECT DATE(bill_date) as date,
            SUM(patient_payable) as total_billed,
            SUM(amount_paid) as collected,
            SUM(balance_due) as outstanding,
            COUNT(*) as bills_count
        FROM `tabFinal Bill`
        WHERE bill_date BETWEEN %(from_date)s AND %(to_date)s
        AND docstatus = 1
        GROUP BY DATE(bill_date)
        ORDER BY date DESC
    """, filters, as_dict=True)
    return columns, data
