import frappe
from frappe import _
from frappe.model.document import Document
import math


class VitalSigns(Document):
    def validate(self):
        self.calculate_bmi()
        self.calculate_bsa()
        self.check_abnormal_ranges()

    def calculate_bmi(self):
        if self.height and self.weight and self.height > 0:
            height_m = self.height / 100
            self.bmi = round(self.weight / (height_m ** 2), 2)

    def calculate_bsa(self):
        """Mosteller formula for Body Surface Area."""
        if self.height and self.weight and self.height > 0 and self.weight > 0:
            self.bsa = round(math.sqrt((self.height * self.weight) / 3600), 2)

    def check_abnormal_ranges(self):
        flags = []
        if self.temperature:
            if self.temperature < 95:
                flags.append("Hypothermia")
            elif self.temperature > 100.4:
                flags.append("Fever")
            if self.temperature > 104:
                flags.append("CRITICAL: High Fever")

        if self.heart_rate:
            if self.heart_rate < 60:
                flags.append("Bradycardia")
            elif self.heart_rate > 100:
                flags.append("Tachycardia")
            if self.heart_rate > 150:
                flags.append("CRITICAL: Severe Tachycardia")

        if self.bp_systolic:
            if self.bp_systolic > 180:
                flags.append("CRITICAL: Hypertensive Crisis")
            elif self.bp_systolic > 140:
                flags.append("Hypertension")
            elif self.bp_systolic < 90:
                flags.append("Hypotension")

        if self.oxygen_saturation:
            if self.oxygen_saturation < 90:
                flags.append("CRITICAL: Severe Hypoxia")
            elif self.oxygen_saturation < 94:
                flags.append("Low SpO2")

        if self.respiratory_rate:
            if self.respiratory_rate > 20:
                flags.append("Tachypnea")
            elif self.respiratory_rate < 12:
                flags.append("Bradypnea")

        if self.pain_score and self.pain_score >= 7:
            flags.append("Severe Pain")

        self.abnormal_flags = ", ".join(flags) if flags else ""

        critical_flags = [f for f in flags if f.startswith("CRITICAL")]
        for flag in critical_flags:
            frappe.msgprint(
                _(flag),
                title=_("Critical Vital Sign Alert"),
                indicator="red",
            )
