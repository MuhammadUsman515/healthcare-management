from frappe import _

def get_data():
    return {
        "heatmap": True,
        "heatmap_message": _("Practitioner activity"),
        "fieldname": "practitioner",
        "transactions": [
            {"label": _("Clinical"), "items": ["Appointment", "Encounter", "Prescription"]},
            {"label": _("Inpatient"), "items": ["Inpatient Admission"]},
        ],
    }
