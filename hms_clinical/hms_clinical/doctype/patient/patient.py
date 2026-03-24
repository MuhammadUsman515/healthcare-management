import frappe
from frappe import _
from frappe.model.document import Document


class Patient(Document):
    def before_save(self):
        self.set_full_name()
        self.set_age_display()
        self.set_mrn()

    def set_full_name(self):
        parts = [self.first_name, self.middle_name, self.last_name]
        self.full_name = " ".join(filter(None, parts))

    def set_age_display(self):
        if not self.dob:
            self.age_display = ""
            return
        import datetime
        today = datetime.date.today()
        born = self.dob
        years = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        months = (today.month - born.month) % 12
        if today.day < born.day:
            months = (months - 1) % 12
        self.age_display = f"{years}Y {months}M"

    def set_mrn(self):
        if not self.mrn:
            self.mrn = self.name

    def validate(self):
        self.validate_duplicate()
        self.validate_flags()

    def validate_duplicate(self):
        """Score-based duplicate detection."""
        if not self.is_new():
            return

        if self.cnic:
            existing = frappe.db.exists("Patient", {"cnic": self.cnic, "status": ["!=", "Merged"]})
            if existing:
                frappe.throw(
                    _("A patient with CNIC {0} already exists: {1}").format(self.cnic, existing)
                )

        if self.mobile:
            duplicates = frappe.get_all(
                "Patient",
                filters={
                    "mobile": self.mobile,
                    "first_name": self.first_name,
                    "status": ["!=", "Merged"],
                },
                pluck="name",
            )
            if duplicates:
                frappe.msgprint(
                    _("Possible duplicate patient(s) found: {0}").format(", ".join(duplicates)),
                    title=_("Duplicate Warning"),
                    indicator="orange",
                )

    def validate_flags(self):
        if self.is_infection_risk and not self.flag_notes:
            frappe.msgprint(
                _("Please add flag notes for infection risk patients."),
                indicator="orange",
            )

    def get_age(self):
        if not self.dob:
            return None
        import datetime
        today = datetime.date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))

    @frappe.whitelist()
    def merge_patient(self, target_patient):
        """Merge this patient into target patient."""
        if self.name == target_patient:
            frappe.throw(_("Cannot merge patient with itself."))

        frappe.only_for("Healthcare Administrator")

        # Update all linked records
        linked_doctypes = [
            "Appointment", "Encounter", "Vital Signs", "Lab Order",
            "Lab Test", "Prescription", "Inpatient Admission",
        ]
        for dt in linked_doctypes:
            frappe.db.sql(
                f"UPDATE `tab{dt}` SET patient = %s WHERE patient = %s",
                (target_patient, self.name),
            )

        self.db_set("status", "Merged")
        frappe.db.commit()
        frappe.msgprint(_("Patient merged into {0}").format(target_patient))


def after_insert(doc, method=None):
    frappe.msgprint(
        _("Patient {0} registered successfully. MRN: {1}").format(doc.full_name, doc.mrn),
        alert=True,
    )
