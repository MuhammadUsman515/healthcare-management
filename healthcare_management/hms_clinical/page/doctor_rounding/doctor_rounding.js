frappe.pages['doctor-rounding'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Doctor Rounding',
        single_column: true
    });

    // Ward filter
    page.add_field({
        fieldname: 'ward',
        label: __('Ward'),
        fieldtype: 'Link',
        options: 'Ward',
        change: function() {
            load_rounding_list();
        }
    });

    page.main.html(`
        <div id="rounding-summary" class="mb-3"></div>
        <div id="rounding-content"></div>
    `);

    function load_rounding_list() {
        var filters = {
            attending_practitioner: frappe.session.user,
            status: 'Admitted'
        };
        var ward_filter = page.fields_dict.ward.get_value();
        if (ward_filter) {
            filters.ward = ward_filter;
        }

        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Inpatient Record',
                filters: filters,
                fields: [
                    'name', 'patient', 'patient_name', 'ward', 'bed',
                    'admission_date', 'diagnosis', 'status'
                ],
                order_by: 'ward asc, bed asc',
                limit_page_length: 100
            },
            callback: function(r) {
                if (!r.message) return;
                var patients = r.message;

                // Summary
                var summary_html = `
                    <div class="row">
                        <div class="col-md-3">
                            <div class="card text-center">
                                <div class="card-body p-2">
                                    <h4>${patients.length}</h4>
                                    <small class="text-muted">Total Patients</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                $('#rounding-summary').html(summary_html);

                if (patients.length === 0) {
                    $('#rounding-content').html('<p class="text-muted">No admitted patients found for rounding.</p>');
                    return;
                }

                var html = '<div class="row">';
                patients.forEach(function(patient) {
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <strong>${patient.patient_name}</strong>
                                    <span class="badge bg-info">${patient.ward || ''} - ${patient.bed || ''}</span>
                                </div>
                                <div class="card-body">
                                    <div class="row mb-2">
                                        <div class="col-md-6">
                                            <small class="text-muted">Patient ID</small><br>
                                            <span>${patient.patient}</span>
                                        </div>
                                        <div class="col-md-6">
                                            <small class="text-muted">Admission Date</small><br>
                                            <span>${patient.admission_date || '-'}</span>
                                        </div>
                                    </div>
                                    <div class="mb-2">
                                        <small class="text-muted">Diagnosis</small><br>
                                        <span>${patient.diagnosis || '-'}</span>
                                    </div>
                                    <div class="mb-2" id="vitals-${patient.name}">
                                        <small class="text-muted">Last Vitals</small><br>
                                        <span class="text-muted">Loading...</span>
                                    </div>
                                    <div class="btn-group btn-group-sm mt-2">
                                        <button class="btn btn-primary btn-add-progress-note"
                                            data-patient="${patient.patient}" data-inpatient="${patient.name}">
                                            <i class="fa fa-file-text"></i> Progress Note
                                        </button>
                                        <button class="btn btn-warning btn-order-lab"
                                            data-patient="${patient.patient}">
                                            <i class="fa fa-flask"></i> Order Lab
                                        </button>
                                        <button class="btn btn-info btn-view-chart"
                                            data-patient="${patient.patient}">
                                            <i class="fa fa-folder-open"></i> View Chart
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                $('#rounding-content').html(html);

                // Load last vitals for each patient
                patients.forEach(function(patient) {
                    frappe.call({
                        method: 'frappe.client.get_list',
                        args: {
                            doctype: 'Vital Signs',
                            filters: { patient: patient.patient },
                            fields: ['temperature', 'pulse', 'blood_pressure', 'respiratory_rate', 'oxygen_saturation', 'creation'],
                            order_by: 'creation desc',
                            limit_page_length: 1
                        },
                        callback: function(v) {
                            var vitals_html = '';
                            if (v.message && v.message.length > 0) {
                                var vs = v.message[0];
                                vitals_html = `
                                    <small class="text-muted">Last Vitals (${frappe.datetime.prettyDate(vs.creation)})</small><br>
                                    <span>
                                        Temp: ${vs.temperature || '-'}
                                        | Pulse: ${vs.pulse || '-'}
                                        | BP: ${vs.blood_pressure || '-'}
                                        | RR: ${vs.respiratory_rate || '-'}
                                        | SpO2: ${vs.oxygen_saturation || '-'}
                                    </span>
                                `;
                            } else {
                                vitals_html = '<small class="text-muted">Last Vitals</small><br><span class="text-muted">No vitals recorded</span>';
                            }
                            $(`#vitals-${patient.name}`).html(vitals_html);
                        }
                    });
                });
            }
        });
    }

    // Button handlers
    $(page.main).on('click', '.btn-add-progress-note', function() {
        var patient = $(this).data('patient');
        var inpatient = $(this).data('inpatient');
        frappe.new_doc('Progress Note', {
            patient: patient,
            inpatient_record: inpatient
        });
    });

    $(page.main).on('click', '.btn-order-lab', function() {
        var patient = $(this).data('patient');
        frappe.new_doc('Lab Test', {
            patient: patient
        });
    });

    $(page.main).on('click', '.btn-view-chart', function() {
        var patient = $(this).data('patient');
        frappe.set_route('patient-chart', patient);
    });

    load_rounding_list();
    setInterval(load_rounding_list, 60000);
};
