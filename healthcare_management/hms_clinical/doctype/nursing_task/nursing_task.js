// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Nursing Task', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show patient info sidebar
        if (frm.doc.patient) {
            nursing_task_show_patient_sidebar(frm);
        }

        // Status indicator
        let colors = {
            'Pending': 'orange',
            'In Progress': 'blue',
            'Completed': 'green',
            'Escalated': 'red',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Timer showing time since assignment
        if (frm.doc.assigned_datetime && ['Pending', 'In Progress'].includes(frm.doc.status)) {
            nursing_task_show_timer(frm);
        }

        // Complete button
        if (['Pending', 'In Progress'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Complete'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Complete Task'),
                    fields: [
                        {
                            fieldname: 'notes',
                            fieldtype: 'Small Text',
                            label: __('Completion Notes')
                        }
                    ],
                    primary_action_label: __('Complete'),
                    primary_action(values) {
                        frappe.xcall('frappe.client.set_value', {
                            doctype: frm.doctype,
                            name: frm.doc.name,
                            fieldname: {
                                status: 'Completed',
                                completed_by: frappe.session.user,
                                completed_datetime: frappe.datetime.now_datetime(),
                                completion_notes: values.notes || ''
                            }
                        }).then(() => {
                            frm.reload_doc();
                            frappe.show_alert({
                                message: __('Task marked as completed'),
                                indicator: 'green'
                            });
                        });
                        d.hide();
                    }
                });
                d.show();
            }).addClass('btn-primary');

            // Start button if pending
            if (frm.doc.status === 'Pending') {
                frm.add_custom_button(__('Start'), () => {
                    frappe.xcall('frappe.client.set_value', {
                        doctype: frm.doctype,
                        name: frm.doc.name,
                        fieldname: {
                            status: 'In Progress',
                            started_by: frappe.session.user,
                            started_datetime: frappe.datetime.now_datetime()
                        }
                    }).then(() => frm.reload_doc());
                });
            }
        }

        // Escalate button
        if (['Pending', 'In Progress'].includes(frm.doc.status)) {
            let is_overdue = frm.doc.due_datetime &&
                frappe.datetime.get_diff(frappe.datetime.now_datetime(), frm.doc.due_datetime, 'minutes') > 0;

            if (is_overdue) {
                frm.dashboard.add_indicator(__('OVERDUE'), 'red');
            }

            frm.add_custom_button(__('Escalate'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Escalate Task'),
                    fields: [
                        {
                            fieldname: 'escalate_to',
                            fieldtype: 'Link',
                            label: __('Escalate To'),
                            options: 'User',
                            reqd: 1
                        },
                        {
                            fieldname: 'escalation_reason',
                            fieldtype: 'Small Text',
                            label: __('Reason'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Escalate'),
                    primary_action(values) {
                        frm.set_value('status', 'Escalated');
                        frm.set_value('escalated_to', values.escalate_to);
                        frm.set_value('escalation_reason', values.escalation_reason);
                        frm.set_value('escalation_datetime', frappe.datetime.now_datetime());
                        frm.save().then(() => {
                            frappe.show_alert({
                                message: __('Task escalated'),
                                indicator: 'orange'
                            });
                        });
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }

        // Priority indicator
        if (frm.doc.priority === 'Urgent') {
            frm.dashboard.add_indicator(__('Urgent'), 'red');
        } else if (frm.doc.priority === 'High') {
            frm.dashboard.add_indicator(__('High Priority'), 'orange');
        }
    },

    status(frm) {
        if (frm.doc.status === 'Completed' && !frm.doc.completed_datetime) {
            frm.set_value('completed_datetime', frappe.datetime.now_datetime());
        }
    }
});

function nursing_task_show_timer(frm) {
    let assigned = moment(frm.doc.assigned_datetime);
    let now = moment();
    let duration = moment.duration(now.diff(assigned));
    let hours = Math.floor(duration.asHours());
    let minutes = duration.minutes();

    frm.dashboard.add_indicator(
        __('Elapsed: {0}h {1}m', [hours, minutes]),
        hours >= 2 ? 'red' : hours >= 1 ? 'orange' : 'blue'
    );
}

function nursing_task_show_patient_sidebar(frm) {
    frappe.db.get_doc('Patient', frm.doc.patient).then(patient => {
        let html = '<div class="patient-sidebar-info">';
        html += '<h6 class="text-muted">' + __('Patient Info') + '</h6>';
        html += '<p><strong>' + frappe.utils.escape_html(patient.full_name || '') + '</strong></p>';
        if (patient.age_display) {
            html += '<p class="text-muted">' + __('Age') + ': ' + patient.age_display + '</p>';
        }
        if (patient.gender) {
            html += '<p class="text-muted">' + __(patient.gender) + '</p>';
        }
        if (patient.blood_group) {
            html += '<p class="text-muted">' + __('Blood Group') + ': ' + patient.blood_group + '</p>';
        }

        // Alerts
        if (patient.is_infection_risk) {
            html += '<p><span class="badge badge-danger">' + __('Infection Risk') + '</span></p>';
        }
        if (patient.allergies) {
            html += '<p><span class="badge badge-warning">' + __('Allergies') + ': ' + frappe.utils.escape_html(patient.allergies) + '</span></p>';
        }

        html += '</div>';
        frm.sidebar.append(html);
    });

    // Show recent vitals
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Vital Signs',
            filters: { patient: frm.doc.patient },
            fields: ['signs_date', 'temperature', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'oxygen_saturation'],
            order_by: 'signs_date desc',
            limit_page_length: 1
        },
        callback(r) {
            if (r.message && r.message.length) {
                let v = r.message[0];
                let html = '<div class="patient-sidebar-vitals mt-2">';
                html += '<h6 class="text-muted">' + __('Latest Vitals') + '</h6>';
                html += '<small class="text-muted">' + frappe.datetime.str_to_user(v.signs_date) + '</small>';
                if (v.temperature) html += '<p>Temp: ' + v.temperature + '°C</p>';
                if (v.systolic_bp) html += '<p>BP: ' + v.systolic_bp + '/' + (v.diastolic_bp || '-') + '</p>';
                if (v.heart_rate) html += '<p>HR: ' + v.heart_rate + ' bpm</p>';
                if (v.oxygen_saturation) html += '<p>SpO2: ' + v.oxygen_saturation + '%</p>';
                html += '</div>';
                frm.sidebar.append(html);
            }
        }
    });
}
