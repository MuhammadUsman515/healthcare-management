import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class Visit(Document):
    def validate(self):
        if not self.visit_date:
            self.visit_date = now_datetime()

    def on_update(self):
        if self.status == "Completed" and self.has_value_changed("status"):
            if self.appointment:
                frappe.db.set_value("Appointment", self.appointment, "status", "Completed")
