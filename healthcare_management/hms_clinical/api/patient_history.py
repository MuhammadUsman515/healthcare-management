import frappe


@frappe.whitelist()
def get_patient_history(patient):
    """Get complete medical history for a patient - single API."""
    return {
        "patient": frappe.get_doc("Patient", patient),
        "appointments": frappe.get_all("Appointment", filters={"patient": patient},
            fields=["name", "practitioner_name", "appointment_date", "appointment_time", "status", "appointment_type"],
            order_by="appointment_date desc", limit_page_length=50),
        "encounters": frappe.get_all("Encounter", filters={"patient": patient, "docstatus": 1},
            fields=["name", "practitioner_name", "encounter_date", "chief_complaints", "provisional_diagnosis", "final_diagnosis"],
            order_by="encounter_date desc", limit_page_length=50),
        "vital_signs": frappe.get_all("Vital Signs", filters={"patient": patient},
            fields=["name", "encounter_date", "temperature", "heart_rate", "bp_systolic", "bp_diastolic", "oxygen_saturation", "bmi", "abnormal_flags"],
            order_by="encounter_date desc", limit_page_length=20),
        "prescriptions": frappe.get_all("Prescription", filters={"patient": patient, "docstatus": 1},
            fields=["name", "prescription_date", "practitioner", "status"],
            order_by="prescription_date desc", limit_page_length=30),
        "lab_tests": frappe.get_all("Lab Test", filters={"patient": patient},
            fields=["name", "test_name", "test_date", "status", "result_status"],
            order_by="test_date desc", limit_page_length=30),
        "admissions": frappe.get_all("Inpatient Admission", filters={"patient": patient},
            fields=["name", "admission_date", "status", "ward", "primary_practitioner", "admission_reason", "length_of_stay"],
            order_by="admission_date desc", limit_page_length=10),
    }


@frappe.whitelist()
def get_dashboard_stats():
    """Healthcare dashboard statistics."""
    return {
        "total_patients": frappe.db.count("Patient", {"status": "Active"}),
        "total_practitioners": frappe.db.count("Practitioner", {"status": "Active"}),
        "todays_appointments": frappe.db.count("Appointment", {
            "appointment_date": frappe.utils.today(),
            "status": ["not in", ["Cancelled", "No Show"]],
        }),
        "active_admissions": frappe.db.count("Inpatient Admission", {"status": "Admitted"}),
        "pending_lab_tests": frappe.db.count("Lab Test", {
            "status": ["in", ["Ordered", "Sample Collected", "In Process"]],
        }),
        "pending_nursing_tasks": frappe.db.count("Nursing Task", {
            "status": ["in", ["Pending", "Overdue"]],
        }),
        "todays_revenue": frappe.db.sql("""
            SELECT COALESCE(SUM(amount), 0) FROM `tabCashier Receipt`
            WHERE DATE(creation) = CURDATE()
        """)[0][0] or 0,
    }
