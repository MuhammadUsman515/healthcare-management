import frappe
from frappe import _
from frappe.model.document import Document


class Appointment(Document):
    def validate(self):
        self.validate_appointment_date()
        self.check_duplicate_appointment()

    def validate_appointment_date(self):
        import datetime

        if self.appointment_date and self.appointment_date < datetime.date.today():
            frappe.throw(_("Appointment date cannot be in the past."))

    def check_duplicate_appointment(self):
        if not self.is_new():
            return

        existing = frappe.db.exists(
            "Appointment",
            {
                "patient": self.patient,
                "practitioner": self.practitioner,
                "appointment_date": self.appointment_date,
                "appointment_time": self.appointment_time,
                "status": ["not in", ["Cancelled", "No Show"]],
            },
        )
        if existing:
            frappe.throw(
                _("An appointment already exists for this patient with {0} on {1} at {2}.").format(
                    self.practitioner_name, self.appointment_date, self.appointment_time
                )
            )

    def on_update(self):
        if self.status == "Cancelled":
            frappe.msgprint(
                _("Appointment {0} has been cancelled.").format(self.name), alert=True
            )
