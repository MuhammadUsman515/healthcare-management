from frappe.model.document import Document


class Ward(Document):
    def autoname(self):
        self.name = self.ward_name
