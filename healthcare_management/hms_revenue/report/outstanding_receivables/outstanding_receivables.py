import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Bill#", "fieldtype": "Link", "options": "Final Bill", "width": 150},
        {"fieldname": "patient_name", "label": "Patient", "fieldtype": "Data", "width": 180},
        {"fieldname": "bill_date", "label": "Bill Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "total_charges", "label": "Total", "fieldtype": "Currency", "width": 120},
        {"fieldname": "amount_paid", "label": "Paid", "fieldtype": "Currency", "width": 120},
        {"fieldname": "balance_due", "label": "Balance Due", "fieldtype": "Currency", "width": 120},
        {"fieldname": "aging_days", "label": "Aging (days)", "fieldtype": "Int", "width": 110},
    ]
    data = frappe.db.sql("""
        SELECT name, patient_name, bill_date, total_charges, amount_paid, balance_due,
            DATEDIFF(%(as_on_date)s, bill_date) as aging_days
        FROM `tabFinal Bill`
        WHERE balance_due > 0 AND docstatus = 1
            AND bill_date <= %(as_on_date)s
        ORDER BY aging_days DESC
    """, filters, as_dict=True)
    return columns, data
