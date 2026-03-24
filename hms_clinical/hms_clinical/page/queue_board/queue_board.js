frappe.pages['queue-board'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Queue Board',
        single_column: true
    });

    page.main.html(`
        <div class="queue-board-container">
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5>Waiting</h5>
                        </div>
                        <div class="card-body" id="waiting-queue"></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-warning text-white">
                            <h5>In Consultation</h5>
                        </div>
                        <div class="card-body" id="in-consultation-queue"></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5>Completed</h5>
                        </div>
                        <div class="card-body" id="completed-queue"></div>
                    </div>
                </div>
            </div>
        </div>
    `);

    function load_queue() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Appointment',
                filters: { appointment_date: frappe.datetime.get_today() },
                fields: ['name', 'patient_name', 'practitioner_name', 'status', 'token_number', 'appointment_time'],
                order_by: 'token_number asc',
                limit_page_length: 100
            },
            callback: function(r) {
                if (!r.message) return;
                var waiting = '', consulting = '', completed = '';
                r.message.forEach(function(apt) {
                    var card = `<div class="mb-2 p-2 border rounded">
                        <strong>#${apt.token_number || '-'}</strong> ${apt.patient_name}
                        <br><small>${apt.practitioner_name} | ${apt.appointment_time}</small>
                    </div>`;
                    if (apt.status === 'Checked In') waiting += card;
                    else if (apt.status === 'In Consultation') consulting += card;
                    else if (apt.status === 'Completed') completed += card;
                });
                $('#waiting-queue').html(waiting || '<p class="text-muted">No patients waiting</p>');
                $('#in-consultation-queue').html(consulting || '<p class="text-muted">None</p>');
                $('#completed-queue').html(completed || '<p class="text-muted">None yet</p>');
            }
        });
    }

    load_queue();
    setInterval(load_queue, 30000); // Refresh every 30s
};
