// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Encounter', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show patient history in sidebar
        if (frm.doc.patient) {
            encounter_show_patient_sidebar(frm);
        }

        if (frm.doc.docstatus === 0) {
            // Draft encounter - show action buttons
            frm.add_custom_button(__('Create Prescription'), () => {
                frappe.new_doc('Prescription', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    encounter: frm.doc.name,
                    practitioner: frm.doc.practitioner
                });
            }, __('Create'));

            frm.add_custom_button(__('Order Lab Test'), () => {
                frappe.new_doc('Lab Order', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    encounter: frm.doc.name,
                    ordering_practitioner: frm.doc.practitioner,
                    provisional_diagnosis: frm.doc.provisional_diagnosis
                });
            }, __('Create'));

            frm.add_custom_button(__('Refer Patient'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Refer Patient'),
                    fields: [
                        {
                            fieldname: 'referral_to',
                            fieldtype: 'Link',
                            label: __('Refer To Practitioner'),
                            options: 'Practitioner',
                            reqd: 1
                        },
                        {
                            fieldname: 'referral_department',
                            fieldtype: 'Link',
                            label: __('Department'),
                            options: 'Department'
                        },
                        {
                            fieldname: 'referral_notes',
                            fieldtype: 'Small Text',
                            label: __('Referral Notes')
                        }
                    ],
                    primary_action_label: __('Refer'),
                    primary_action(values) {
                        frm.set_value('referral_to', values.referral_to);
                        frm.set_value('referral_department', values.referral_department);
                        frm.save().then(() => {
                            frappe.show_alert({
                                message: __('Referral recorded'),
                                indicator: 'green'
                            });
                        });
                        d.hide();
                    }
                });
                d.show();
            }, __('Create'));

            if (frm.doc.admit_patient) {
                frm.add_custom_button(__('Create Admission'), () => {
                    frappe.new_doc('Inpatient Admission', {
                        patient: frm.doc.patient,
                        patient_name: frm.doc.patient_name,
                        encounter: frm.doc.name,
                        primary_practitioner: frm.doc.practitioner,
                        department: frm.doc.department,
                        provisional_diagnosis: frm.doc.provisional_diagnosis
                    });
                }, __('Create'));
            }

            frm.add_custom_button(__('Record Vitals'), () => {
                frappe.new_doc('Vital Signs', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    encounter: frm.doc.name,
                    practitioner: frm.doc.practitioner
                });
            }, __('Create'));
        }
    },

    practitioner(frm) {
        if (frm.doc.practitioner) {
            frappe.db.get_value('Practitioner', frm.doc.practitioner, 'department', (r) => {
                if (r && r.department) {
                    frm.set_value('department', r.department);
                }
            });
        }
    }
});

function encounter_show_patient_sidebar(frm) {
    // Fetch recent encounters for the patient
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Encounter',
            filters: {
                patient: frm.doc.patient,
                name: ['!=', frm.doc.name]
            },
            fields: ['name', 'encounter_date', 'practitioner_name', 'provisional_diagnosis'],
            order_by: 'encounter_date desc',
            limit_page_length: 5
        },
        callback(r) {
            if (r.message && r.message.length) {
                let html = '<div class="patient-history"><h6 class="text-muted">Recent Encounters</h6><ul class="list-unstyled">';
                r.message.forEach(enc => {
                    html += `<li class="mb-2">
                        <a href="/app/encounter/${enc.name}">${frappe.datetime.str_to_user(enc.encounter_date)}</a>
                        <br><small class="text-muted">${enc.practitioner_name || ''}</small>
                        <br><small>${enc.provisional_diagnosis || ''}</small>
                    </li>`;
                });
                html += '</ul></div>';
                frm.sidebar.append(html);
            }
        }
    });
}
