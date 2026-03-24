app_name = "hms_revenue"
app_title = "HMS Revenue"
app_publisher = "Healthcare Team"
app_description = "Revenue cycle - billing, packages, insurance/TPA, welfare approvals, donations"
app_email = "healthcare@example.com"
app_license = "MIT"
required_apps = ["frappe", "hms_core"]

doc_events = {
    "Final Bill": {
        "on_submit": "hms_revenue.hms_revenue.doctype.final_bill.final_bill.post_to_ledger",
    },
    "Donation Receipt": {
        "after_insert": "hms_revenue.hms_revenue.doctype.donation_receipt.donation_receipt.send_donor_acknowledgment",
    },
    "Welfare Approval Decision": {
        "on_submit": "hms_revenue.hms_revenue.doctype.welfare_approval_decision.welfare_approval_decision.create_subsidy_ledger",
    },
}

scheduler_events = {
    "daily": [
        "hms_revenue.hms_revenue.api.tasks.outstanding_aging_update",
        "hms_revenue.hms_revenue.api.tasks.claim_follow_up_reminder",
    ],
    "weekly": [
        "hms_revenue.hms_revenue.api.tasks.fund_utilization_report",
    ],
}
