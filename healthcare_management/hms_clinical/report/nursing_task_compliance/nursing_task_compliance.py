import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "ward", "label": "Ward", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_tasks", "label": "Total Tasks", "fieldtype": "Int", "width": 100},
        {"fieldname": "completed", "label": "Completed", "fieldtype": "Int", "width": 100},
        {"fieldname": "overdue", "label": "Overdue", "fieldtype": "Int", "width": 100},
        {"fieldname": "compliance_pct", "label": "Compliance %", "fieldtype": "Percent", "width": 120},
        {"fieldname": "avg_delay_min", "label": "Avg Delay (min)", "fieldtype": "Int", "width": 130},
    ]
    conditions = "WHERE DATE(nt.creation) BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("ward"):
        conditions += " AND nt.ward = %(ward)s"
    data = frappe.db.sql("""
        SELECT COALESCE(nt.ward, 'Unassigned') as ward,
            COUNT(*) as total_tasks,
            SUM(CASE WHEN nt.status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN nt.status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
            ROUND(SUM(CASE WHEN nt.status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 1) as compliance_pct,
            ROUND(AVG(CASE WHEN nt.status = 'Completed' AND nt.completed_at > nt.due_datetime
                THEN TIMESTAMPDIFF(MINUTE, nt.due_datetime, nt.completed_at) END)) as avg_delay_min
        FROM `tabNursing Task` nt
        {conditions}
        GROUP BY nt.ward
        ORDER BY compliance_pct ASC
    """.format(conditions=conditions), filters, as_dict=True)
    return columns, data
