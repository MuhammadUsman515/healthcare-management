// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Final Bill', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show payment summary
        final_bill_show_payment_summary(frm);

        // Status indicator
        let colors = {
            'Draft': 'red',
            'Pending': 'orange',
            'Partially Paid': 'yellow',
            'Paid': 'green',
            'Insurance Pending': 'blue',
            'Cancelled': 'grey',
            'Written Off': 'darkgrey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        if (frm.doc.docstatus === 1 && !['Paid', 'Cancelled', 'Written Off'].includes(frm.doc.status)) {
            // Collect Payment button
            frm.add_custom_button(__('Collect Payment'), () => {
                let outstanding = (frm.doc.grand_total || 0) - (frm.doc.total_paid || 0);
                let d = new frappe.ui.Dialog({
                    title: __('Collect Payment'),
                    fields: [
                        {
                            fieldname: 'amount',
                            fieldtype: 'Currency',
                            label: __('Amount'),
                            reqd: 1,
                            default: outstanding
                        },
                        {
                            fieldname: 'mode_of_payment',
                            fieldtype: 'Link',
                            label: __('Mode of Payment'),
                            options: 'Mode of Payment',
                            reqd: 1
                        },
                        {
                            fieldname: 'reference_no',
                            fieldtype: 'Data',
                            label: __('Reference No'),
                            depends_on: 'eval:doc.mode_of_payment!="Cash"'
                        }
                    ],
                    primary_action_label: __('Submit Payment'),
                    primary_action(values) {
                        frappe.call({
                            method: 'frappe.client.insert',
                            args: {
                                doc: {
                                    doctype: 'Payment Entry',
                                    payment_type: 'Receive',
                                    party_type: 'Patient',
                                    party: frm.doc.patient,
                                    paid_amount: values.amount,
                                    mode_of_payment: values.mode_of_payment,
                                    reference_no: values.reference_no,
                                    reference_date: frappe.datetime.get_today(),
                                    bill: frm.doc.name
                                }
                            },
                            callback() {
                                d.hide();
                                frm.reload_doc();
                                frappe.show_alert({
                                    message: __('Payment recorded successfully'),
                                    indicator: 'green'
                                });
                            }
                        });
                    }
                });
                d.show();
            }).addClass('btn-primary');

            // Apply Discount button
            frm.add_custom_button(__('Apply Discount'), () => {
                let d = new frappe.ui.Dialog({
                    title: __('Apply Discount'),
                    fields: [
                        {
                            fieldname: 'discount_type',
                            fieldtype: 'Select',
                            label: __('Discount Type'),
                            options: 'Percentage\nAmount',
                            reqd: 1,
                            default: 'Percentage'
                        },
                        {
                            fieldname: 'discount_value',
                            fieldtype: 'Float',
                            label: __('Discount Value'),
                            reqd: 1
                        },
                        {
                            fieldname: 'reason',
                            fieldtype: 'Small Text',
                            label: __('Reason'),
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Apply'),
                    primary_action(values) {
                        let discount_amount = values.discount_value;
                        if (values.discount_type === 'Percentage') {
                            discount_amount = (frm.doc.grand_total || 0) * values.discount_value / 100;
                        }
                        frm.set_value('discount_amount', discount_amount);
                        frm.set_value('discount_reason', values.reason);
                        frm.save();
                        d.hide();
                    }
                });
                d.show();
            }, __('Actions'));
        }

        // Print button
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Print Bill'), () => {
                frappe.utils.print(frm.doctype, frm.docname, 'Final Bill Print');
            }, __('Actions'));
        }

        // Show insurance/welfare deductions
        final_bill_show_deductions(frm);
    }
});

function final_bill_show_payment_summary(frm) {
    let grand_total = frm.doc.grand_total || 0;
    let total_paid = frm.doc.total_paid || 0;
    let insurance_amount = frm.doc.insurance_amount || 0;
    let welfare_amount = frm.doc.welfare_amount || 0;
    let discount_amount = frm.doc.discount_amount || 0;
    let outstanding = grand_total - total_paid - insurance_amount - welfare_amount - discount_amount;

    if (outstanding < 0) outstanding = 0;

    let html = '<div class="frappe-card p-3 mb-3">';
    html += '<h6>' + __('Payment Summary') + '</h6>';
    html += '<table class="table table-sm table-borderless mb-0">';
    html += '<tr><td>' + __('Grand Total') + '</td><td class="text-right"><strong>' + format_currency(grand_total) + '</strong></td></tr>';
    if (insurance_amount) {
        html += '<tr><td>' + __('Insurance Coverage') + '</td><td class="text-right text-success">- ' + format_currency(insurance_amount) + '</td></tr>';
    }
    if (welfare_amount) {
        html += '<tr><td>' + __('Welfare Assistance') + '</td><td class="text-right text-success">- ' + format_currency(welfare_amount) + '</td></tr>';
    }
    if (discount_amount) {
        html += '<tr><td>' + __('Discount') + '</td><td class="text-right text-success">- ' + format_currency(discount_amount) + '</td></tr>';
    }
    if (total_paid) {
        html += '<tr><td>' + __('Total Paid') + '</td><td class="text-right text-success">- ' + format_currency(total_paid) + '</td></tr>';
    }
    html += '<tr class="border-top"><td><strong>' + __('Outstanding') + '</strong></td>';
    html += '<td class="text-right"><strong class="' + (outstanding > 0 ? 'text-danger' : 'text-success') + '">';
    html += format_currency(outstanding) + '</strong></td></tr>';
    html += '</table></div>';

    $(frm.layout.wrapper).find('.frappe-control[data-fieldname="items"]').before(html);
}

function final_bill_show_deductions(frm) {
    if (frm.doc.insurance_claim) {
        frm.dashboard.add_indicator(
            __('Insurance: {0}', [frm.doc.insurance_claim]), 'blue'
        );
    }
    if (frm.doc.welfare_case) {
        frm.dashboard.add_indicator(
            __('Welfare: {0}', [frm.doc.welfare_case]), 'green'
        );
    }
}
