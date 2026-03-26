import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "discount_type", "label": "Discount Type", "fieldtype": "Data", "width": 180},
        {"fieldname": "bill_count", "label": "Bills", "fieldtype": "Int", "width": 80},
        {"fieldname": "total_charges", "label": "Total Charges", "fieldtype": "Currency", "width": 140},
        {"fieldname": "discount_amount", "label": "Discount Given", "fieldtype": "Currency", "width": 140},
        {"fieldname": "discount_pct", "label": "Discount %", "fieldtype": "Percent", "width": 110},
    ]
    data = frappe.db.sql("""
        SELECT COALESCE(discount_type, 'No Discount') as discount_type,
            COUNT(*) as bill_count,
            SUM(total_charges) as total_charges,
            SUM(discount_amount) as discount_amount,
            ROUND(SUM(discount_amount) * 100.0 / NULLIF(SUM(total_charges), 0), 1) as discount_pct
        FROM `tabFinal Bill`
        WHERE bill_date BETWEEN %(from_date)s AND %(to_date)s AND docstatus = 1
        GROUP BY discount_type
        ORDER BY discount_amount DESC
    """, filters, as_dict=True)
    return columns, data
