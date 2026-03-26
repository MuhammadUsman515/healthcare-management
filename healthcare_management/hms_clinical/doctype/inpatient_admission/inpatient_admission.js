// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inpatient Admission', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Prominent bed/ward display
        if (frm.doc.ward || frm.doc.bed) {
            let bed_info = [];
            if (frm.doc.ward) bed_info.push(__('Ward: {0}', [frm.doc.ward]));
            if (frm.doc.bed) bed_info.push(__('Bed: {0}', [frm.doc.bed]));
            if (frm.doc.bed_class) bed_info.push(__('Class: {0}', [frm.doc.bed_class]));
            frm.set_intro(bed_info.join(' | '), frm.doc.isolation_type ? 'red' : 'blue');
        }

        if (frm.doc.isolation_type) {
            frm.dashboard.add_indicator(
                __('Isolation: {0}', [frm.doc.isolation_type]), 'red'
            );
        }

        // Status-dependent action buttons
        if (frm.doc.status === 'Admitted' && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Discharge'), () => {
                frappe.confirm(
                    __('Initiate discharge process for {0}?', [frm.doc.patient_name]),
                    () => {
                        frappe.xcall('frappe.client.set_value', {
                            doctype: frm.doctype,
                            name: frm.doc.name,
                            fieldname: 'status',
                            value: 'Discharge Initiated'
                        }).then(() => frm.reload_doc());
                    }
                );
            }).addClass('btn-primary');

            frm.add_custom_button(__('Transfer'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Transfer Patient'),
                    fields: [
                        {
                            fieldname: 'new_ward',
                            fieldtype: 'Link',
                            label: __('New Ward'),
                            options: 'Ward',
                            reqd: 1
                        },
                        {
                            fieldname: 'new_bed',
                            fieldtype: 'Link',
                            label: __('New Bed'),
                            options: 'Bed'
                        },
                        {
                            fieldname: 'transfer_reason',
                            fieldtype: 'Small Text',
                            label: __('Transfer Reason')
                        }
                    ],
                    primary_action_label: __('Transfer'),
                    primary_action(values) {
                        frm.set_value('ward', values.new_ward);
                        if (values.new_bed) {
                            frm.set_value('bed', values.new_bed);
                        }
                        frm.set_value('status', 'Transferred');
                        frm.save();
                        d.hide();
                        frappe.show_alert({
                            message: __('Patient transferred successfully'),
                            indicator: 'green'
                        });
                    }
                });
                d.show();
            }, __('Actions'));

            frm.add_custom_button(__('Order Lab Test'), () => {
                frappe.new_doc('Lab Order', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    ordering_practitioner: frm.doc.primary_practitioner
                });
            }, __('Order'));

            frm.add_custom_button(__('Order Medication'), () => {
                frappe.new_doc('Prescription', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    practitioner: frm.doc.primary_practitioner
                });
            }, __('Order'));

            frm.add_custom_button(__('Record Vitals'), () => {
                frappe.new_doc('Vital Signs', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name
                });
            }, __('Order'));

            frm.add_custom_button(__('Nursing Task'), () => {
                frappe.new_doc('Nursing Task', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    admission: frm.doc.name
                });
            }, __('Order'));
        }

        if (frm.doc.status === 'Discharge Initiated') {
            frm.add_custom_button(__('Create Discharge Summary'), () => {
                frappe.new_doc('Discharge Summary', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    admission: frm.doc.name,
                    practitioner: frm.doc.primary_practitioner
                });
            }).addClass('btn-primary');
        }

        // Length of stay indicator
        if (frm.doc.admission_date && frm.doc.status === 'Admitted') {
            let los = frappe.datetime.get_diff(frappe.datetime.get_today(), frm.doc.admission_date);
            frm.dashboard.add_indicator(__('Day {0}', [los]), los > 14 ? 'orange' : 'blue');
        }

        // Status indicator
        let colors = {
            'Admitted': 'blue',
            'Transferred': 'purple',
            'Discharge Initiated': 'orange',
            'Billing Clearance': 'yellow',
            'Discharged': 'green',
            'LAMA': 'red',
            'Expired': 'darkgrey',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }
    }
});
