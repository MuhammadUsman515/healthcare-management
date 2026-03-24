import frappe
from frappe import _
from frappe.model.document import Document


class NursingTask(Document):
    def validate(self):
        if self.status == "Completed" and not self.completed_datetime:
            self.completed_datetime = frappe.utils.now_datetime()

    @frappe.whitelist()
    def mark_complete(self, notes=None):
        self.status = "Completed"
        self.completed_datetime = frappe.utils.now_datetime()
        if notes:
            self.completion_notes = notes
        self.save()
