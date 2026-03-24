from frappe.model.document import Document


class CoveragePlan(Document):
    def autoname(self):
        self.name = self.plan_name
