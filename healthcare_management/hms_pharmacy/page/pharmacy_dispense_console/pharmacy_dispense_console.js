frappe.pages['pharmacy-dispense-console'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Pharmacy Dispense Console',
        single_column: true
    });

    page.main.html(`
        <div class="dispense-console">
            <div class="row mb-3">
                <div class="col-md-3"><div class="card text-center p-3 bg-warning"><h3 id="pending-rx">-</h3><small>Pending Prescriptions</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3"><h3 id="partial-dispense">-</h3><small>Partial Dispenses</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3 bg-info text-white"><h3 id="today-sales">-</h3><small>Today's Sales</small></div></div>
                <div class="col-md-3"><div class="card text-center p-3 bg-danger text-white"><h3 id="near-expiry">-</h3><small>Near Expiry Items</small></div></div>
            </div>
            <h5>Pending Prescriptions Queue</h5>
            <div id="prescription-queue"></div>
        </div>
    `);

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Prescription',
            filters: { status: 'Sent to Pharmacy', docstatus: 1 },
            fields: ['name', 'patient_name', 'practitioner', 'prescription_date'],
            order_by: 'prescription_date desc',
            limit_page_length: 20
        },
        callback: function(r) {
            var html = '<table class="table table-bordered"><thead><tr><th>Rx#</th><th>Patient</th><th>Doctor</th><th>Date</th><th>Action</th></tr></thead><tbody>';
            (r.message || []).forEach(function(rx) {
                html += `<tr>
                    <td><a href="/app/prescription/${rx.name}">${rx.name}</a></td>
                    <td>${rx.patient_name}</td>
                    <td>${rx.practitioner}</td>
                    <td>${rx.prescription_date}</td>
                    <td><button class="btn btn-sm btn-primary" onclick="frappe.set_route('app/dispense-slip/new', {prescription: '${rx.name}'})">Dispense</button></td>
                </tr>`;
            });
            html += '</tbody></table>';
            $('#prescription-queue').html(html);
        }
    });
};
