frappe.pages['cashier-counter'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Cashier Counter',
        single_column: true
    });

    page.main.html(`
        <div class="row">
            <!-- Left: Patient search and billing -->
            <div class="col-md-8">
                <div class="card mb-3">
                    <div class="card-header"><h5>Patient Search</h5></div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <div id="patient-search-field"></div>
                            </div>
                            <div class="col-md-4">
                                <div id="patient-info" class="text-muted">Select a patient to view pending bills</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card mb-3">
                    <div class="card-header"><h5>Pending Bills</h5></div>
                    <div class="card-body" id="pending-bills">
                        <p class="text-muted">No patient selected</p>
                    </div>
                </div>
                <div class="card mb-3" id="receipt-form-card" style="display:none;">
                    <div class="card-header"><h5>Create Receipt</h5></div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3">
                                <label>Amount</label>
                                <input type="number" id="receipt-amount" class="form-control" placeholder="0.00">
                            </div>
                            <div class="col-md-3">
                                <label>Payment Mode</label>
                                <select id="payment-mode" class="form-control">
                                    <option value="Cash">Cash</option>
                                    <option value="Card">Card</option>
                                    <option value="Online">Online</option>
                                    <option value="Cheque">Cheque</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label>Reference</label>
                                <input type="text" id="payment-reference" class="form-control" placeholder="Ref #">
                            </div>
                            <div class="col-md-3 d-flex align-items-end">
                                <button class="btn btn-primary btn-block" id="btn-create-receipt">
                                    <i class="fa fa-check"></i> Create Receipt
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- Right: Summary and recent receipts -->
            <div class="col-md-4">
                <div class="card mb-3">
                    <div class="card-header bg-success text-white"><h5>Today's Collection</h5></div>
                    <div class="card-body" id="collection-summary">
                        <p class="text-muted">Loading...</p>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><h5>Recent Receipts</h5></div>
                    <div class="card-body" id="recent-receipts" style="max-height: 400px; overflow-y: auto;">
                        <p class="text-muted">Loading...</p>
                    </div>
                </div>
            </div>
        </div>
    `);

    // Render patient search as a Frappe control
    var patient_field = frappe.ui.form.make_control({
        df: {
            fieldtype: 'Link',
            options: 'Patient',
            fieldname: 'patient',
            placeholder: 'Search by Patient Name or MRN',
            change: function() {
                var patient = patient_field.get_value();
                if (patient) {
                    load_patient_bills(patient);
                } else {
                    $('#pending-bills').html('<p class="text-muted">No patient selected</p>');
                    $('#patient-info').html('<span class="text-muted">Select a patient to view pending bills</span>');
                    $('#receipt-form-card').hide();
                }
            }
        },
        parent: $('#patient-search-field'),
        render_input: true
    });

    var selected_patient = null;
    var selected_bill = null;

    function load_patient_bills(patient) {
        selected_patient = patient;

        // Get patient info
        frappe.call({
            method: 'frappe.client.get',
            args: { doctype: 'Patient', name: patient },
            callback: function(r) {
                if (r.message) {
                    var p = r.message;
                    $('#patient-info').html(`
                        <strong>${p.patient_name}</strong><br>
                        <small>MRN: ${p.name} | ${p.gender || ''} | ${p.mobile_phone || ''}</small>
                    `);
                }
            }
        });

        // Get pending bills
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Sales Invoice',
                filters: {
                    patient: patient,
                    outstanding_amount: ['>', 0],
                    docstatus: 1
                },
                fields: ['name', 'posting_date', 'grand_total', 'outstanding_amount', 'due_date'],
                order_by: 'posting_date desc',
                limit_page_length: 50
            },
            callback: function(r) {
                if (!r.message || r.message.length === 0) {
                    $('#pending-bills').html('<p class="text-muted">No pending bills for this patient.</p>');
                    $('#receipt-form-card').hide();
                    return;
                }
                var html = '<table class="table table-sm table-hover"><thead><tr>' +
                    '<th>Invoice</th><th>Date</th><th>Total</th><th>Outstanding</th><th>Action</th>' +
                    '</tr></thead><tbody>';
                r.message.forEach(function(bill) {
                    html += `<tr>
                        <td><a href="/app/sales-invoice/${bill.name}">${bill.name}</a></td>
                        <td>${bill.posting_date}</td>
                        <td>${format_currency(bill.grand_total)}</td>
                        <td><strong>${format_currency(bill.outstanding_amount)}</strong></td>
                        <td>
                            <button class="btn btn-sm btn-success btn-pay-bill"
                                data-bill="${bill.name}" data-amount="${bill.outstanding_amount}">
                                <i class="fa fa-money"></i> Pay
                            </button>
                        </td>
                    </tr>`;
                });
                html += '</tbody></table>';
                $('#pending-bills').html(html);
            }
        });
    }

    // Handle pay button click
    $(page.main).on('click', '.btn-pay-bill', function() {
        selected_bill = $(this).data('bill');
        var amount = $(this).data('amount');
        $('#receipt-amount').val(amount);
        $('#payment-reference').val('');
        $('#receipt-form-card').show();
    });

    // Create receipt
    $(page.main).on('click', '#btn-create-receipt', function() {
        var amount = parseFloat($('#receipt-amount').val());
        var mode = $('#payment-mode').val();
        var reference = $('#payment-reference').val();

        if (!selected_patient || !amount || amount <= 0) {
            frappe.msgprint(__('Please select a patient and enter a valid amount.'));
            return;
        }

        frappe.call({
            method: 'frappe.client.insert',
            args: {
                doc: {
                    doctype: 'Payment Entry',
                    payment_type: 'Receive',
                    party_type: 'Customer',
                    party: selected_patient,
                    paid_amount: amount,
                    received_amount: amount,
                    mode_of_payment: mode,
                    reference_no: reference,
                    reference_date: frappe.datetime.get_today(),
                    references: selected_bill ? [{
                        reference_doctype: 'Sales Invoice',
                        reference_name: selected_bill,
                        allocated_amount: amount
                    }] : []
                }
            },
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint(__('Receipt {0} created successfully.', [r.message.name]));
                    $('#receipt-form-card').hide();
                    if (selected_patient) load_patient_bills(selected_patient);
                    load_collection_summary();
                    load_recent_receipts();
                }
            }
        });
    });

    function load_collection_summary() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Payment Entry',
                filters: {
                    posting_date: frappe.datetime.get_today(),
                    payment_type: 'Receive',
                    docstatus: 1
                },
                fields: ['mode_of_payment', 'paid_amount'],
                limit_page_length: 0
            },
            callback: function(r) {
                if (!r.message) {
                    $('#collection-summary').html('<p class="text-muted">No collections today</p>');
                    return;
                }
                var total = 0, cash = 0, card = 0, count = r.message.length;
                r.message.forEach(function(pe) {
                    total += pe.paid_amount;
                    if (pe.mode_of_payment === 'Cash') cash += pe.paid_amount;
                    else if (pe.mode_of_payment === 'Card') card += pe.paid_amount;
                });
                var html = `
                    <div class="mb-2"><strong>Total Collected:</strong> ${format_currency(total)}</div>
                    <div class="mb-2"><strong>Cash:</strong> ${format_currency(cash)}</div>
                    <div class="mb-2"><strong>Card:</strong> ${format_currency(card)}</div>
                    <div class="mb-2"><strong>Other:</strong> ${format_currency(total - cash - card)}</div>
                    <div><strong>Receipt Count:</strong> ${count}</div>
                `;
                $('#collection-summary').html(html);
            }
        });
    }

    function load_recent_receipts() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Payment Entry',
                filters: {
                    posting_date: frappe.datetime.get_today(),
                    payment_type: 'Receive'
                },
                fields: ['name', 'party_name', 'paid_amount', 'mode_of_payment', 'creation'],
                order_by: 'creation desc',
                limit_page_length: 20
            },
            callback: function(r) {
                if (!r.message || r.message.length === 0) {
                    $('#recent-receipts').html('<p class="text-muted">No receipts today</p>');
                    return;
                }
                var html = '';
                r.message.forEach(function(receipt) {
                    html += `
                        <div class="mb-2 p-2 border rounded">
                            <div class="d-flex justify-content-between">
                                <strong><a href="/app/payment-entry/${receipt.name}">${receipt.name}</a></strong>
                                <span class="badge bg-secondary">${receipt.mode_of_payment}</span>
                            </div>
                            <small>${receipt.party_name || '-'} | ${format_currency(receipt.paid_amount)}</small>
                        </div>
                    `;
                });
                $('#recent-receipts').html(html);
            }
        });
    }

    load_collection_summary();
    load_recent_receipts();
    setInterval(function() {
        load_collection_summary();
        load_recent_receipts();
    }, 60000);
};
