import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "date", "label": "Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "admissions", "label": "Admissions", "fieldtype": "Int", "width": 100},
        {"fieldname": "discharges", "label": "Discharges", "fieldtype": "Int", "width": 100},
        {"fieldname": "transfers_in", "label": "Transfers In", "fieldtype": "Int", "width": 110},
        {"fieldname": "transfers_out", "label": "Transfers Out", "fieldtype": "Int", "width": 110},
        {"fieldname": "deaths", "label": "Deaths", "fieldtype": "Int", "width": 80},
        {"fieldname": "census", "label": "Midnight Census", "fieldtype": "Int", "width": 130},
    ]
    data = frappe.db.sql("""
        SELECT DATE(admission_date) as date,
            COUNT(*) as admissions,
            SUM(CASE WHEN status = 'Discharged' AND DATE(discharge_date) BETWEEN %(from_date)s AND %(to_date)s THEN 1 ELSE 0 END) as discharges,
            0 as transfers_in,
            0 as transfers_out,
            SUM(CASE WHEN status = 'Deceased' AND DATE(discharge_date) BETWEEN %(from_date)s AND %(to_date)s THEN 1 ELSE 0 END) as deaths,
            SUM(CASE WHEN status = 'Admitted' THEN 1 ELSE 0 END) as census
        FROM `tabInpatient Admission`
        WHERE DATE(admission_date) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY DATE(admission_date)
        ORDER BY date DESC
    """, filters, as_dict=True)
    return columns, data
