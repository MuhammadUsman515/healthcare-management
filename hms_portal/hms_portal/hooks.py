app_name = "hms_portal"
app_title = "HMS Portal"
app_publisher = "Healthcare Team"
app_description = "External portals - patient, lab, donor, corporate, insurance"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe", "hms_core"]

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
    "Lab Report": "hms_portal.hms_portal.api.permissions.has_lab_report_permission",
}
