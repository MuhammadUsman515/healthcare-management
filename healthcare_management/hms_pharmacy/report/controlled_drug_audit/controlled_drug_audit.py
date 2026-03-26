import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "drug_item", "label": "Drug", "fieldtype": "Data", "width": 200},
        {"fieldname": "controlled_class", "label": "Class", "fieldtype": "Data", "width": 80},
        {"fieldname": "dispensed_qty", "label": "Dispensed Qty", "fieldtype": "Float", "width": 120},
        {"fieldname": "dispense_count", "label": "Dispense Count", "fieldtype": "Int", "width": 120},
        {"fieldname": "patient_count", "label": "Unique Patients", "fieldtype": "Int", "width": 130},
        {"fieldname": "dispensed_by", "label": "Dispensed By", "fieldtype": "Data", "width": 150},
    ]
    data = frappe.db.sql("""
        SELECT di.drug_item, d.controlled_drug_class as controlled_class,
            SUM(di.quantity) as dispensed_qty,
            COUNT(DISTINCT ds.name) as dispense_count,
            COUNT(DISTINCT ds.patient) as patient_count,
            ds.dispensed_by
        FROM `tabDispense Item` di
        JOIN `tabDispense Slip` ds ON di.parent = ds.name
        JOIN `tabDrug Item` d ON di.drug_item = d.name
        WHERE d.controlled_drug_class IS NOT NULL
            AND d.controlled_drug_class != ''
            AND DATE(ds.dispense_date) BETWEEN %(from_date)s AND %(to_date)s
            AND ds.docstatus = 1
        GROUP BY di.drug_item, d.controlled_drug_class, ds.dispensed_by
        ORDER BY dispensed_qty DESC
    """, filters, as_dict=True)
    return columns, data
