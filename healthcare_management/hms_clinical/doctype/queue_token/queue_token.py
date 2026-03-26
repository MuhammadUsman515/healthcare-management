import frappe
from frappe.model.document import Document


class QueueToken(Document):
    def validate(self):
        if not self.token_number:
            self.assign_token_number()

    def assign_token_number(self):
        existing_count = frappe.db.count("Queue Token", {
            "practitioner": self.practitioner,
            "date": self.date,
            "status": ["!=", "Cancelled"],
        })
        self.token_number = existing_count + 1

    def complete(self):
        self.status = "Completed"
        self.save()
