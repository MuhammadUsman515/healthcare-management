from frappe import _

def get_data():
    return {
        "fieldname": "appointment",
        "transactions": [
            {"label": _("Clinical"), "items": ["Encounter", "Visit", "Check In", "Queue Token"]},
            {"label": _("Billing"), "items": ["Final Bill"]},
        ],
    }
