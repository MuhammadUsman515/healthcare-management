import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "department", "label": "Specialty", "fieldtype": "Data", "width": 200},
        {"fieldname": "bill_count", "label": "Bills", "fieldtype": "Int", "width": 80},
        {"fieldname": "total_charges", "label": "Total Charges", "fieldtype": "Currency", "width": 140},
        {"fieldname": "collected", "label": "Collected", "fieldtype": "Currency", "width": 140},
        {"fieldname": "outstanding", "label": "Outstanding", "fieldtype": "Currency", "width": 140},
        {"fieldname": "collection_pct", "label": "Collection %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT COALESCE(department, 'General') as department,
            COUNT(*) as bill_count,
            SUM(total_charges) as total_charges,
            SUM(amount_paid) as collected,
            SUM(balance_due) as outstanding,
            ROUND(SUM(amount_paid) * 100.0 / NULLIF(SUM(total_charges), 0), 1) as collection_pct
        FROM `tabFinal Bill`
        WHERE bill_date BETWEEN %(from_date)s AND %(to_date)s AND docstatus = 1
        GROUP BY department
        ORDER BY total_charges DESC
    """, filters, as_dict=True)
    return columns, data
