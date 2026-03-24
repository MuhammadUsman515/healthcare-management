app_name = "healthcare_management"
app_title = "Healthcare Management"
app_publisher = "Healthcare Team"
app_description = "Comprehensive Healthcare Management System - OPD, IPD, EMR, LIS, Pharmacy, Revenue & Patient Portal"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe"]

# Fixtures
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

# --- Document Events (merged from all modules) ---
doc_events = {
    # Core - global audit
    "*": {
        "after_insert": "healthcare_management.hms_core.api.audit.log_document_event",
        "on_update": "healthcare_management.hms_core.api.audit.log_document_event",
        "on_cancel": "healthcare_management.hms_core.api.audit.log_document_event",
    },
    # Clinical
    "Patient": {
        "after_insert": "healthcare_management.hms_clinical.doctype.patient.patient.after_insert",
    },
    "Encounter": {
        "on_update": "healthcare_management.hms_clinical.doctype.encounter.encounter.on_update",
    },
    "Appointment": {
        "after_insert": "healthcare_management.hms_clinical.doctype.appointment.appointment.send_confirmation",
    },
    # LIS
    "Lab Test": {
        "on_update": "healthcare_management.hms_lis.doctype.lab_test.lab_test.check_critical_value",
    },
    "Result Authorization": {
        "on_submit": "healthcare_management.hms_lis.doctype.result_authorization.result_authorization.release_to_portal",
    },
    # Pharmacy
    "Dispense Slip": {
        "before_save": "healthcare_management.hms_pharmacy.api.safety.run_all_safety_checks",
    },
    "Prescription Fulfillment": {
        "on_submit": "healthcare_management.hms_pharmacy.doctype.prescription_fulfillment.prescription_fulfillment.update_prescription_status",
    },
    # Revenue
    "Final Bill": {
        "on_submit": "healthcare_management.hms_revenue.doctype.final_bill.final_bill.post_to_ledger",
    },
    "Donation Receipt": {
        "after_insert": "healthcare_management.hms_revenue.doctype.donation_receipt.donation_receipt.send_donor_acknowledgment",
    },
    "Welfare Approval Decision": {
        "on_submit": "healthcare_management.hms_revenue.doctype.welfare_approval_decision.welfare_approval_decision.create_subsidy_ledger",
    },
}

# --- Scheduled Tasks (merged from all modules) ---
scheduler_events = {
    "hourly": [
        # Clinical
        "healthcare_management.hms_clinical.api.tasks.overdue_nursing_tasks_alert",
        # LIS
        "healthcare_management.hms_lis.api.tasks.tat_breach_alerts",
        "healthcare_management.hms_lis.api.tasks.pending_authorization_reminder",
    ],
    "daily": [
        # Core
        "healthcare_management.hms_core.api.maintenance.cleanup_expired_sessions",
        # Clinical
        "healthcare_management.hms_clinical.api.tasks.mark_no_show_appointments",
        "healthcare_management.hms_clinical.api.tasks.follow_up_reminders",
        # LIS
        "healthcare_management.hms_lis.api.tasks.qc_daily_review",
        # Pharmacy
        "healthcare_management.hms_pharmacy.api.tasks.expiry_alerts",
        "healthcare_management.hms_pharmacy.api.tasks.stockout_alerts",
        "healthcare_management.hms_pharmacy.api.tasks.controlled_drug_daily_report",
        # Revenue
        "healthcare_management.hms_revenue.api.tasks.outstanding_aging_update",
        "healthcare_management.hms_revenue.api.tasks.claim_follow_up_reminder",
    ],
    "weekly": [
        # Core
        "healthcare_management.hms_core.api.maintenance.audit_review_reminder",
        # Revenue
        "healthcare_management.hms_revenue.api.tasks.fund_utilization_report",
    ],
}

# --- Portal / Website ---
website_route_rules = [
    {"from_route": "/patient/<path:app_path>", "to_route": "patient"},
    {"from_route": "/lab-report-login", "to_route": "lab_report_login"},
    {"from_route": "/book-appointment", "to_route": "book_appointment"},
    {"from_route": "/find-doctor", "to_route": "find_doctor"},
    {"from_route": "/health-packages", "to_route": "health_packages"},
    {"from_route": "/donate", "to_route": "donate"},
    {"from_route": "/check-report-status", "to_route": "check_report_status"},
    {"from_route": "/corporate-panel", "to_route": "corporate_panel"},
    {"from_route": "/insurance-panel", "to_route": "insurance_panel"},
    {"from_route": "/donor-portal", "to_route": "donor_portal"},
]

portal_menu_items = [
    {"title": "My Appointments", "route": "/patient/appointments", "role": "Patient"},
    {"title": "My Lab Results", "route": "/patient/lab-results", "role": "Patient"},
    {"title": "My Prescriptions", "route": "/patient/prescriptions", "role": "Patient"},
    {"title": "My Invoices", "route": "/patient/invoices", "role": "Patient"},
    {"title": "My Profile", "route": "/patient/profile", "role": "Patient"},
]

has_website_permission = {
    "Lab Report": "healthcare_management.hms_portal.api.permissions.has_lab_report_permission",
}

# --- Jinja ---
jinja = {
    "methods": [
        "healthcare_management.hms_core.api.utils.get_branch_name",
        "healthcare_management.hms_core.api.utils.get_department_name",
    ],
}

override_whitelisted_methods = {}
