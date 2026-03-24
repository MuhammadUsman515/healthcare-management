app_name = "hms_clinical"
app_title = "HMS Clinical"
app_publisher = "Healthcare Team"
app_description = "Clinical module - OPD, IPD, EMR, encounters, nursing, procedures, discharge"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe", "hms_core"]

doc_events = {
    "Patient": {
        "after_insert": "hms_clinical.hms_clinical.doctype.patient.patient.after_insert",
    },
    "Encounter": {
        "on_update": "hms_clinical.hms_clinical.doctype.encounter.encounter.on_update",
    },
    "Appointment": {
        "after_insert": "hms_clinical.hms_clinical.doctype.appointment.appointment.send_confirmation",
    },
}

scheduler_events = {
    "daily": [
        "hms_clinical.hms_clinical.api.tasks.mark_no_show_appointments",
        "hms_clinical.hms_clinical.api.tasks.follow_up_reminders",
    ],
    "hourly": [
        "hms_clinical.hms_clinical.api.tasks.overdue_nursing_tasks_alert",
    ],
}

override_whitelisted_methods = {}
