from frappe.model.document import Document


class Practitioner(Document):
    def before_save(self):
        self.set_full_name()

    def set_full_name(self):
        name_parts = [self.first_name, self.last_name]
        self.full_name = " ".join(filter(None, name_parts))
