from frappe import _

def get_data():
    return {
        "fieldname": "encounter",
        "transactions": [
            {"label": _("Orders"), "items": ["Prescription", "Lab Order", "Procedure Order", "Referral Order"]},
            {"label": _("Notes"), "items": ["Clinical Note", "Progress Note"]},
        ],
    }
