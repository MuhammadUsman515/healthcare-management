import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "test_group", "label": "Department", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_tests", "label": "Total Tests", "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_tat", "label": "Avg TAT (min)", "fieldtype": "Int", "width": 120},
        {"fieldname": "max_tat", "label": "Max TAT (min)", "fieldtype": "Int", "width": 120},
        {"fieldname": "breached", "label": "TAT Breached", "fieldtype": "Int", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT test_group,
            COUNT(*) as total_tests,
            ROUND(AVG(tat_minutes)) as avg_tat,
            MAX(tat_minutes) as max_tat,
            SUM(CASE WHEN tat_minutes > 1440 THEN 1 ELSE 0 END) as breached
        FROM `tabLab Test`
        WHERE order_date BETWEEN %(from_date)s AND %(to_date)s
        AND status IN ('Authorized', 'Released')
        AND tat_minutes IS NOT NULL
        GROUP BY test_group
        ORDER BY avg_tat DESC
    """, filters, as_dict=True)
    return columns, data
