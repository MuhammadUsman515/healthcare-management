import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "drug_item", "label": "Drug Item", "fieldtype": "Link", "options": "Drug Item", "width": 200},
        {"fieldname": "generic_name", "label": "Generic", "fieldtype": "Data", "width": 150},
        {"fieldname": "total_dispensed", "label": "Total Dispensed", "fieldtype": "Float", "width": 130},
        {"fieldname": "current_stock", "label": "Current Stock", "fieldtype": "Float", "width": 120},
        {"fieldname": "days_of_stock", "label": "Days of Stock", "fieldtype": "Int", "width": 120},
        {"fieldname": "category", "label": "Category", "fieldtype": "Data", "width": 100},
    ]
    conditions = ""
    if filters.get("store"):
        conditions = "AND b.store = %(store)s"
    data = frappe.db.sql("""
        SELECT d.name as drug_item, d.generic_name,
            COALESCE(disp.total_dispensed, 0) as total_dispensed,
            COALESCE(stk.current_stock, 0) as current_stock,
            CASE WHEN COALESCE(disp.daily_avg, 0) > 0
                THEN ROUND(COALESCE(stk.current_stock, 0) / disp.daily_avg)
                ELSE 999 END as days_of_stock,
            CASE
                WHEN COALESCE(disp.total_dispensed, 0) = 0 THEN 'Dead'
                WHEN COALESCE(disp.daily_avg, 0) >= 5 THEN 'Fast'
                WHEN COALESCE(disp.daily_avg, 0) >= 1 THEN 'Medium'
                ELSE 'Slow'
            END as category
        FROM `tabDrug Item` d
        LEFT JOIN (
            SELECT di.drug_item,
                SUM(di.quantity) as total_dispensed,
                SUM(di.quantity) / NULLIF(DATEDIFF(%(to_date)s, %(from_date)s), 0) as daily_avg
            FROM `tabDispense Item` di
            JOIN `tabDispense Slip` ds ON di.parent = ds.name
            WHERE DATE(ds.dispense_date) BETWEEN %(from_date)s AND %(to_date)s
                AND ds.docstatus = 1
            GROUP BY di.drug_item
        ) disp ON disp.drug_item = d.name
        LEFT JOIN (
            SELECT drug_item, SUM(quantity) as current_stock
            FROM `tabBatch` b
            WHERE quantity > 0 {conditions}
            GROUP BY drug_item
        ) stk ON stk.drug_item = d.name
        ORDER BY total_dispensed DESC
    """.format(conditions=conditions), filters, as_dict=True)
    return columns, data
