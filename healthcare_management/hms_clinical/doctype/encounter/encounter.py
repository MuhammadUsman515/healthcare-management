import frappe
from frappe import _
from frappe.model.document import Document


class Encounter(Document):
    def validate(self):
        self.update_appointment_status()

    def update_appointment_status(self):
        if self.appointment:
            frappe.db.set_value("Appointment", self.appointment, "status", "In Consultation")

    def on_submit(self):
        """Lock encounter after signing."""
        if self.appointment:
            frappe.db.set_value("Appointment", self.appointment, "status", "Completed")

        if self.admit_patient:
            self.create_admission_request()

    def on_cancel(self):
        if self.appointment:
            frappe.db.set_value("Appointment", self.appointment, "status", "Checked In")

    def create_admission_request(self):
        if frappe.db.exists("Admission Request", {"encounter": self.name, "docstatus": ["!=", 2]}):
            return
        frappe.get_doc({
            "doctype": "Admission Request",
            "patient": self.patient,
            "practitioner": self.practitioner,
            "encounter": self.name,
            "department": self.department,
            "reason": self.provisional_diagnosis or self.chief_complaints,
        }).insert(ignore_permissions=True)
        frappe.msgprint(_("Admission Request created."), alert=True)

    @frappe.whitelist()
    def add_addendum(self, text):
        """Add addendum to signed encounter without editing original."""
        if self.docstatus != 1:
            frappe.throw(_("Addendum can only be added to submitted encounters."))
        self.db_set("addendum", (self.addendum or "") + f"\n\n--- Addendum ({frappe.utils.now()}) ---\n{text}")
        self.db_set("addendum_date", frappe.utils.now())
        frappe.msgprint(_("Addendum added successfully."))


def on_update(doc, method=None):
    pass
