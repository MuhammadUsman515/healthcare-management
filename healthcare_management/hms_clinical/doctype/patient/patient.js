// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient', {
    refresh(frm) {
        // Show alert flags prominently
        patient_show_alerts(frm);

        // Dashboard with counts
        if (!frm.is_new()) {
            patient_show_dashboard(frm);

            frm.add_custom_button(__('New Appointment'), () => {
                frappe.new_doc('Appointment', {
                    patient: frm.doc.name,
                    patient_name: frm.doc.full_name
                });
            }, __('Actions'));

            frm.add_custom_button(__('View History'), () => {
                frappe.route_options = { patient: frm.doc.name };
                frappe.set_route('List', 'Encounter');
            }, __('Actions'));

            frm.add_custom_button(__('View Appointments'), () => {
                frappe.route_options = { patient: frm.doc.name };
                frappe.set_route('List', 'Appointment');
            }, __('Actions'));

            frm.add_custom_button(__('View Lab Tests'), () => {
                frappe.route_options = { patient: frm.doc.name };
                frappe.set_route('List', 'Lab Test');
            }, __('Actions'));
        }

        // Set indicator based on status
        if (frm.doc.status === 'Active') {
            frm.page.set_indicator(__('Active'), 'green');
        } else if (frm.doc.status === 'Disabled') {
            frm.page.set_indicator(__('Disabled'), 'grey');
        } else if (frm.doc.status === 'Deceased') {
            frm.page.set_indicator(__('Deceased'), 'red');
        }
    },

    dob(frm) {
        if (frm.doc.dob) {
            let today = frappe.datetime.get_today();
            let birth = frm.doc.dob;
            let years = frappe.datetime.get_diff(today, birth) / 365.25;
            let age_years = Math.floor(years);
            let age_months = Math.floor((years - age_years) * 12);
            frm.set_value('age_display', age_years + ' Years ' + age_months + ' Months');
        }
    }
});

function patient_show_alerts(frm) {
    let alerts = [];
    if (frm.doc.is_vip) {
        alerts.push('<span class="badge badge-warning">VIP</span>');
    }
    if (frm.doc.is_medico_legal) {
        alerts.push('<span class="badge badge-danger">Medico-Legal</span>');
    }
    if (frm.doc.is_infection_risk) {
        alerts.push('<span class="badge badge-danger">Infection Risk</span>');
    }
    if (frm.doc.is_high_risk) {
        alerts.push('<span class="badge badge-danger">High Risk</span>');
    }
    if (frm.doc.allergies) {
        alerts.push('<span class="badge badge-warning">Allergies: ' + frappe.utils.escape_html(frm.doc.allergies) + '</span>');
    }

    if (alerts.length) {
        frm.set_intro(alerts.join(' '), 'red');
    }
}

function patient_show_dashboard(frm) {
    let patient = frm.doc.name;

    frappe.xcall('frappe.client.get_count', {
        doctype: 'Appointment',
        filters: { patient: patient }
    }).then(count => {
        frm.dashboard.add_indicator(__('Appointments: {0}', [count]), 'blue');
    });

    frappe.xcall('frappe.client.get_count', {
        doctype: 'Encounter',
        filters: { patient: patient }
    }).then(count => {
        frm.dashboard.add_indicator(__('Encounters: {0}', [count]), 'green');
    });

    frappe.xcall('frappe.client.get_count', {
        doctype: 'Lab Test',
        filters: { patient: patient }
    }).then(count => {
        frm.dashboard.add_indicator(__('Lab Tests: {0}', [count]), 'orange');
    });
}
