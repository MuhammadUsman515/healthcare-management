from frappe.model.document import Document


class Department(Document):
    def autoname(self):
        self.name = f"{self.department_name} - {self.company}" if self.company else self.department_name
