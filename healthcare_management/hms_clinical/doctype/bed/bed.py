from frappe.model.document import Document


class Bed(Document):
    def autoname(self):
        self.name = self.bed_name
