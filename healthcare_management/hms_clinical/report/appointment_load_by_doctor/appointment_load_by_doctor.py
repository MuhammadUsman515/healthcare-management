import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "practitioner_name", "label": "Doctor", "fieldtype": "Data", "width": 200},
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "total", "label": "Total", "fieldtype": "Int", "width": 80},
        {"fieldname": "completed", "label": "Completed", "fieldtype": "Int", "width": 100},
        {"fieldname": "no_show", "label": "No Show", "fieldtype": "Int", "width": 80},
        {"fieldname": "cancelled", "label": "Cancelled", "fieldtype": "Int", "width": 100},
    ]
    data = frappe.db.sql("""
        SELECT practitioner_name, department,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'No Show' THEN 1 ELSE 0 END) as no_show,
            SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
        FROM `tabAppointment`
        WHERE appointment_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY practitioner_name, department
        ORDER BY total DESC
    """, filters, as_dict=True)
    return columns, data
