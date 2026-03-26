import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Case#", "fieldtype": "Link", "options": "Patient Welfare Case", "width": 150},
        {"fieldname": "patient_name", "label": "Patient", "fieldtype": "Data", "width": 180},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 120},
        {"fieldname": "requested_amount", "label": "Requested", "fieldtype": "Currency", "width": 120},
        {"fieldname": "approved_amount", "label": "Approved", "fieldtype": "Currency", "width": 120},
        {"fieldname": "aging_days", "label": "Aging (days)", "fieldtype": "Int", "width": 110},
        {"fieldname": "category", "label": "Category", "fieldtype": "Data", "width": 100},
    ]
    data = frappe.db.sql("""
        SELECT name, patient_name, status, requested_amount, approved_amount,
            DATEDIFF(CURDATE(), DATE(creation)) as aging_days,
            CASE
                WHEN DATEDIFF(CURDATE(), DATE(creation)) <= 7 THEN '0-7 days'
                WHEN DATEDIFF(CURDATE(), DATE(creation)) <= 30 THEN '8-30 days'
                WHEN DATEDIFF(CURDATE(), DATE(creation)) <= 90 THEN '31-90 days'
                ELSE '90+ days'
            END as category
        FROM `tabPatient Welfare Case`
        WHERE status NOT IN ('Closed', 'Cancelled')
        ORDER BY aging_days DESC
    """, as_dict=True)
    return columns, data
