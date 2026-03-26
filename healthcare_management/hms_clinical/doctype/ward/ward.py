import frappe
from frappe import _
from frappe.model.document import Document


class Ward(Document):
    def autoname(self):
        self.name = self.ward_name

    def validate(self):
        self.update_bed_count()

    def update_bed_count(self):
        self.total_beds = frappe.db.count("Bed", {"ward": self.name})
