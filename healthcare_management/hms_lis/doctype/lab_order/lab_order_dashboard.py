from frappe import _

def get_data():
    return {
        "fieldname": "lab_order",
        "transactions": [
            {"label": _("Lab"), "items": ["Lab Test", "Sample Collection"]},
        ],
    }
