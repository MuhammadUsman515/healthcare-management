import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "practitioner_name", "label": "Doctor", "fieldtype": "Data", "width": 200},
        {"fieldname": "total_patients", "label": "Patients", "fieldtype": "Int", "width": 90},
        {"fieldname": "avg_wait_min", "label": "Avg Wait (min)", "fieldtype": "Int", "width": 120},
        {"fieldname": "max_wait_min", "label": "Max Wait (min)", "fieldtype": "Int", "width": 120},
        {"fieldname": "within_30", "label": "Within 30 min", "fieldtype": "Int", "width": 120},
    ]
    conditions = "WHERE a.appointment_date BETWEEN %(from_date)s AND %(to_date)s AND a.status IN ('Completed', 'In Consultation')"
    if filters.get("department"):
        conditions += " AND a.department = %(department)s"
    data = frappe.db.sql("""
        SELECT a.department, a.practitioner_name,
            COUNT(*) as total_patients,
            ROUND(AVG(TIMESTAMPDIFF(MINUTE, a.appointment_time, a.consultation_start_time))) as avg_wait_min,
            MAX(TIMESTAMPDIFF(MINUTE, a.appointment_time, a.consultation_start_time)) as max_wait_min,
            SUM(CASE WHEN TIMESTAMPDIFF(MINUTE, a.appointment_time, a.consultation_start_time) <= 30 THEN 1 ELSE 0 END) as within_30
        FROM `tabAppointment` a
        {conditions}
        GROUP BY a.department, a.practitioner_name
        ORDER BY avg_wait_min DESC
    """.format(conditions=conditions), filters, as_dict=True)
    return columns, data
