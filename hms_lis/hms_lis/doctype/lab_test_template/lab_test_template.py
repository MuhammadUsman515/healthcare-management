from frappe.model.document import Document


class LabTestTemplate(Document):
    def autoname(self):
        self.name = self.test_name
