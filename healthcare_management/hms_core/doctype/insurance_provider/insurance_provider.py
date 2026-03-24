import frappe
from frappe import _
from frappe.model.document import Document


class InsuranceProvider(Document):
    def autoname(self):
        self.name = self.provider_name

    def validate(self):
        if self.contract_end and self.contract_start:
            if self.contract_end < self.contract_start:
                frappe.throw(_("Contract end date cannot be before start date."))
