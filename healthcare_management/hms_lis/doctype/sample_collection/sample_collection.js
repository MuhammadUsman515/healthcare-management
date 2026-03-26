// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sample Collection', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show patient details prominently
        if (frm.doc.patient) {
            sample_collection_show_patient_info(frm);
        }

        // Status indicator
        let colors = {
            'Pending': 'orange',
            'Collected': 'green',
            'Rejected': 'red',
            'Sent to Lab': 'blue',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Priority indicator
        if (frm.doc.priority === 'STAT') {
            frm.dashboard.add_indicator(__('STAT'), 'red');
        } else if (frm.doc.priority === 'Urgent') {
            frm.dashboard.add_indicator(__('Urgent'), 'orange');
        }

        // Collect button
        if (frm.doc.status === 'Pending') {
            frm.add_custom_button(__('Collect'), () => {
                frappe.xcall('frappe.client.set_value', {
                    doctype: frm.doctype,
                    name: frm.doc.name,
                    fieldname: {
                        status: 'Collected',
                        collected_by: frappe.session.user,
                        collection_datetime: frappe.datetime.now_datetime()
                    }
                }).then(() => {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __('Sample marked as collected'),
                        indicator: 'green'
                    });
                });
            }).addClass('btn-primary');

            // Reject button
            frm.add_custom_button(__('Reject'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Reject Sample'),
                    fields: [
                        {
                            fieldname: 'rejection_reason',
                            fieldtype: 'Select',
                            label: __('Rejection Reason'),
                            options: 'Hemolyzed\nClotted\nInsufficient Volume\nWrong Container\nIncorrect Labeling\nExpired\nOther',
                            reqd: 1
                        },
                        {
                            fieldname: 'rejection_notes',
                            fieldtype: 'Small Text',
                            label: __('Additional Notes')
                        }
                    ],
                    primary_action_label: __('Reject Sample'),
                    primary_action(values) {
                        frm.set_value('status', 'Rejected');
                        frm.set_value('rejection_reason', values.rejection_reason);
                        frm.set_value('rejection_notes', values.rejection_notes);
                        frm.save();
                        d.hide();
                        frappe.show_alert({
                            message: __('Sample rejected'),
                            indicator: 'red'
                        });
                    }
                });
                d.show();
            }, __('Actions'));
        }

        // Print barcode label
        if (['Collected', 'Sent to Lab'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Print Barcode Label'), () => {
                frappe.utils.print(frm.doctype, frm.docname, 'Sample Barcode Label');
            }, __('Actions'));
        }

        // Send to Lab button
        if (frm.doc.status === 'Collected') {
            frm.add_custom_button(__('Send to Lab'), () => {
                frappe.xcall('frappe.client.set_value', {
                    doctype: frm.doctype,
                    name: frm.doc.name,
                    fieldname: 'status',
                    value: 'Sent to Lab'
                }).then(() => {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __('Sample sent to lab'),
                        indicator: 'green'
                    });
                });
            }).addClass('btn-primary');
        }
    }
});

function sample_collection_show_patient_info(frm) {
    frappe.db.get_doc('Patient', frm.doc.patient).then(patient => {
        let info = [];
        if (patient.full_name) info.push('<strong>' + frappe.utils.escape_html(patient.full_name) + '</strong>');
        if (patient.age_display) info.push(__('Age: {0}', [patient.age_display]));
        if (patient.gender) info.push(__(patient.gender));
        if (patient.blood_group) info.push(__('Blood Group: {0}', [patient.blood_group]));

        let alerts = [];
        if (patient.is_infection_risk) alerts.push('<span class="badge badge-danger">Infection Risk</span>');
        if (patient.allergies) alerts.push('<span class="badge badge-warning">Allergies</span>');

        if (info.length) {
            let html = info.join(' | ');
            if (alerts.length) html += '<br>' + alerts.join(' ');
            frm.set_intro(html, patient.is_infection_risk ? 'red' : 'blue');
        }
    });
}
