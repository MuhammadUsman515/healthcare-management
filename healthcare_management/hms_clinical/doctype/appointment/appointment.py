import frappe
from frappe import _
from frappe.model.document import Document


class Appointment(Document):
    def validate(self):
        self.validate_appointment_date()
        self.check_duplicate()
        self.assign_token()

    def validate_appointment_date(self):
        import datetime
        if self.appointment_date and self.appointment_date < datetime.date.today():
            if self.is_new():
                frappe.throw(_("Appointment date cannot be in the past."))

    def check_duplicate(self):
        if not self.is_new():
            return
        existing = frappe.db.exists("Appointment", {
            "patient": self.patient,
            "practitioner": self.practitioner,
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time,
            "status": ["not in", ["Cancelled", "No Show", "Rescheduled"]],
        })
        if existing:
            frappe.throw(
                _("Duplicate appointment exists: {0}").format(existing)
            )

    def assign_token(self):
        if self.token_number:
            return
        existing_count = frappe.db.count("Appointment", {
            "practitioner": self.practitioner,
            "appointment_date": self.appointment_date,
            "status": ["not in", ["Cancelled", "No Show", "Rescheduled"]],
        })
        self.token_number = existing_count + 1

    def on_update(self):
        if self.status == "Cancelled" and self.has_value_changed("status"):
            frappe.msgprint(
                _("Appointment {0} cancelled.").format(self.name),
                alert=True,
            )

    @frappe.whitelist()
    def check_in(self):
        if self.status != "Scheduled":
            frappe.throw(_("Only scheduled appointments can be checked in."))
        self.status = "Checked In"
        self.save()
        token = self.create_queue_token()
        frappe.msgprint(_("Patient checked in. Token: {0}").format(token.token_number))

    def create_queue_token(self):
        existing = frappe.db.exists("Queue Token", {
            "appointment": self.name,
            "status": ["!=", "Cancelled"]
        })
        if existing:
            return frappe.get_doc("Queue Token", existing)

        token = frappe.get_doc({
            "doctype": "Queue Token",
            "appointment": self.name,
            "patient": self.patient,
            "practitioner": self.practitioner,
            "department": self.department,
            "token_number": self.token_number,
            "date": self.appointment_date,
            "status": "Active",
        })
        token.insert(ignore_permissions=True)
        return token

    @frappe.whitelist()
    def reschedule(self, new_date, new_time):
        old_date = self.appointment_date
        old_time = self.appointment_time
        self.status = "Rescheduled"
        self.save()

        new_apt = frappe.copy_doc(self)
        new_apt.appointment_date = new_date
        new_apt.appointment_time = new_time
        new_apt.status = "Scheduled"
        new_apt.token_number = 0
        new_apt.insert()

        frappe.get_doc({
            "doctype": "Appointment Reschedule Log",
            "original_appointment": self.name,
            "new_appointment": new_apt.name,
            "old_date": old_date,
            "old_time": old_time,
            "new_date": new_date,
            "new_time": new_time,
            "rescheduled_by": frappe.session.user,
        }).insert(ignore_permissions=True)

        return new_apt.name


def send_confirmation(doc, method=None):
    if doc.patient and doc.status == "Scheduled":
        patient_mobile = frappe.db.get_value("Patient", doc.patient, "mobile")
        if patient_mobile:
            pass  # SMS/WhatsApp integration point


def on_appointment_update(doc, method=None):
    if doc.status == "Checked In" and doc.has_value_changed("status"):
        doc.create_queue_token()
