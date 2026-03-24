app_name = "hms_pharmacy"
app_title = "HMS Pharmacy"
app_publisher = "Healthcare Team"
app_description = "Pharmacy module - inventory, formulary, dispensing, POS, batch/expiry, controlled stock"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe", "hms_core"]

doc_events = {
    "Dispense Slip": {
        "before_save": "hms_pharmacy.hms_pharmacy.api.safety.run_all_safety_checks",
    },
    "Prescription Fulfillment": {
        "on_submit": "hms_pharmacy.hms_pharmacy.doctype.prescription_fulfillment.prescription_fulfillment.update_prescription_status",
    },
}

scheduler_events = {
    "daily": [
        "hms_pharmacy.hms_pharmacy.api.tasks.expiry_alerts",
        "hms_pharmacy.hms_pharmacy.api.tasks.stockout_alerts",
        "hms_pharmacy.hms_pharmacy.api.tasks.controlled_drug_daily_report",
    ],
}
