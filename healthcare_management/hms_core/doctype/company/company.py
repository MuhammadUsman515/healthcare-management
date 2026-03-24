from frappe.model.document import Document


class Company(Document):
    def autoname(self):
        self.name = self.company_name
