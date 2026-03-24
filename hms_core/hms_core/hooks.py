app_name = "hms_core"
app_title = "HMS Core"
app_publisher = "Healthcare Team"
app_description = "Core foundation - shared masters, settings, identity, audit, notifications"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe"]

fixtures = [
    {"dt": "Role", "filters": [["name", "in", [
        "Healthcare Administrator",
        "Physician",
        "Nurse",
        "Lab Technician",
        "Lab Supervisor",
        "Pharmacist",
        "Cashier",
        "Welfare Officer",
        "Welfare Committee",
        "Branch Admin",
        "Hospital Admin",
        "Auditor",
    ]]]},
]

# Document Events
doc_events = {
    "*": {
        "after_insert": "hms_core.hms_core.api.audit.log_document_event",
        "on_update": "hms_core.hms_core.api.audit.log_document_event",
        "on_cancel": "hms_core.hms_core.api.audit.log_document_event",
    },
}

# Scheduled Tasks
scheduler_events = {
    "daily": [
        "hms_core.hms_core.api.maintenance.cleanup_expired_sessions",
    ],
    "weekly": [
        "hms_core.hms_core.api.maintenance.audit_review_reminder",
    ],
}

# Jinja
jinja = {
    "methods": [
        "hms_core.hms_core.api.utils.get_branch_name",
        "hms_core.hms_core.api.utils.get_department_name",
    ],
}
