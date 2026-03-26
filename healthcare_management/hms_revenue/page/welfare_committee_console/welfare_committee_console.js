frappe.pages['welfare-committee-console'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Welfare Committee Console',
        single_column: true
    });

    // Category filter
    page.add_field({
        fieldname: 'category',
        label: __('Category'),
        fieldtype: 'Select',
        options: '\nZakat\nSadaqah\nGeneral',
        change: function() {
            load_welfare_cases();
        }
    });

    page.main.html(`
        <div id="welfare-summary" class="mb-3"></div>
        <div id="welfare-content"></div>
    `);

    function load_welfare_cases() {
        var filters = {
            approval_status: 'Pending'
        };
        var category_filter = page.fields_dict.category.get_value();
        if (category_filter) {
            filters.category = category_filter;
        }

        // Load summary stats in parallel
        load_summary_stats();

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Welfare Approval Request',
                filters: filters,
                fields: [
                    'name', 'patient', 'patient_name', 'case_type', 'category',
                    'requested_amount', 'social_assessment_summary', 'creation'
                ],
                order_by: 'creation asc',
                limit_page_length: 100
            },
            callback: function(r) {
                if (!r.message || r.message.length === 0) {
                    $('#welfare-content').html('<p class="text-muted">No pending welfare approval requests.</p>');
                    return;
                }

                var html = '<div class="row">';
                r.message.forEach(function(req) {
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <strong>${req.patient_name}</strong>
                                    <span class="badge bg-secondary">${req.category || req.case_type || '-'}</span>
                                </div>
                                <div class="card-body">
                                    <div class="row mb-2">
                                        <div class="col-md-6">
                                            <small class="text-muted">Patient ID</small><br>
                                            <span>${req.patient}</span>
                                        </div>
                                        <div class="col-md-6">
                                            <small class="text-muted">Case Type</small><br>
                                            <span>${req.case_type || '-'}</span>
                                        </div>
                                    </div>
                                    <div class="row mb-2">
                                        <div class="col-md-6">
                                            <small class="text-muted">Requested Amount</small><br>
                                            <strong>${format_currency(req.requested_amount)}</strong>
                                        </div>
                                        <div class="col-md-6">
                                            <small class="text-muted">Submitted</small><br>
                                            <span>${frappe.datetime.prettyDate(req.creation)}</span>
                                        </div>
                                    </div>
                                    <div class="mb-3">
                                        <small class="text-muted">Social Assessment Summary</small><br>
                                        <span>${req.social_assessment_summary || '-'}</span>
                                    </div>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <input type="number" class="form-control form-control-sm mb-1 approve-amount"
                                                data-request="${req.name}" placeholder="Approved Amount"
                                                value="${req.requested_amount || ''}">
                                        </div>
                                        <div class="col-md-6">
                                            <input type="text" class="form-control form-control-sm mb-1 approve-remarks"
                                                data-request="${req.name}" placeholder="Remarks">
                                        </div>
                                    </div>
                                    <div class="btn-group btn-group-sm mt-2">
                                        <button class="btn btn-success btn-approve-welfare"
                                            data-request="${req.name}">
                                            <i class="fa fa-check"></i> Approve
                                        </button>
                                        <button class="btn btn-danger btn-reject-welfare"
                                            data-request="${req.name}">
                                            <i class="fa fa-times"></i> Reject
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                $('#welfare-content').html(html);
            }
        });
    }

    function load_summary_stats() {
        // Pending cases
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'Welfare Approval Request',
                filters: { approval_status: 'Pending' }
            },
            callback: function(r) {
                var pending_count = r.message || 0;

                // Approved today
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Welfare Approval Request',
                        filters: {
                            approval_status: 'Approved',
                            modified: ['>=', frappe.datetime.get_today()]
                        },
                        fields: ['name', 'approved_amount'],
                        limit_page_length: 0
                    },
                    callback: function(r2) {
                        var approved_today = r2.message ? r2.message.length : 0;

                        // Total disbursed this month
                        var first_of_month = frappe.datetime.get_today().substring(0, 8) + '01';
                        frappe.call({
                            method: 'frappe.client.get_list',
                            args: {
                                doctype: 'Welfare Approval Request',
                                filters: {
                                    approval_status: 'Approved',
                                    modified: ['>=', first_of_month]
                                },
                                fields: ['approved_amount'],
                                limit_page_length: 0
                            },
                            callback: function(r3) {
                                var total_disbursed = 0;
                                if (r3.message) {
                                    r3.message.forEach(function(item) {
                                        total_disbursed += (item.approved_amount || 0);
                                    });
                                }

                                var summary_html = `
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="card text-center border-warning">
                                                <div class="card-body p-2">
                                                    <h4 class="text-warning">${pending_count}</h4>
                                                    <small>Pending Cases</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card text-center border-success">
                                                <div class="card-body p-2">
                                                    <h4 class="text-success">${approved_today}</h4>
                                                    <small>Approved Today</small>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card text-center border-info">
                                                <div class="card-body p-2">
                                                    <h4 class="text-info">${format_currency(total_disbursed)}</h4>
                                                    <small>Disbursed This Month</small>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                                $('#welfare-summary').html(summary_html);
                            }
                        });
                    }
                });
            }
        });
    }

    function process_welfare_action(request_name, action) {
        var amount_input = $(`.approve-amount[data-request="${request_name}"]`);
        var remarks_input = $(`.approve-remarks[data-request="${request_name}"]`);
        var approved_amount = parseFloat(amount_input.val()) || 0;
        var remarks = remarks_input.val() || '';

        if (action === 'Approved' && approved_amount <= 0) {
            frappe.msgprint(__('Please enter a valid approved amount.'));
            return;
        }

        frappe.call({
            method: 'frappe.client.set_value',
            args: {
                doctype: 'Welfare Approval Request',
                name: request_name,
                fieldname: {
                    approval_status: action,
                    approved_amount: action === 'Approved' ? approved_amount : 0,
                    remarks: remarks,
                    approved_by: frappe.session.user,
                    approval_date: frappe.datetime.get_today()
                }
            },
            callback: function(r) {
                if (r.message) {
                    frappe.show_alert({
                        message: __('Request {0} {1}.', [request_name, action.toLowerCase()]),
                        indicator: action === 'Approved' ? 'green' : 'red'
                    });
                    load_welfare_cases();
                }
            }
        });
    }

    // Button handlers
    $(page.main).on('click', '.btn-approve-welfare', function() {
        var request_name = $(this).data('request');
        frappe.confirm(
            __('Are you sure you want to approve this welfare request?'),
            function() {
                process_welfare_action(request_name, 'Approved');
            }
        );
    });

    $(page.main).on('click', '.btn-reject-welfare', function() {
        var request_name = $(this).data('request');
        frappe.confirm(
            __('Are you sure you want to reject this welfare request?'),
            function() {
                process_welfare_action(request_name, 'Rejected');
            }
        );
    });

    load_welfare_cases();
    setInterval(load_welfare_cases, 60000);
};
