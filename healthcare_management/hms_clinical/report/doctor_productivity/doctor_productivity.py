import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "practitioner_name", "label": "Doctor", "fieldtype": "Data", "width": 200},
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "appointments", "label": "Appointments", "fieldtype": "Int", "width": 110},
        {"fieldname": "encounters", "label": "Encounters", "fieldtype": "Int", "width": 100},
        {"fieldname": "prescriptions", "label": "Prescriptions", "fieldtype": "Int", "width": 110},
        {"fieldname": "lab_orders", "label": "Lab Orders", "fieldtype": "Int", "width": 100},
        {"fieldname": "admissions", "label": "Admissions", "fieldtype": "Int", "width": 100},
    ]
    conditions = ""
    if filters.get("practitioner"):
        conditions = "AND a.practitioner = %(practitioner)s"
    data = frappe.db.sql("""
        SELECT a.practitioner_name, a.department,
            COUNT(DISTINCT a.name) as appointments,
            (SELECT COUNT(*) FROM `tabEncounter` e WHERE e.practitioner = a.practitioner
                AND e.encounter_date BETWEEN %(from_date)s AND %(to_date)s) as encounters,
            (SELECT COUNT(*) FROM `tabPrescription` p WHERE p.practitioner = a.practitioner
                AND DATE(p.creation) BETWEEN %(from_date)s AND %(to_date)s) as prescriptions,
            (SELECT COUNT(*) FROM `tabLab Order` l WHERE l.requesting_practitioner = a.practitioner
                AND DATE(l.creation) BETWEEN %(from_date)s AND %(to_date)s) as lab_orders,
            (SELECT COUNT(*) FROM `tabInpatient Admission` ia WHERE ia.attending_practitioner = a.practitioner
                AND DATE(ia.admission_date) BETWEEN %(from_date)s AND %(to_date)s) as admissions
        FROM `tabAppointment` a
        WHERE a.appointment_date BETWEEN %(from_date)s AND %(to_date)s
            AND a.status NOT IN ('Cancelled', 'Rescheduled')
            {conditions}
        GROUP BY a.practitioner, a.practitioner_name, a.department
        ORDER BY encounters DESC
    """.format(conditions=conditions), filters, as_dict=True)
    return columns, data
