// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Lab Order', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Status indicator
        let colors = {
            'Ordered': 'blue',
            'Sample Pending': 'orange',
            'Collected': 'yellow',
            'In Process': 'purple',
            'Result Entered': 'cyan',
            'Verified': 'light-blue',
            'Authorized': 'green',
            'Released': 'darkgreen',
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

        if (frm.doc.docstatus === 1) {
            if (['Ordered', 'Sample Pending'].includes(frm.doc.status)) {
                frm.add_custom_button(__('Collect Sample'), () => {
                    frappe.new_doc('Sample Collection', {
                        patient: frm.doc.patient,
                        patient_name: frm.doc.patient_name,
                        lab_order: frm.doc.name
                    });
                }).addClass('btn-primary');
            }

            if (frm.doc.status === 'Collected') {
                frm.add_custom_button(__('Start Processing'), () => {
                    frappe.xcall('frappe.client.set_value', {
                        doctype: frm.doctype,
                        name: frm.doc.name,
                        fieldname: 'status',
                        value: 'In Process'
                    }).then(() => frm.reload_doc());
                }).addClass('btn-primary');
            }

            // Show results summary for completed tests
            if (['Result Entered', 'Verified', 'Authorized', 'Released'].includes(frm.doc.status)) {
                lab_order_show_results_summary(frm);
            }
        }
    }
});

function lab_order_show_results_summary(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Lab Test',
            filters: { lab_order: frm.doc.name },
            fields: ['name', 'test_name', 'result_value', 'result_unit', 'normal_range', 'result_status', 'status']
        },
        callback(r) {
            if (r.message && r.message.length) {
                let html = '<div class="frappe-card p-3 mb-3"><h6>Results Summary</h6>';
                html += '<table class="table table-sm table-bordered"><thead><tr>';
                html += '<th>Test</th><th>Result</th><th>Unit</th><th>Reference</th><th>Status</th>';
                html += '</tr></thead><tbody>';

                r.message.forEach(test => {
                    let badge_class = 'secondary';
                    if (test.result_status === 'Normal') badge_class = 'success';
                    else if (test.result_status === 'Abnormal') badge_class = 'warning';
                    else if (test.result_status === 'Critical') badge_class = 'danger';

                    html += `<tr>
                        <td><a href="/app/lab-test/${test.name}">${test.test_name}</a></td>
                        <td><strong>${test.result_value || '-'}</strong></td>
                        <td>${test.result_unit || ''}</td>
                        <td>${test.normal_range || ''}</td>
                        <td><span class="badge badge-${badge_class}">${test.result_status || test.status}</span></td>
                    </tr>`;
                });

                html += '</tbody></table></div>';
                $(frm.fields_dict.items.wrapper).before(html);
            }
        }
    });
}
