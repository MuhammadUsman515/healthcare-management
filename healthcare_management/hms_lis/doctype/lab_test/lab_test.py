import frappe
from frappe import _
from frappe.model.document import Document


class LabTest(Document):
    def validate(self):
        self.calculate_tat()

    def calculate_tat(self):
        if self.order_date and self.authorized_datetime:
            delta = self.authorized_datetime - self.order_date
            self.tat_minutes = int(delta.total_seconds() / 60)

    def before_submit(self):
        if self.status not in ("Authorized", "Released"):
            frappe.throw(_("Lab Test must be Authorized before submission."))

    @frappe.whitelist()
    def enter_result(self, value, unit=None, normal_range=None, result_status=None, comment=None):
        """Stage 1: Result Entry by Lab Tech."""
        self.result_value = value
        if unit:
            self.result_unit = unit
        if normal_range:
            self.normal_range = normal_range
        if result_status:
            self.result_status = result_status
        if comment:
            self.result_comment = comment
        self.result_entered_by = frappe.session.user
        self.result_entered_datetime = frappe.utils.now_datetime()
        self.status = "Result Entered"
        self.save()

    @frappe.whitelist()
    def verify_result(self):
        """Stage 2: Verification by senior tech."""
        if self.status != "Result Entered":
            frappe.throw(_("Can only verify results that are entered."))
        if self.result_entered_by == frappe.session.user:
            frappe.throw(_("Result cannot be verified by the same person who entered it."))
        self.verified_by = frappe.session.user
        self.verified_datetime = frappe.utils.now_datetime()
        self.status = "Verified"
        self.save()

    @frappe.whitelist()
    def authorize_result(self):
        """Stage 3: Authorization by pathologist/supervisor."""
        if self.status != "Verified":
            frappe.throw(_("Can only authorize verified results."))
        frappe.only_for("Lab Supervisor")
        self.authorized_by = frappe.session.user
        self.authorized_datetime = frappe.utils.now_datetime()
        self.status = "Authorized"
        self.save()

        if self.result_status == "Critical":
            self.create_critical_alert()

    def create_critical_alert(self):
        frappe.get_doc({
            "doctype": "Critical Value Alert",
            "title": f"CRITICAL: {self.test_name} - {self.patient_name}",
            "patient": self.patient,
            "lab_test": self.name,
            "description": f"Critical value: {self.result_value} {self.result_unit or ''}. Normal: {self.normal_range or 'N/A'}",
            "status": "Active",
        }).insert(ignore_permissions=True)
        if self.ordering_practitioner:
            frappe.publish_realtime(
                "critical_lab_alert",
                {"test": self.name, "patient": self.patient_name, "value": self.result_value},
                user=frappe.db.get_value("Practitioner", self.ordering_practitioner, "user"),
            )


def check_critical_value(doc, method=None):
    if doc.result_status == "Critical" and doc.status in ("Result Entered", "Verified", "Authorized"):
        frappe.msgprint(
            _("CRITICAL: {0} result for {1} = {2}").format(doc.test_name, doc.patient_name, doc.result_value),
            title=_("Critical Value"),
            indicator="red",
        )
