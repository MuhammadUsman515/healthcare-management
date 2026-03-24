frappe.pages['bed-board'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Bed Board',
        single_column: true
    });

    page.main.html('<div id="bed-board-content"></div>');

    function load_bed_board() {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Ward',
                filters: { is_active: 1 },
                fields: ['name', 'ward_name', 'ward_type', 'total_beds'],
                order_by: 'ward_name'
            },
            callback: function(r) {
                if (!r.message) return;
                var html = '';
                r.message.forEach(function(ward) {
                    html += `<div class="card mb-3">
                        <div class="card-header">
                            <h5>${ward.ward_name} <span class="badge bg-info">${ward.ward_type}</span></h5>
                        </div>
                        <div class="card-body" id="ward-${ward.name}">
                            <p class="text-muted">Loading beds...</p>
                        </div>
                    </div>`;
                });
                $('#bed-board-content').html(html);

                r.message.forEach(function(ward) {
                    frappe.call({
                        method: 'frappe.client.get_list',
                        args: {
                            doctype: 'Bed',
                            filters: { ward: ward.name },
                            fields: ['name', 'bed_name', 'status', 'current_patient'],
                            order_by: 'bed_name'
                        },
                        callback: function(beds) {
                            var beds_html = '<div class="row">';
                            (beds.message || []).forEach(function(bed) {
                                var color = bed.status === 'Available' ? 'success' :
                                           bed.status === 'Occupied' ? 'danger' :
                                           bed.status === 'Reserved' ? 'warning' : 'secondary';
                                beds_html += `<div class="col-md-2 mb-2">
                                    <div class="card text-center border-${color}">
                                        <div class="card-body p-2">
                                            <strong>${bed.bed_name}</strong><br>
                                            <span class="badge bg-${color}">${bed.status}</span>
                                            ${bed.current_patient ? '<br><small>' + bed.current_patient + '</small>' : ''}
                                        </div>
                                    </div>
                                </div>`;
                            });
                            beds_html += '</div>';
                            $(`#ward-${ward.name}`).html(beds_html);
                        }
                    });
                });
            }
        });
    }

    load_bed_board();
    setInterval(load_bed_board, 60000);
};
