// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Prescription', {
    refresh(frm) {
        if (frm.is_new()) return;

        if (frm.doc.docstatus === 1 && frm.doc.status === 'Signed') {
            frm.add_custom_button(__('Send to Pharmacy'), () => {
                frappe.confirm(
                    __('Send this prescription to the pharmacy for dispensing?'),
                    () => {
                        frappe.xcall(
                            'frappe.client.set_value',
                            {
                                doctype: 'Prescription',
                                name: frm.doc.name,
                                fieldname: 'status',
                                value: 'Sent to Pharmacy'
                            }
                        ).then(() => {
                            frm.reload_doc();
                            frappe.show_alert({
                                message: __('Prescription sent to pharmacy'),
                                indicator: 'green'
                            });
                        });
                    }
                );
            }).addClass('btn-primary');
        }

        if (frm.doc.status === 'Sent to Pharmacy') {
            frm.add_custom_button(__('Create Dispense Slip'), () => {
                frappe.new_doc('Dispense Slip', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    prescription: frm.doc.name
                });
            });
        }

        // Status indicator
        let colors = {
            'Draft': 'red',
            'Signed': 'blue',
            'Sent to Pharmacy': 'orange',
            'Partially Dispensed': 'yellow',
            'Fully Dispensed': 'green',
            'Cancelled': 'grey',
            'Expired': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }
    },

    validate(frm) {
        // Warn on duplicate drugs in the prescription
        prescription_check_duplicates(frm);
    }
});

frappe.ui.form.on('Prescription Item', {
    drug_item(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.drug_item) {
            frappe.db.get_value('Item', row.drug_item,
                ['default_dosage', 'default_route', 'default_frequency', 'is_controlled'],
                (r) => {
                    if (r) {
                        if (r.default_dosage) {
                            frappe.model.set_value(cdt, cdn, 'dosage', r.default_dosage);
                        }
                        if (r.default_route) {
                            frappe.model.set_value(cdt, cdn, 'route', r.default_route);
                        }
                        if (r.default_frequency) {
                            frappe.model.set_value(cdt, cdn, 'frequency', r.default_frequency);
                        }
                        if (r.is_controlled) {
                            frappe.msgprint({
                                title: __('Controlled Drug'),
                                message: __('Warning: {0} is a controlled substance. Additional authorization may be required.', [row.drug_item]),
                                indicator: 'orange'
                            });
                        }
                    }
                }
            );
        }
    }
});

function prescription_check_duplicates(frm) {
    if (!frm.doc.items || !frm.doc.items.length) return;

    let drugs = {};
    let duplicates = [];
    frm.doc.items.forEach(item => {
        if (item.drug_item) {
            if (drugs[item.drug_item]) {
                duplicates.push(item.drug_item);
            }
            drugs[item.drug_item] = true;
        }
    });

    if (duplicates.length) {
        frappe.msgprint({
            title: __('Duplicate Drugs'),
            message: __('The following drugs appear more than once: {0}. Please verify this is intentional.', [duplicates.join(', ')]),
            indicator: 'orange'
        });
    }
}
