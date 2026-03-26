// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Discharge Summary', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Print button
        frm.add_custom_button(__('Print'), () => {
            frappe.utils.print(frm.doctype, frm.docname, 'Discharge Summary Print');
        }, __('Actions'));

        // Show medication list at discharge
        if (frm.doc.discharge_medications && frm.doc.discharge_medications.length) {
            discharge_summary_show_medications(frm);
        }

        // Status indicator
        let colors = {
            'Draft': 'orange',
            'Completed': 'green',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }
    },

    admission(frm) {
        // Auto-fetch admission details
        if (frm.doc.admission) {
            frappe.db.get_doc('Inpatient Admission', frm.doc.admission).then(admission => {
                frm.set_value('patient', admission.patient);
                frm.set_value('patient_name', admission.patient_name);
                frm.set_value('practitioner', admission.primary_practitioner);
                frm.set_value('department', admission.department);
                frm.set_value('admission_date', admission.admission_date);
                frm.set_value('ward', admission.ward);
                frm.set_value('bed', admission.bed);
                frm.set_value('provisional_diagnosis', admission.provisional_diagnosis);

                frappe.show_alert({
                    message: __('Admission details fetched'),
                    indicator: 'green'
                });

                // Fetch encounters during this admission
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Encounter',
                        filters: {
                            patient: admission.patient,
                            encounter_date: ['>=', admission.admission_date]
                        },
                        fields: ['name', 'encounter_date', 'practitioner_name', 'provisional_diagnosis'],
                        order_by: 'encounter_date desc'
                    },
                    callback(r) {
                        if (r.message && r.message.length) {
                            let notes = r.message.map(enc =>
                                frappe.datetime.str_to_user(enc.encounter_date) + ' - ' +
                                (enc.practitioner_name || '') + ': ' +
                                (enc.provisional_diagnosis || '')
                            ).join('\n');
                            frm.set_value('clinical_notes', notes);
                        }
                    }
                });

                // Fetch active prescriptions
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Prescription',
                        filters: {
                            patient: admission.patient,
                            creation: ['>=', admission.admission_date],
                            status: ['not in', ['Cancelled', 'Expired']]
                        },
                        fields: ['name', 'creation']
                    },
                    callback(r) {
                        if (r.message && r.message.length) {
                            frm.dashboard.add_indicator(
                                __('Active Prescriptions: {0}', [r.message.length]), 'blue'
                            );
                        }
                    }
                });
            });
        }
    }
});

function discharge_summary_show_medications(frm) {
    let html = '<div class="frappe-card p-3 mb-3">';
    html += '<h6>' + __('Discharge Medications') + '</h6>';
    html += '<table class="table table-sm table-bordered mb-0"><thead><tr>';
    html += '<th>' + __('Drug') + '</th><th>' + __('Dosage') + '</th>';
    html += '<th>' + __('Frequency') + '</th><th>' + __('Duration') + '</th>';
    html += '<th>' + __('Instructions') + '</th>';
    html += '</tr></thead><tbody>';

    frm.doc.discharge_medications.forEach(med => {
        html += '<tr>';
        html += '<td>' + (med.drug || '') + '</td>';
        html += '<td>' + (med.dosage || '') + '</td>';
        html += '<td>' + (med.frequency || '') + '</td>';
        html += '<td>' + (med.duration || '') + '</td>';
        html += '<td>' + (med.instructions || '') + '</td>';
        html += '</tr>';
    });

    html += '</tbody></table></div>';
    $(frm.layout.wrapper).find('.form-layout').prepend(html);
}
