import frappe

def execute(filters=None):
    days = filters.get("days_ahead") or 90
    columns = [
        {"fieldname": "drug_item", "label": "Drug Item", "fieldtype": "Link", "options": "Drug Item", "width": 200},
        {"fieldname": "batch_no", "label": "Batch No", "fieldtype": "Data", "width": 120},
        {"fieldname": "expiry_date", "label": "Expiry Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "days_to_expiry", "label": "Days to Expiry", "fieldtype": "Int", "width": 130},
        {"fieldname": "quantity", "label": "Qty on Hand", "fieldtype": "Float", "width": 110},
        {"fieldname": "store", "label": "Store", "fieldtype": "Data", "width": 150},
    ]
    data = frappe.db.sql("""
        SELECT drug_item, batch_no, expiry_date,
            DATEDIFF(expiry_date, CURDATE()) as days_to_expiry,
            quantity, store
        FROM `tabBatch`
        WHERE expiry_date IS NOT NULL
            AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL %(days)s DAY)
            AND quantity > 0
        ORDER BY expiry_date ASC
    """, {"days": days}, as_dict=True)
    return columns, data
