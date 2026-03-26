// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Test', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show reference ranges prominently
        lab_test_show_reference_ranges(frm);

        // Highlight critical results
        if (frm.doc.result_status === 'Critical') {
            frm.set_intro(
                __('CRITICAL: Result is outside critical limits. Immediate clinical attention required.'),
                'red'
            );
        } else if (frm.doc.result_status === 'Abnormal') {
            frm.set_intro(
                __('Abnormal: Result is outside normal reference range.'),
                'orange'
            );
        }

        // Status indicator
        let colors = {
            'Pending': 'orange',
            'In Process': 'blue',
            'Result Entered': 'yellow',
            'Verified': 'cyan',
            'Authorized': 'green',
            'Released': 'darkgreen',
            'Rejected': 'red',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Authorize button for supervisors
        if (frm.doc.status === 'Verified' && frappe.user_roles.includes('Lab Supervisor')) {
            frm.add_custom_button(__('Authorize'), () => {
                frappe.confirm(
                    __('Authorize results for test {0}?', [frm.doc.test_name]),
                    () => {
                        frappe.xcall('frappe.client.set_value', {
                            doctype: frm.doctype,
                            name: frm.doc.name,
                            fieldname: {
                                status: 'Authorized',
                                authorized_by: frappe.session.user,
                                authorized_date: frappe.datetime.now_datetime()
                            }
                        }).then(() => {
                            frm.reload_doc();
                            frappe.show_alert({
                                message: __('Test results authorized'),
                                indicator: 'green'
                            });
                        });
                    }
                );
            }).addClass('btn-primary');
        }

        // Verify button for lab technicians
        if (frm.doc.status === 'Result Entered') {
            frm.add_custom_button(__('Verify'), () => {
                frappe.xcall('frappe.client.set_value', {
                    doctype: frm.doctype,
                    name: frm.doc.name,
                    fieldname: {
                        status: 'Verified',
                        verified_by: frappe.session.user
                    }
                }).then(() => frm.reload_doc());
            }).addClass('btn-primary');
        }

        // Release results button
        if (frm.doc.status === 'Authorized') {
            frm.add_custom_button(__('Release Results'), () => {
                frappe.xcall('frappe.client.set_value', {
                    doctype: frm.doctype,
                    name: frm.doc.name,
                    fieldname: 'status',
                    value: 'Released'
                }).then(() => {
                    frm.reload_doc();
                    frappe.show_alert({
                        message: __('Results released'),
                        indicator: 'green'
                    });
                });
            }).addClass('btn-primary');
        }
    },

    result_value(frm) {
        // Auto-evaluate result against reference ranges
        lab_test_evaluate_result(frm);
    }
});

function lab_test_show_reference_ranges(frm) {
    if (frm.doc.normal_range) {
        let html = '<div class="frappe-card p-3 mb-3">';
        html += '<h6 class="text-muted">' + __('Reference Range') + '</h6>';
        html += '<p>' + frappe.utils.escape_html(frm.doc.normal_range) + '</p>';
        if (frm.doc.critical_low || frm.doc.critical_high) {
            html += '<p class="text-danger"><strong>' + __('Critical Limits') + ':</strong> ';
            if (frm.doc.critical_low) html += __('Low: {0}', [frm.doc.critical_low]);
            if (frm.doc.critical_low && frm.doc.critical_high) html += ' | ';
            if (frm.doc.critical_high) html += __('High: {0}', [frm.doc.critical_high]);
            html += '</p>';
        }
        html += '</div>';
        $(frm.fields_dict.result_value.wrapper).before(html);
    }
}

function lab_test_evaluate_result(frm) {
    if (!frm.doc.result_value) return;

    let val = parseFloat(frm.doc.result_value);
    if (isNaN(val)) return;

    if (frm.doc.critical_low && val < parseFloat(frm.doc.critical_low)) {
        frm.set_value('result_status', 'Critical');
        frappe.msgprint({
            title: __('Critical Result'),
            message: __('Result {0} is below critical low limit ({1}). Immediate notification required.', [val, frm.doc.critical_low]),
            indicator: 'red'
        });
    } else if (frm.doc.critical_high && val > parseFloat(frm.doc.critical_high)) {
        frm.set_value('result_status', 'Critical');
        frappe.msgprint({
            title: __('Critical Result'),
            message: __('Result {0} is above critical high limit ({1}). Immediate notification required.', [val, frm.doc.critical_high]),
            indicator: 'red'
        });
    } else if (frm.doc.normal_low && val < parseFloat(frm.doc.normal_low)) {
        frm.set_value('result_status', 'Abnormal');
    } else if (frm.doc.normal_high && val > parseFloat(frm.doc.normal_high)) {
        frm.set_value('result_status', 'Abnormal');
    } else {
        frm.set_value('result_status', 'Normal');
    }
}
