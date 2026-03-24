import frappe
from frappe import _
from frappe.model.document import Document


class LabTest(Document):
    def validate(self):
        self.set_result_status_indicator()

    def set_result_status_indicator(self):
        if self.result_value and self.result_status == "Critical":
            frappe.msgprint(
                _("CRITICAL: Lab test result for {0} requires immediate attention.").format(
                    self.patient_name
                ),
                title=_("Critical Result"),
                indicator="red",
            )

    def before_submit(self):
        if self.status != "Completed":
            frappe.throw(_("Lab Test must be marked as Completed before submission."))
