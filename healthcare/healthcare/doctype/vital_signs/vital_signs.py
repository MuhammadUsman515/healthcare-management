import frappe
from frappe import _
from frappe.model.document import Document


class VitalSigns(Document):
    def validate(self):
        self.calculate_bmi()
        self.validate_vital_ranges()

    def calculate_bmi(self):
        if self.height and self.weight:
            height_m = self.height / 100
            self.bmi = round(self.weight / (height_m ** 2), 2)

    def validate_vital_ranges(self):
        warnings = []
        if self.temperature and (self.temperature < 95 or self.temperature > 104):
            warnings.append(_("Temperature {0}°F is outside normal range (95-104°F)").format(self.temperature))
        if self.heart_rate and (self.heart_rate < 40 or self.heart_rate > 200):
            warnings.append(_("Heart rate {0} bpm is outside normal range (40-200 bpm)").format(self.heart_rate))
        if self.oxygen_saturation and self.oxygen_saturation < 90:
            warnings.append(_("Oxygen saturation {0}% is critically low").format(self.oxygen_saturation))

        for warning in warnings:
            frappe.msgprint(warning, title=_("Vital Signs Warning"), indicator="orange")
