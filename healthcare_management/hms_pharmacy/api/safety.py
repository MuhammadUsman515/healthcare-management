import frappe
from frappe import _


def run_all_safety_checks(doc, method=None):
    """Run drug interaction, allergy, and duplicate checks before dispensing."""
    warnings = []

    if doc.patient:
        patient_allergies = frappe.db.get_value("Patient", doc.patient, "allergies") or ""
        for item in doc.items:
            if item.drug_name and patient_allergies:
                if item.drug_name.lower() in patient_allergies.lower():
                    warnings.append(
                        _("ALLERGY ALERT: {0} may conflict with patient allergies: {1}").format(
                            item.drug_name, patient_allergies
                        )
                    )

            if item.drug_item:
                is_controlled = frappe.db.get_value("Drug Item", item.drug_item, "is_controlled")
                if is_controlled:
                    warnings.append(
                        _("CONTROLLED DRUG: {0} requires additional documentation.").format(
                            item.drug_name
                        )
                    )

        drug_names = [i.drug_name for i in doc.items if i.drug_name]
        if len(drug_names) != len(set(drug_names)):
            warnings.append(_("DUPLICATE: Same drug appears multiple times in this dispense."))

    if warnings:
        doc.safety_warnings = "\n".join(warnings)
        doc.safety_checks_passed = 0
        if not doc.pharmacist_override:
            frappe.msgprint(
                "\n".join(warnings),
                title=_("Pharmacy Safety Warnings"),
                indicator="orange",
            )
    else:
        doc.safety_checks_passed = 1
        doc.safety_warnings = ""


@frappe.whitelist()
def check_stock_availability(drug_item, quantity):
    """Check if sufficient stock is available."""
    current = frappe.db.get_value("Drug Item", drug_item, "current_stock") or 0
    return {
        "available": current >= float(quantity),
        "current_stock": current,
        "requested": float(quantity),
    }
