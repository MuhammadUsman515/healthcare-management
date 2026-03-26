from frappe import _

def get_data():
    return {
        "heatmap": True,
        "heatmap_message": _("Patient activity over the year"),
        "fieldname": "patient",
        "transactions": [
            {
                "label": _("Clinical"),
                "items": ["Appointment", "Encounter", "Prescription", "Vital Signs"]
            },
            {
                "label": _("Inpatient"),
                "items": ["Inpatient Admission", "Discharge Summary", "Nursing Task"]
            },
            {
                "label": _("Diagnostics"),
                "items": ["Lab Order", "Lab Test", "Sample Collection"]
            },
            {
                "label": _("Billing"),
                "items": ["Final Bill", "Deposit", "Cashier Receipt"]
            },
        ],
    }
