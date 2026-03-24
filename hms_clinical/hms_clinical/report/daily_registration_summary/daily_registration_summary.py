import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "new_patients", "label": "New Patients", "fieldtype": "Int", "width": 120},
        {"fieldname": "male", "label": "Male", "fieldtype": "Int", "width": 80},
        {"fieldname": "female", "label": "Female", "fieldtype": "Int", "width": 80},
        {"fieldname": "branch", "label": "Branch", "fieldtype": "Data", "width": 150},
    ]
    data = frappe.db.sql("""
        SELECT DATE(creation) as date,
            COUNT(*) as new_patients,
            SUM(CASE WHEN gender = 'Male' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN gender = 'Female' THEN 1 ELSE 0 END) as female,
            COALESCE(branch, 'Unassigned') as branch
        FROM `tabPatient`
        WHERE DATE(creation) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY DATE(creation), branch
        ORDER BY date DESC
    """, filters, as_dict=True)
    return columns, data
