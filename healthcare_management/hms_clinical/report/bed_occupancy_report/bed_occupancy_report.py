import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "ward_name", "label": "Ward", "fieldtype": "Data", "width": 200},
        {"fieldname": "ward_type", "label": "Type", "fieldtype": "Data", "width": 120},
        {"fieldname": "total_beds", "label": "Total Beds", "fieldtype": "Int", "width": 100},
        {"fieldname": "occupied", "label": "Occupied", "fieldtype": "Int", "width": 100},
        {"fieldname": "available", "label": "Available", "fieldtype": "Int", "width": 100},
        {"fieldname": "occupancy_pct", "label": "Occupancy %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT w.ward_name, w.ward_type, w.total_beds,
            (SELECT COUNT(*) FROM `tabBed` b WHERE b.ward = w.name AND b.status = 'Occupied') as occupied,
            (SELECT COUNT(*) FROM `tabBed` b WHERE b.ward = w.name AND b.status = 'Available') as available,
            ROUND((SELECT COUNT(*) FROM `tabBed` b WHERE b.ward = w.name AND b.status = 'Occupied') * 100.0 / NULLIF(w.total_beds, 0), 1) as occupancy_pct
        FROM `tabWard` w
        WHERE w.is_active = 1
        ORDER BY occupancy_pct DESC
    """, as_dict=True)
    return columns, data
