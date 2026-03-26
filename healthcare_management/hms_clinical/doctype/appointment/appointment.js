// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Appointment', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Status-dependent buttons
        if (frm.doc.status === 'Scheduled') {
            frm.add_custom_button(__('Check In'), () => {
                frappe.confirm(
                    __('Check in patient {0}?', [frm.doc.patient_name]),
                    () => {
                        frm.set_value('status', 'Checked In');
                        frm.save().then(() => {
                            frappe.show_alert({
                                message: __('Patient checked in successfully'),
                                indicator: 'green'
                            });
                        });
                    }
                );
            }).addClass('btn-primary');
        }

        if (['Scheduled', 'Checked In'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Reschedule'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Reschedule Appointment'),
                    fields: [
                        {
                            fieldname: 'new_date',
                            fieldtype: 'Date',
                            label: __('New Date'),
                            reqd: 1,
                            default: frm.doc.appointment_date
                        },
                        {
                            fieldname: 'new_time',
                            fieldtype: 'Time',
                            label: __('New Time'),
                            reqd: 1,
                            default: frm.doc.appointment_time
                        }
                    ],
                    primary_action_label: __('Reschedule'),
                    primary_action(values) {
                        frm.set_value('appointment_date', values.new_date);
                        frm.set_value('appointment_time', values.new_time);
                        frm.set_value('status', 'Rescheduled');
                        frm.save();
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));

            frm.add_custom_button(__('Cancel'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Cancel Appointment'),
                    fields: [
                        {
                            fieldname: 'reason',
                            fieldtype: 'Small Text',
                            label: __('Cancellation Reason'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Confirm Cancellation'),
                    primary_action(values) {
                        frm.set_value('cancellation_reason', values.reason);
                        frm.set_value('status', 'Cancelled');
                        frm.save();
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }

        if (frm.doc.status === 'Checked In' && frm.doc.token_number) {
            frm.add_custom_button(__('Print Token'), () => {
                frappe.utils.print(frm.doctype, frm.docname, 'Token Print');
            }, __('Actions'));
        }

        if (frm.doc.status === 'Checked In') {
            frm.add_custom_button(__('Start Consultation'), () => {
                frappe.new_doc('Encounter', {
                    patient: frm.doc.patient,
                    patient_name: frm.doc.patient_name,
                    practitioner: frm.doc.practitioner,
                    appointment: frm.doc.name,
                    department: frm.doc.department
                });
            }).addClass('btn-primary-dark');
        }

        // Set status indicator color
        let indicator_map = {
            'Scheduled': 'orange',
            'Checked In': 'blue',
            'In Consultation': 'purple',
            'Completed': 'green',
            'Cancelled': 'red',
            'No Show': 'grey',
            'Rescheduled': 'yellow'
        };
        if (indicator_map[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), indicator_map[frm.doc.status]);
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
