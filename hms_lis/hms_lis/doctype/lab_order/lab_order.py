import frappe
from frappe import _
from frappe.model.document import Document


class LabOrder(Document):
    def validate(self):
        if not self.items:
            frappe.throw(_("At least one lab test must be ordered."))

    def on_submit(self):
        self.db_set("status", "Sample Pending")
        for item in self.items:
            frappe.get_doc({
                "doctype": "Lab Test",
                "lab_order": self.name,
                "patient": self.patient,
                "test_template": item.test_template,
                "test_name": item.test_name,
                "test_group": item.test_group,
                "ordering_practitioner": self.ordering_practitioner,
                "order_date": self.order_date,
                "priority": self.priority,
                "status": "Ordered",
            }).insert(ignore_permissions=True)

    def on_cancel(self):
        self.db_set("status", "Cancelled")
        frappe.db.sql("""
            UPDATE `tabLab Test` SET status = 'Cancelled'
            WHERE lab_order = %s AND status NOT IN ('Authorized', 'Released')
        """, self.name)
        frappe.db.commit()
