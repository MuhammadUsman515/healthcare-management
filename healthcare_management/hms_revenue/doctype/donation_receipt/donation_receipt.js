// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Donation Receipt', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Show fund balance
        donation_receipt_show_fund_balance(frm);

        // Print receipt button
        frm.add_custom_button(__('Print Receipt'), () => {
            frappe.utils.print(frm.doctype, frm.docname, 'Donation Receipt Print');
        }, __('Actions'));

        // Status indicator
        let colors = {
            'Draft': 'orange',
            'Received': 'green',
            'Acknowledged': 'blue',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Category badge
        if (frm.doc.donation_category) {
            let cat_colors = {
                'Zakat': 'green',
                'Sadaqah': 'blue',
                'General': 'orange',
                'Waqf': 'purple'
            };
            frm.dashboard.add_indicator(
                __(frm.doc.donation_category),
                cat_colors[frm.doc.donation_category] || 'grey'
            );
        }
    },

    donor(frm) {
        // Auto-fetch donor details
        if (frm.doc.donor) {
            frappe.db.get_doc('Donor', frm.doc.donor).then(donor => {
                frm.set_value('donor_name', donor.donor_name || donor.full_name);
                frm.set_value('donor_phone', donor.phone || donor.mobile_no);
                frm.set_value('donor_email', donor.email);
                frm.set_value('donor_address', donor.address);

                frappe.show_alert({
                    message: __('Donor details fetched'),
                    indicator: 'green'
                });
            });
        }
    },

    donation_category(frm) {
        // Show category-specific notes
        let notes = {
            'Zakat': __('Zakat funds can only be used for eligible recipients as per Islamic guidelines.'),
            'Sadaqah': __('Sadaqah funds can be used for general welfare purposes.'),
            'General': __('General donations can be allocated to any hospital fund.'),
            'Waqf': __('Waqf contributions are endowment funds with restricted usage.')
        };
        if (notes[frm.doc.donation_category]) {
            frm.set_intro(notes[frm.doc.donation_category], 'blue');
        }
    }
});

function donation_receipt_show_fund_balance(frm) {
    if (!frm.doc.donation_category) return;

    frappe.call({
        method: 'frappe.client.get_value',
        args: {
            doctype: 'Welfare Fund',
            filters: { fund_type: frm.doc.donation_category },
            fieldname: 'available_balance'
        },
        callback(r) {
            if (r.message && r.message.available_balance !== undefined) {
                frm.dashboard.add_indicator(
                    __('Fund Balance: {0}', [format_currency(r.message.available_balance)]),
                    r.message.available_balance > 0 ? 'green' : 'red'
                );
            }
        }
    });
}
