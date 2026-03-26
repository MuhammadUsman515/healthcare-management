import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "test_group", "label": "Department / Group", "fieldtype": "Data", "width": 200},
        {"fieldname": "total_tests", "label": "Total Tests", "fieldtype": "Int", "width": 100},
        {"fieldname": "completed", "label": "Completed", "fieldtype": "Int", "width": 100},
        {"fieldname": "pending", "label": "Pending", "fieldtype": "Int", "width": 100},
        {"fieldname": "critical", "label": "Critical", "fieldtype": "Int", "width": 100},
        {"fieldname": "completion_pct", "label": "Completion %", "fieldtype": "Percent", "width": 120},
    ]
    data = frappe.db.sql("""
        SELECT COALESCE(test_group, 'Ungrouped') as test_group,
            COUNT(*) as total_tests,
            SUM(CASE WHEN status IN ('Authorized', 'Released') THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status IN ('Pending', 'In Progress') THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN result_status = 'Critical' THEN 1 ELSE 0 END) as critical,
            ROUND(SUM(CASE WHEN status IN ('Authorized', 'Released') THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as completion_pct
        FROM `tabLab Test`
        WHERE order_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY test_group
        ORDER BY total_tests DESC
    """, filters, as_dict=True)
    return columns, data
