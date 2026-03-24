import frappe
from frappe import _


@frappe.whitelist()
def get_patient_for_user():
    """Get patient record linked to current user."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        frappe.throw(_("No patient record linked to your account."))
    return frappe.get_doc("Patient", patient)


@frappe.whitelist()
def get_my_appointments(status=None):
    """Get appointments for current patient."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        return []
    filters = {"patient": patient}
    if status:
        filters["status"] = status
    return frappe.get_all("Appointment",
        filters=filters,
        fields=["name", "practitioner_name", "appointment_date", "appointment_time", "status", "department"],
        order_by="appointment_date desc",
        limit_page_length=20,
    )


@frappe.whitelist()
def get_my_lab_results():
    """Get released lab results for current patient."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        return []
    return frappe.get_all("Lab Test",
        filters={"patient": patient, "status": "Released"},
        fields=["name", "test_name", "test_group", "result_value", "result_unit", "normal_range", "result_status", "authorized_datetime"],
        order_by="authorized_datetime desc",
        limit_page_length=50,
    )


@frappe.whitelist()
def get_my_prescriptions():
    """Get prescriptions for current patient."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        return []
    return frappe.get_all("Prescription",
        filters={"patient": patient, "docstatus": 1},
        fields=["name", "prescription_date", "practitioner", "status"],
        order_by="prescription_date desc",
    )


@frappe.whitelist()
def get_my_invoices():
    """Get bills for current patient."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        return []
    return frappe.get_all("Final Bill",
        filters={"patient": patient},
        fields=["name", "bill_date", "total_charges", "patient_payable", "amount_paid", "balance_due", "status"],
        order_by="bill_date desc",
    )


@frappe.whitelist()
def book_appointment(department=None, practitioner=None, appointment_date=None, appointment_time=None, reason=None):
    """Book appointment from portal."""
    patient = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient:
        frappe.throw(_("No patient record found."))

    apt = frappe.get_doc({
        "doctype": "Appointment",
        "patient": patient,
        "practitioner": practitioner,
        "department": department,
        "appointment_date": appointment_date,
        "appointment_time": appointment_time,
        "reason": reason,
        "appointment_type": "New Consultation",
    })
    apt.insert(ignore_permissions=True)
    return apt.name


@frappe.whitelist(allow_guest=True)
def verify_lab_report(report_no, mobile, dob):
    """Public lab report verification with OTP-less basic auth."""
    patient = frappe.db.get_value("Patient", {"mobile": mobile, "dob": dob}, "name")
    if not patient:
        frappe.throw(_("Verification failed. Please check your details."))

    test = frappe.db.get_value("Lab Test", {
        "name": report_no,
        "patient": patient,
        "status": "Released",
    }, ["name", "test_name", "result_value", "result_unit", "normal_range", "result_status", "authorized_datetime"], as_dict=True)

    if not test:
        frappe.throw(_("Report not found or not yet released."))

    frappe.get_doc({
        "doctype": "Result View Audit",
        "title": f"Public view: {report_no}",
        "patient": patient,
        "lab_test": report_no,
        "description": f"Accessed via public portal by mobile: {mobile}",
    }).insert(ignore_permissions=True)

    return test


def has_lab_report_permission(doc, ptype, user):
    """Check if user has permission to view lab report."""
    patient = frappe.db.get_value("Patient", {"user": user}, "name")
    if not patient:
        return False
    return doc.patient == patient and doc.status == "Released"
