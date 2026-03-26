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


@frappe.whitelist()
def update_patient_profile(mobile=None, email=None, address=None,
                           emergency_contact_name=None, emergency_contact_phone=None):
    """Update patient profile from portal."""
    patient_name = frappe.db.get_value("Patient", {"user": frappe.session.user}, "name")
    if not patient_name:
        frappe.throw(_("No patient record found."))

    patient = frappe.get_doc("Patient", patient_name)
    if mobile:
        patient.mobile = mobile
    if email:
        patient.email = email
    if address is not None:
        patient.address = address
    if emergency_contact_name is not None:
        patient.emergency_contact_name = emergency_contact_name
    if emergency_contact_phone is not None:
        patient.emergency_contact_phone = emergency_contact_phone
    patient.save(ignore_permissions=True)
    return "ok"


@frappe.whitelist(allow_guest=True)
def get_lab_report(report_number, patient_identifier):
    """Public lab report access by report number and mobile/CNIC."""
    if not report_number or not patient_identifier:
        return {"success": False, "error": "Please provide both report number and identifier."}

    patient = frappe.db.get_value(
        "Patient",
        {"mobile": patient_identifier},
        "name",
    )
    if not patient:
        patient = frappe.db.get_value(
            "Patient",
            {"cnic": patient_identifier},
            "name",
        )
    if not patient:
        return {"success": False, "error": "Patient not found. Please check your mobile/CNIC."}

    test = frappe.db.get_value(
        "Lab Test",
        {"name": report_number, "patient": patient, "status": "Released"},
        ["name", "test_name", "patient_name", "result_value", "result_unit",
         "normal_range", "result_status", "order_date"],
        as_dict=True,
    )
    if not test:
        return {"success": False, "error": "Report not found or not yet released."}

    return {"success": True, "report": test}


@frappe.whitelist(allow_guest=True)
def check_report_status(order_number, mobile):
    """Check status of lab tests by order/report number and mobile."""
    if not order_number or not mobile:
        return {"success": False}

    patient = frappe.db.get_value("Patient", {"mobile": mobile}, "name")
    if not patient:
        return {"success": False}

    tests = frappe.get_all(
        "Lab Test",
        filters={"patient": patient, "name": ["like", f"%{order_number}%"]},
        fields=["name", "test_name", "status", "order_date"],
        limit_page_length=20,
    )
    if not tests:
        tests = frappe.get_all(
            "Lab Test",
            filters={"patient": patient, "lab_order": order_number},
            fields=["name", "test_name", "status", "order_date"],
            limit_page_length=20,
        )

    if not tests:
        return {"success": False}

    return {"success": True, "tests": tests}


def has_lab_report_permission(doc, ptype, user):
    """Check if user has permission to view lab report."""
    patient = frappe.db.get_value("Patient", {"user": user}, "name")
    if not patient:
        return False
    return doc.patient == patient and doc.status == "Released"
