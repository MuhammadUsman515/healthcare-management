import frappe
from frappe import _
from frappe.model.document import Document


class ResultAuthorization(Document):
    def on_submit(self):
        frappe.db.set_value("Lab Test", self.lab_test, {
            "status": "Released" if self.release_to_portal else "Authorized",
            "authorized_by": self.authorized_by,
            "authorized_datetime": self.authorization_datetime,
        })

        if self.release_to_portal:
            self.notify_patient()

    def notify_patient(self):
        patient_mobile = frappe.db.get_value("Patient", self.patient, "mobile")
        if patient_mobile:
            pass  # SMS/WhatsApp: "Your lab report is ready"


def release_to_portal(doc, method=None):
    if doc.release_to_portal:
        frappe.db.set_value("Lab Test", doc.lab_test, "status", "Released")
