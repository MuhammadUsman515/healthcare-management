import frappe
from frappe import _
from frappe.model.document import Document


class Bed(Document):
    def autoname(self):
        self.name = self.bed_name

    def validate(self):
        if not self.status:
            self.status = "Available"

    @frappe.whitelist()
    def mark_maintenance(self):
        self.status = "Under Maintenance"
        self.save()

    @frappe.whitelist()
    def mark_available(self):
        self.status = "Available"
        self.save()
