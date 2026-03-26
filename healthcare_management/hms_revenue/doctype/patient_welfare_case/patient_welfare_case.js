// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patient Welfare Case', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Status indicator
        let colors = {
            'Draft': 'red',
            'Pending Assessment': 'orange',
            'Under Review': 'yellow',
            'Approved': 'green',
            'Partially Approved': 'blue',
            'Rejected': 'red',
            'Expired': 'grey',
            'Closed': 'darkgrey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Show assessment status
        if (frm.doc.assessment_score) {
            frm.dashboard.add_indicator(
                __('Assessment Score: {0}', [frm.doc.assessment_score]),
                frm.doc.assessment_score >= 70 ? 'green' : frm.doc.assessment_score >= 40 ? 'orange' : 'red'
            );
        }

        // Show fund availability
        welfare_case_show_fund_balance(frm);

        // Request Approval button
        if (frm.doc.status === 'Pending Assessment' || frm.doc.status === 'Draft') {
            frm.add_custom_button(__('Request Approval'), () => {
                frappe.confirm(
                    __('Submit this welfare case for approval?'),
                    () => {
                        frm.set_value('status', 'Under Review');
                        frm.set_value('submitted_date', frappe.datetime.get_today());
                        frm.set_value('submitted_by', frappe.session.user);
                        frm.save().then(() => {
                            frappe.show_alert({
                                message: __('Welfare case submitted for approval'),
                                indicator: 'green'
                            });
                        });
                    }
                );
            }).addClass('btn-primary');
        }

        // Approval/Rejection buttons for reviewers
        if (frm.doc.status === 'Under Review' && frappe.user_roles.includes('Welfare Officer')) {
            frm.add_custom_button(__('Approve'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Approve Welfare Case'),
                    fields: [
                        {
                            fieldname: 'approved_amount',
                            fieldtype: 'Currency',
                            label: __('Approved Amount'),
                            reqd: 1,
                            default: frm.doc.requested_amount
                        },
                        {
                            fieldname: 'fund_source',
                            fieldtype: 'Select',
                            label: __('Fund Source'),
                            options: 'Zakat\nSadaqah\nGeneral Welfare\nDonation Fund',
                            reqd: 1
                        },
                        {
                            fieldname: 'remarks',
                            fieldtype: 'Small Text',
                            label: __('Remarks')
                        }
                    ],
                    primary_action_label: __('Approve'),
                    primary_action(values) {
                        frm.set_value('approved_amount', values.approved_amount);
                        frm.set_value('fund_source', values.fund_source);
                        frm.set_value('approval_remarks', values.remarks);
                        frm.set_value('approved_by', frappe.session.user);
                        frm.set_value('approval_date', frappe.datetime.get_today());
                        let status = values.approved_amount < frm.doc.requested_amount
                            ? 'Partially Approved' : 'Approved';
                        frm.set_value('status', status);
                        frm.save();
                        d.hide();
                    }
                });
                d.show();
            }).addClass('btn-primary');

            frm.add_custom_button(__('Reject'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Reject Welfare Case'),
                    fields: [
                        {
                            fieldname: 'rejection_reason',
                            fieldtype: 'Small Text',
                            label: __('Reason for Rejection'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Reject'),
                    primary_action(values) {
                        frm.set_value('status', 'Rejected');
                        frm.set_value('rejection_reason', values.rejection_reason);
                        frm.save();
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }
    }
});

function welfare_case_show_fund_balance(frm) {
    if (!frm.doc.fund_source) return;

    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Welfare Fund',
            filters: { fund_type: frm.doc.fund_source },
            fieldname: 'available_balance'
        },
        callback(r) {
            if (r.message && r.message.available_balance !== undefined) {
                let balance = r.message.available_balance;
                frm.dashboard.add_indicator(
                    __('Fund Balance ({0}): {1}', [frm.doc.fund_source, format_currency(balance)]),
                    balance > 0 ? 'green' : 'red'
                );
            }
        }
    });
}
