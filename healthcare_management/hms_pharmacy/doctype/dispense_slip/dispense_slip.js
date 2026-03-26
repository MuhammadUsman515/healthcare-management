// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Dispense Slip', {
    refresh(frm) {
        if (frm.is_new()) return;

        // Status indicator
        let colors = {
            'Pending': 'orange',
            'In Progress': 'blue',
            'Dispensed': 'green',
            'Partially Dispensed': 'yellow',
            'Cancelled': 'grey'
        };
        if (colors[frm.doc.status]) {
            frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status]);
        }

        // Dispense button
        if (['Pending', 'In Progress', 'Partially Dispensed'].includes(frm.doc.status)) {
            frm.add_custom_button(__('Dispense'), () => {
                frappe.confirm(
                    __('Confirm dispensing medications to {0}?', [frm.doc.patient_name]),
                    () => {
                        frappe.xcall('frappe.client.set_value', {
                            doctype: frm.doctype,
                            name: frm.doc.name,
                            fieldname: {
                                status: 'Dispensed',
                                dispensed_by: frappe.session.user,
                                dispensed_datetime: frappe.datetime.now_datetime()
                            }
                        }).then(() => {
                            frm.reload_doc();
                            frappe.show_alert({
                                message: __('Medications dispensed successfully'),
                                indicator: 'green'
                            });
                        });
                    }
                );
            }).addClass('btn-primary');
        }

        // Show stock availability for each item
        if (frm.doc.items && frm.doc.items.length) {
            dispense_slip_check_stock(frm);
        }

        // Calculate totals
        dispense_slip_calculate_totals(frm);
    },

    validate(frm) {
        // Check for controlled drugs
        dispense_slip_warn_controlled(frm);
    }
});

frappe.ui.form.on('Dispense Slip Item', {
    item(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item) {
            // Check stock for the selected item
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Bin',
                    filters: {
                        item_code: row.item,
                        warehouse: frm.doc.warehouse || 'Pharmacy - HMS'
                    },
                    fieldname: 'actual_qty'
                },
                callback(r) {
                    if (r.message) {
                        let qty = r.message.actual_qty || 0;
                        if (qty <= 0) {
                            frappe.msgprint({
                                title: __('Out of Stock'),
                                message: __('{0} is currently out of stock in the pharmacy.', [row.item]),
                                indicator: 'red'
                            });
                        } else if (row.quantity && qty < row.quantity) {
                            frappe.msgprint({
                                title: __('Insufficient Stock'),
                                message: __('Only {0} units of {1} available. Requested: {2}', [qty, row.item, row.quantity]),
                                indicator: 'orange'
                            });
                        }
                    }
                }
            });

            // Check if controlled drug
            frappe.db.get_value('Item', row.item, 'is_controlled', (r) => {
                if (r && r.is_controlled) {
                    frappe.msgprint({
                        title: __('Controlled Substance'),
                        message: __('Warning: {0} is a controlled drug. Ensure proper authorization and documentation.', [row.item]),
                        indicator: 'red'
                    });
                }
            });
        }
    },

    quantity(frm, cdt, cdn) {
        dispense_slip_calculate_row_total(frm, cdt, cdn);
        dispense_slip_calculate_totals(frm);
    },

    rate(frm, cdt, cdn) {
        dispense_slip_calculate_row_total(frm, cdt, cdn);
        dispense_slip_calculate_totals(frm);
    }
});

function dispense_slip_check_stock(frm) {
    let items = frm.doc.items.map(d => d.item).filter(Boolean);
    if (!items.length) return;

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Bin',
            filters: {
                item_code: ['in', items],
                warehouse: frm.doc.warehouse || 'Pharmacy - HMS'
            },
            fields: ['item_code', 'actual_qty']
        },
        callback(r) {
            if (!r.message) return;
            let stock_map = {};
            r.message.forEach(b => { stock_map[b.item_code] = b.actual_qty; });

            let out_of_stock = [];
            frm.doc.items.forEach(item => {
                if (item.item) {
                    let avail = stock_map[item.item] || 0;
                    if (avail <= 0) {
                        out_of_stock.push(item.item);
                    }
                }
            });

            if (out_of_stock.length) {
                frm.dashboard.add_indicator(
                    __('Out of Stock: {0}', [out_of_stock.join(', ')]), 'red'
                );
            }
        }
    });
}

function dispense_slip_calculate_row_total(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let amount = (row.quantity || 0) * (row.rate || 0);
    frappe.model.set_value(cdt, cdn, 'amount', amount);
}

function dispense_slip_calculate_totals(frm) {
    let total = 0;
    (frm.doc.items || []).forEach(item => {
        total += (item.amount || 0);
    });
    frm.set_value('total_amount', total);
}

function dispense_slip_warn_controlled(frm) {
    if (!frm.doc.items || !frm.doc.items.length) return;

    let controlled = frm.doc.items.filter(d => d.is_controlled);
    if (controlled.length) {
        frappe.msgprint({
            title: __('Controlled Substances'),
            message: __('This slip contains {0} controlled substance(s). Ensure proper documentation and authorization before dispensing.', [controlled.length]),
            indicator: 'orange'
        });
    }
}
