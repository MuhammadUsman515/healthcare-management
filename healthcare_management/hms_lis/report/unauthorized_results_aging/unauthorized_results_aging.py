import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Test ID", "fieldtype": "Link", "options": "Lab Test", "width": 150},
        {"fieldname": "patient_name", "label": "Patient", "fieldtype": "Data", "width": 180},
        {"fieldname": "test_name", "label": "Test", "fieldtype": "Data", "width": 180},
        {"fieldname": "test_group", "label": "Group", "fieldtype": "Data", "width": 120},
        {"fieldname": "order_date", "label": "Order Date", "fieldtype": "Date", "width": 110},
        {"fieldname": "aging_hours", "label": "Aging (hours)", "fieldtype": "Int", "width": 120},
        {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 90},
    ]
    data = frappe.db.sql("""
        SELECT name, patient_name, test_name, test_group, order_date,
            ROUND(TIMESTAMPDIFF(HOUR, creation, NOW())) as aging_hours,
            priority
        FROM `tabLab Test`
        WHERE status IN ('Completed', 'Verified')
            AND authorized_datetime IS NULL
        ORDER BY aging_hours DESC
    """, as_dict=True)
    return columns, data
