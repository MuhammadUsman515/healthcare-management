import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class CheckIn(Document):
    def validate(self):
        if not self.check_in_time:
            self.check_in_time = now_datetime()

    def after_insert(self):
        if self.appointment:
            apt = frappe.get_doc("Appointment", self.appointment)
            if apt.status == "Scheduled":
                apt.check_in()
