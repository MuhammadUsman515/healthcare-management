import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "name", "label": "Test ID", "fieldtype": "Link", "options": "Lab Test", "width": 150},
        {"fieldname": "patient_name", "label": "Patient", "fieldtype": "Data", "width": 180},
        {"fieldname": "test_name", "label": "Test", "fieldtype": "Data", "width": 180},
        {"fieldname": "result_value", "label": "Value", "fieldtype": "Data", "width": 100},
        {"fieldname": "normal_range", "label": "Normal Range", "fieldtype": "Data", "width": 120},
        {"fieldname": "authorized_datetime", "label": "Authorized", "fieldtype": "Datetime", "width": 160},
    ]
    data = frappe.db.sql("""
        SELECT name, patient_name, test_name, result_value, normal_range, authorized_datetime
        FROM `tabLab Test`
        WHERE result_status = 'Critical'
        AND order_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY authorized_datetime DESC
    """, filters, as_dict=True)
    return columns, data
