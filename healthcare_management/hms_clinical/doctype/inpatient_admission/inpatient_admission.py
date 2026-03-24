import frappe
from frappe import _
from frappe.model.document import Document


class InpatientAdmission(Document):
    def validate(self):
        self.calculate_los()

    def on_submit(self):
        if self.bed:
            frappe.db.set_value("Bed", self.bed, "status", "Occupied")
            frappe.get_doc({
                "doctype": "Bed Occupancy",
                "bed": self.bed,
                "patient": self.patient,
                "admission": self.name,
                "from_datetime": self.admission_date,
                "is_active": 1,
            }).insert(ignore_permissions=True)

    def on_cancel(self):
        if self.bed:
            frappe.db.set_value("Bed", self.bed, "status", "Available")

    def calculate_los(self):
        if self.admission_date and self.actual_discharge:
            delta = self.actual_discharge - self.admission_date
            self.length_of_stay = max(delta.days, 1)

    @frappe.whitelist()
    def initiate_discharge(self):
        if self.status not in ("Admitted", "Transferred"):
            frappe.throw(_("Can only discharge admitted patients."))
        self.db_set("status", "Discharge Initiated")
        frappe.msgprint(_("Discharge initiated. Pending billing clearance."))

    @frappe.whitelist()
    def complete_discharge(self):
        if self.status != "Billing Clearance":
            frappe.throw(_("Billing clearance required before discharge."))
        self.db_set("status", "Discharged")
        self.db_set("actual_discharge", frappe.utils.now_datetime())
        if self.bed:
            frappe.db.set_value("Bed", self.bed, "status", "Available")
            frappe.db.set_value(
                "Bed Occupancy",
                {"admission": self.name, "is_active": 1},
                {"is_active": 0, "to_datetime": frappe.utils.now_datetime()},
            )
        frappe.msgprint(_("Patient discharged successfully."))

    @frappe.whitelist()
    def transfer_bed(self, new_ward, new_bed):
        old_bed = self.bed
        if old_bed:
            frappe.db.set_value("Bed", old_bed, "status", "Available")
            frappe.db.set_value(
                "Bed Occupancy",
                {"admission": self.name, "is_active": 1},
                {"is_active": 0, "to_datetime": frappe.utils.now_datetime()},
            )
        self.db_set("ward", new_ward)
        self.db_set("bed", new_bed)
        self.db_set("status", "Transferred")
        frappe.db.set_value("Bed", new_bed, "status", "Occupied")
        frappe.get_doc({
            "doctype": "Bed Occupancy",
            "bed": new_bed,
            "patient": self.patient,
            "admission": self.name,
            "from_datetime": frappe.utils.now_datetime(),
            "is_active": 1,
        }).insert(ignore_permissions=True)
