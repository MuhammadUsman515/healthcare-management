from frappe import _


def get_data():
    return {
        "heatmap": True,
        "heatmap_message": _("Patient activity over the year"),
        "fieldname": "appointment_date",
        "transactions": [
            {
                "label": _("Clinical"),
                "items": ["Appointment", "Vital Signs", "Clinical Procedure"],
            },
            {
                "label": _("Diagnostics & Treatment"),
                "items": ["Lab Test", "Prescription"],
            },
        ],
    }
