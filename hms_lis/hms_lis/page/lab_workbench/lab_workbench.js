frappe.pages['lab-workbench'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Lab Workbench',
        single_column: true
    });

    page.main.html(`
        <div class="lab-workbench">
            <div class="row mb-4">
                <div class="col-md-2"><div class="card text-center p-3"><h3 id="pending-collection">-</h3><small>Pending Collection</small></div></div>
                <div class="col-md-2"><div class="card text-center p-3"><h3 id="in-process">-</h3><small>In Process</small></div></div>
                <div class="col-md-2"><div class="card text-center p-3"><h3 id="result-entered">-</h3><small>Result Entered</small></div></div>
                <div class="col-md-2"><div class="card text-center p-3"><h3 id="pending-verify">-</h3><small>Pending Verify</small></div></div>
                <div class="col-md-2"><div class="card text-center p-3"><h3 id="pending-auth">-</h3><small>Pending Auth</small></div></div>
                <div class="col-md-2"><div class="card text-center p-3 bg-danger text-white"><h3 id="critical-count">-</h3><small>Critical Values</small></div></div>
            </div>
            <div id="lab-worklist"></div>
        </div>
    `);

    function load_stats() {
        var statuses = ['Ordered', 'In Process', 'Result Entered', 'Verified'];
        statuses.forEach(function(status) {
            frappe.call({
                method: 'frappe.client.get_count',
                args: { doctype: 'Lab Test', filters: { status: status } },
                callback: function(r) {
                    var id_map = { 'Ordered': 'pending-collection', 'In Process': 'in-process', 'Result Entered': 'result-entered', 'Verified': 'pending-auth' };
                    if (id_map[status]) $('#' + id_map[status]).text(r.message || 0);
                }
            });
        });
        frappe.call({
            method: 'frappe.client.get_count',
            args: { doctype: 'Lab Test', filters: { result_status: 'Critical', status: ['in', ['Result Entered', 'Verified', 'Authorized']] } },
            callback: function(r) { $('#critical-count').text(r.message || 0); }
        });
    }

    load_stats();
    setInterval(load_stats, 30000);
};
