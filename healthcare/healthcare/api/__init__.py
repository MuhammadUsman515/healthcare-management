import frappe
from frappe import _


@frappe.whitelist()
def get_patient_history(patient):
    """Get complete medical history for a patient."""
    appointments = frappe.get_all(
        "Appointment",
        filters={"patient": patient},
        fields=["name", "practitioner_name", "appointment_date", "status", "reason"],
        order_by="appointment_date desc",
        limit_page_length=20,
    )

    vital_signs = frappe.get_all(
        "Vital Signs",
        filters={"patient": patient},
        fields=[
            "name", "encounter_date", "temperature", "heart_rate",
            "bp_systolic", "bp_diastolic", "oxygen_saturation", "bmi",
        ],
        order_by="encounter_date desc",
        limit_page_length=20,
    )

    lab_tests = frappe.get_all(
        "Lab Test",
        filters={"patient": patient},
        fields=["name", "test_name", "test_date", "status", "result_value", "result_status"],
        order_by="test_date desc",
        limit_page_length=20,
    )

    prescriptions = frappe.get_all(
        "Prescription",
        filters={"patient": patient},
        fields=["name", "drug_name", "dosage", "frequency", "prescription_date"],
        order_by="prescription_date desc",
        limit_page_length=20,
    )

    procedures = frappe.get_all(
        "Clinical Procedure",
        filters={"patient": patient},
        fields=["name", "procedure_name", "procedure_date", "status", "outcome"],
        order_by="procedure_date desc",
        limit_page_length=20,
    )

    return {
        "appointments": appointments,
        "vital_signs": vital_signs,
        "lab_tests": lab_tests,
        "prescriptions": prescriptions,
        "procedures": procedures,
    }


@frappe.whitelist()
def get_dashboard_stats():
    """Get healthcare dashboard statistics."""
    return {
        "total_patients": frappe.db.count("Patient", {"status": "Active"}),
        "total_practitioners": frappe.db.count("Practitioner", {"status": "Active"}),
        "todays_appointments": frappe.db.count(
            "Appointment",
            {"appointment_date": frappe.utils.today(), "status": ["!=", "Cancelled"]},
        ),
        "pending_lab_tests": frappe.db.count(
            "Lab Test", {"status": ["in", ["Ordered", "Sample Collected", "In Progress"]]}
        ),
        "active_prescriptions": frappe.db.count("Prescription", {"docstatus": 1}),
    }
