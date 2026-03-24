import frappe
from frappe import _
from frappe.model.document import Document


class Practitioner(Document):
    def before_save(self):
        self.set_full_name()

    def set_full_name(self):
        parts = [self.first_name, self.last_name]
        self.full_name = " ".join(filter(None, parts))

    def validate(self):
        self.check_license_expiry()

    def check_license_expiry(self):
        if self.license_expiry:
            import datetime
            if self.license_expiry < datetime.date.today():
                frappe.msgprint(
                    _("Medical license for {0} has expired on {1}.").format(
                        self.full_name, self.license_expiry
                    ),
                    title=_("License Expired"),
                    indicator="red",
                )

    @frappe.whitelist()
    def get_today_appointments(self):
        return frappe.get_all(
            "Appointment",
            filters={
                "practitioner": self.name,
                "appointment_date": frappe.utils.today(),
                "status": ["not in", ["Cancelled", "No Show"]],
            },
            fields=["name", "patient_name", "appointment_time", "status", "token_number"],
            order_by="appointment_time",
        )
