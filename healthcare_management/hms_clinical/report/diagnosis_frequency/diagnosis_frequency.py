import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "diagnosis", "label": "Diagnosis", "fieldtype": "Data", "width": 250},
        {"fieldname": "icd_code", "label": "ICD Code", "fieldtype": "Data", "width": 100},
        {"fieldname": "count", "label": "Count", "fieldtype": "Int", "width": 80},
        {"fieldname": "male", "label": "Male", "fieldtype": "Int", "width": 80},
        {"fieldname": "female", "label": "Female", "fieldtype": "Int", "width": 80},
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
    ]
    conditions = "WHERE e.encounter_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("department"):
        conditions += " AND e.department = %(department)s"
    data = frappe.db.sql("""
        SELECT d.diagnosis, d.icd_code,
            COUNT(*) as count,
            SUM(CASE WHEN e.patient_gender = 'Male' THEN 1 ELSE 0 END) as male,
            SUM(CASE WHEN e.patient_gender = 'Female' THEN 1 ELSE 0 END) as female,
            e.department
        FROM `tabDiagnosis` d
        JOIN `tabEncounter` e ON d.parent = e.name
        {conditions}
        GROUP BY d.diagnosis, d.icd_code, e.department
        ORDER BY count DESC
    """.format(conditions=conditions), filters, as_dict=True)
    return columns, data
