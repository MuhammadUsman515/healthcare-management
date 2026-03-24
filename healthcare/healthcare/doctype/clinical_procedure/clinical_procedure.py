import frappe
from frappe import _
from frappe.model.document import Document


class ClinicalProcedure(Document):
    def validate(self):
        self.validate_procedure_date()

    def validate_procedure_date(self):
        if self.status == "Completed" and not self.outcome:
            frappe.msgprint(
                _("Please record the outcome for the completed procedure."),
                indicator="orange",
            )

    def before_submit(self):
        if self.status not in ("Completed", "Cancelled"):
            frappe.throw(
                _("Procedure must be Completed or Cancelled before submission.")
            )
