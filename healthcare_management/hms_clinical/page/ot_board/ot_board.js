frappe.pages['ot-board'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'OT Board',
        single_column: true
    });

    // Date filter
    page.add_field({
        fieldname: 'procedure_date',
        label: __('Date'),
        fieldtype: 'Date',
        default: frappe.datetime.get_today(),
        change: function() {
            load_ot_board();
        }
    });

    // OT Room filter
    page.add_field({
        fieldname: 'ot_room',
        label: __('OT Room'),
        fieldtype: 'Link',
        options: 'OT Room',
        change: function() {
            load_ot_board();
        }
    });

    page.main.html(`
        <div id="ot-summary" class="mb-3"></div>
        <div id="ot-board-content"></div>
    `);

    function get_status_color(status) {
        switch (status) {
            case 'Scheduled': return 'primary';
            case 'In Progress': return 'warning';
            case 'Completed': return 'success';
            case 'Cancelled': return 'danger';
            default: return 'secondary';
        }
    }

    function load_ot_board() {
        var selected_date = page.fields_dict.procedure_date.get_value() || frappe.datetime.get_today();
        var filters = {
            procedure_date: selected_date
        };
        var ot_room_filter = page.fields_dict.ot_room.get_value();
        if (ot_room_filter) {
            filters.ot_room = ot_room_filter;
        }

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Surgical Procedure',
                filters: filters,
                fields: [
                    'name', 'patient_name', 'procedure_name', 'surgeon',
                    'anesthetist', 'ot_room', 'start_time', 'status',
                    'expected_duration'
                ],
                order_by: 'start_time asc',
                limit_page_length: 100
            },
            callback: function(r) {
                if (!r.message) return;
                var procedures = r.message;

                // Summary counts
                var counts = { Scheduled: 0, 'In Progress': 0, Completed: 0, Cancelled: 0 };
                procedures.forEach(function(p) {
                    if (counts.hasOwnProperty(p.status)) counts[p.status]++;
                });

                var summary_html = `
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card text-center border-primary">
                                <div class="card-body p-2">
                                    <h4 class="text-primary">${counts['Scheduled']}</h4>
                                    <small>Scheduled</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center border-warning">
                                <div class="card-body p-2">
                                    <h4 class="text-warning">${counts['In Progress']}</h4>
                                    <small>In Progress</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center border-success">
                                <div class="card-body p-2">
                                    <h4 class="text-success">${counts['Completed']}</h4>
                                    <small>Completed</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card text-center border-danger">
                                <div class="card-body p-2">
                                    <h4 class="text-danger">${counts['Cancelled']}</h4>
                                    <small>Cancelled</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#ot-summary').html(summary_html);

                if (procedures.length === 0) {
                    $('#ot-board-content').html('<p class="text-muted">No procedures scheduled for this date.</p>');
                    return;
                }

                var html = '';
                procedures.forEach(function(proc) {
                    var color = get_status_color(proc.status);
                    html += `
                        <div class="card mb-2 border-${color}">
                            <div class="card-body p-3">
                                <div class="row align-items-center">
                                    <div class="col-md-1 text-center">
                                        <strong>${proc.start_time || '--:--'}</strong>
                                    </div>
                                    <div class="col-md-3">
                                        <strong>${proc.patient_name}</strong><br>
                                        <small class="text-muted">${proc.procedure_name || '-'}</small>
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">Surgeon</small><br>
                                        ${proc.surgeon || '-'}
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">Anesthetist</small><br>
                                        ${proc.anesthetist || '-'}
                                    </div>
                                    <div class="col-md-2">
                                        <small class="text-muted">OT Room</small><br>
                                        ${proc.ot_room || '-'}
                                    </div>
                                    <div class="col-md-2 text-center">
                                        <span class="badge bg-${color}">${proc.status}</span>
                                        ${proc.expected_duration ? '<br><small class="text-muted">' + proc.expected_duration + ' mins</small>' : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                $('#ot-board-content').html(html);
            }
        });
    }

    load_ot_board();
    setInterval(load_ot_board, 30000);
};
