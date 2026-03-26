import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "department", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_prescriptions", "label": "Prescriptions", "fieldtype": "Int", "width": 120},
        {"fieldname": "dispensed", "label": "Dispensed", "fieldtype": "Int", "width": 100},
        {"fieldname": "partially_dispensed", "label": "Partial", "fieldtype": "Int", "width": 100},
        {"fieldname": "not_dispensed", "label": "Not Dispensed", "fieldtype": "Int", "width": 120},
        {"fieldname": "conversion_pct", "label": "Conversion %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT COALESCE(p.department, 'Unknown') as department,
            COUNT(*) as total_prescriptions,
            SUM(CASE WHEN p.fulfillment_status = 'Dispensed' THEN 1 ELSE 0 END) as dispensed,
            SUM(CASE WHEN p.fulfillment_status = 'Partially Dispensed' THEN 1 ELSE 0 END) as partially_dispensed,
            SUM(CASE WHEN p.fulfillment_status IN ('Pending', 'Not Dispensed') OR p.fulfillment_status IS NULL THEN 1 ELSE 0 END) as not_dispensed,
            ROUND(SUM(CASE WHEN p.fulfillment_status IN ('Dispensed', 'Partially Dispensed') THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as conversion_pct
        FROM `tabPrescription` p
        WHERE DATE(p.creation) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY p.department
        ORDER BY conversion_pct DESC
    """, filters, as_dict=True)
    return columns, data
