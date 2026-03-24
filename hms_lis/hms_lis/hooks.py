app_name = "hms_lis"
app_title = "HMS LIS"
app_publisher = "Healthcare Team"
app_description = "Laboratory Information System - ordering, collection, analysis, authorization, reporting"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe", "hms_core"]

doc_events = {
    "Lab Test": {
        "on_update": "hms_lis.hms_lis.doctype.lab_test.lab_test.check_critical_value",
    },
    "Result Authorization": {
        "on_submit": "hms_lis.hms_lis.doctype.result_authorization.result_authorization.release_to_portal",
    },
}

scheduler_events = {
    "hourly": [
        "hms_lis.hms_lis.api.tasks.tat_breach_alerts",
        "hms_lis.hms_lis.api.tasks.pending_authorization_reminder",
    ],
    "daily": [
        "hms_lis.hms_lis.api.tasks.qc_daily_review",
    ],
}
