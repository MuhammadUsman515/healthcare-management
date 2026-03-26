import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "rejection_reason", "label": "Rejection Reason", "fieldtype": "Data", "width": 250},
        {"fieldname": "total_rejected", "label": "Rejected", "fieldtype": "Int", "width": 100},
        {"fieldname": "total_collected", "label": "Total Collected", "fieldtype": "Int", "width": 130},
        {"fieldname": "rejection_pct", "label": "Rejection %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT sr.rejection_reason,
            COUNT(sr.name) as total_rejected,
            (SELECT COUNT(*) FROM `tabSample Collection` sc2
                WHERE DATE(sc2.collection_date) BETWEEN %(from_date)s AND %(to_date)s) as total_collected,
            ROUND(COUNT(sr.name) * 100.0 / NULLIF(
                (SELECT COUNT(*) FROM `tabSample Collection` sc2
                    WHERE DATE(sc2.collection_date) BETWEEN %(from_date)s AND %(to_date)s), 0), 2) as rejection_pct
        FROM `tabSample Rejection` sr
        JOIN `tabSample Collection` sc ON sr.sample_collection = sc.name
        WHERE DATE(sc.collection_date) BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY sr.rejection_reason
        ORDER BY total_rejected DESC
    """, filters, as_dict=True)
    return columns, data
