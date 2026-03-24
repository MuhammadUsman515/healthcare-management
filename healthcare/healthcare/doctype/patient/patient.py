import frappe
from frappe.model.document import Document


class Patient(Document):
    def before_save(self):
        self.set_full_name()

    def set_full_name(self):
        name_parts = [self.first_name, self.last_name]
        self.full_name = " ".join(filter(None, name_parts))

    def get_patient_age(self):
        if not self.dob:
            return None
        import datetime

        today = datetime.date.today()
        born = self.dob
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def after_insert(doc, method=None):
    frappe.msgprint(f"Patient {doc.full_name} registered successfully.", alert=True)
