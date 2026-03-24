import frappe
from frappe.utils import today, add_days, now_datetime


def mark_no_show_appointments():
    """Mark past appointments as No Show if still Scheduled."""
    frappe.db.sql("""
        UPDATE `tabAppointment`
        SET status = 'No Show'
        WHERE appointment_date < %s
        AND status = 'Scheduled'
    """, today())
    frappe.db.commit()


def follow_up_reminders():
    """Send follow-up reminders for encounters due tomorrow."""
    tomorrow = add_days(today(), 1)
    encounters = frappe.get_all(
        "Encounter",
        filters={"follow_up_date": tomorrow, "docstatus": 1},
        fields=["patient", "patient_name", "practitioner_name", "follow_up_date"],
    )
    for enc in encounters:
        patient_mobile = frappe.db.get_value("Patient", enc.patient, "mobile")
        if patient_mobile:
            pass  # SMS integration point


def overdue_nursing_tasks_alert():
    """Alert nurse station about overdue tasks."""
    overdue = frappe.db.count("Nursing Task", {
        "status": "Pending",
        "scheduled_datetime": ["<", now_datetime()],
    })
    if overdue > 0:
        frappe.db.sql("""
            UPDATE `tabNursing Task`
            SET status = 'Overdue'
            WHERE status = 'Pending'
            AND scheduled_datetime < %s
        """, now_datetime())
        frappe.db.commit()
