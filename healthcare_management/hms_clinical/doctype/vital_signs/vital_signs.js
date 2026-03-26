// Copyright (c) 2024, HMS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vital Signs', {
    refresh(frm) {
        // Show previous vitals for comparison
        if (frm.doc.patient && !frm.is_new()) {
            vital_signs_show_previous(frm);
        }

        // Highlight abnormal values
        vital_signs_highlight_abnormals(frm);
    },

    height(frm) {
        vital_signs_calculate_bmi(frm);
    },

    weight(frm) {
        vital_signs_calculate_bmi(frm);
    },

    temperature(frm) {
        vital_signs_highlight_abnormals(frm);
    },

    systolic_bp(frm) {
        vital_signs_highlight_abnormals(frm);
    },

    diastolic_bp(frm) {
        vital_signs_highlight_abnormals(frm);
    },

    heart_rate(frm) {
        vital_signs_highlight_abnormals(frm);
    },

    respiratory_rate(frm) {
        vital_signs_highlight_abnormals(frm);
    },

    oxygen_saturation(frm) {
        vital_signs_highlight_abnormals(frm);
    }
});

function vital_signs_calculate_bmi(frm) {
    let height = frm.doc.height; // in cm
    let weight = frm.doc.weight; // in kg

    if (height && weight && height > 0) {
        let height_m = height / 100;
        let bmi = weight / (height_m * height_m);
        frm.set_value('bmi', flt(bmi, 1));

        let category = '';
        if (bmi < 18.5) category = 'Underweight';
        else if (bmi < 25) category = 'Normal';
        else if (bmi < 30) category = 'Overweight';
        else category = 'Obese';

        frm.set_value('bmi_category', category);
    }
}

function vital_signs_highlight_abnormals(frm) {
    let alerts = [];

    // Temperature > 38C (fever)
    if (frm.doc.temperature && frm.doc.temperature > 38) {
        alerts.push(__('Fever: {0}°C', [frm.doc.temperature]));
        frm.get_field('temperature').$wrapper.addClass('has-error');
    } else if (frm.doc.temperature && frm.doc.temperature < 35) {
        alerts.push(__('Hypothermia: {0}°C', [frm.doc.temperature]));
        frm.get_field('temperature').$wrapper.addClass('has-error');
    } else if (frm.doc.temperature) {
        frm.get_field('temperature').$wrapper.removeClass('has-error');
    }

    // Blood Pressure > 140/90
    if (frm.doc.systolic_bp && frm.doc.systolic_bp > 140) {
        alerts.push(__('High Systolic BP: {0} mmHg', [frm.doc.systolic_bp]));
        frm.get_field('systolic_bp').$wrapper.addClass('has-error');
    } else if (frm.doc.systolic_bp && frm.doc.systolic_bp < 90) {
        alerts.push(__('Low Systolic BP: {0} mmHg', [frm.doc.systolic_bp]));
        frm.get_field('systolic_bp').$wrapper.addClass('has-error');
    } else if (frm.doc.systolic_bp) {
        frm.get_field('systolic_bp').$wrapper.removeClass('has-error');
    }

    if (frm.doc.diastolic_bp && frm.doc.diastolic_bp > 90) {
        alerts.push(__('High Diastolic BP: {0} mmHg', [frm.doc.diastolic_bp]));
        frm.get_field('diastolic_bp').$wrapper.addClass('has-error');
    } else if (frm.doc.diastolic_bp && frm.doc.diastolic_bp < 60) {
        alerts.push(__('Low Diastolic BP: {0} mmHg', [frm.doc.diastolic_bp]));
        frm.get_field('diastolic_bp').$wrapper.addClass('has-error');
    } else if (frm.doc.diastolic_bp) {
        frm.get_field('diastolic_bp').$wrapper.removeClass('has-error');
    }

    // Heart Rate
    if (frm.doc.heart_rate && frm.doc.heart_rate > 100) {
        alerts.push(__('Tachycardia: {0} bpm', [frm.doc.heart_rate]));
        frm.get_field('heart_rate').$wrapper.addClass('has-error');
    } else if (frm.doc.heart_rate && frm.doc.heart_rate < 60) {
        alerts.push(__('Bradycardia: {0} bpm', [frm.doc.heart_rate]));
        frm.get_field('heart_rate').$wrapper.addClass('has-error');
    } else if (frm.doc.heart_rate) {
        frm.get_field('heart_rate').$wrapper.removeClass('has-error');
    }

    // Respiratory Rate
    if (frm.doc.respiratory_rate && frm.doc.respiratory_rate > 20) {
        alerts.push(__('Tachypnea: {0}/min', [frm.doc.respiratory_rate]));
        frm.get_field('respiratory_rate').$wrapper.addClass('has-error');
    } else if (frm.doc.respiratory_rate && frm.doc.respiratory_rate < 12) {
        alerts.push(__('Bradypnea: {0}/min', [frm.doc.respiratory_rate]));
        frm.get_field('respiratory_rate').$wrapper.addClass('has-error');
    } else if (frm.doc.respiratory_rate) {
        frm.get_field('respiratory_rate').$wrapper.removeClass('has-error');
    }

    // Oxygen Saturation
    if (frm.doc.oxygen_saturation && frm.doc.oxygen_saturation < 95) {
        alerts.push(__('Low SpO2: {0}%', [frm.doc.oxygen_saturation]));
        frm.get_field('oxygen_saturation').$wrapper.addClass('has-error');
    } else if (frm.doc.oxygen_saturation) {
        frm.get_field('oxygen_saturation').$wrapper.removeClass('has-error');
    }

    if (alerts.length) {
        frm.set_intro(
            '<strong>' + __('Abnormal Values') + ':</strong> ' + alerts.join(' | '),
            'red'
        );
    }
}

function vital_signs_show_previous(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Vital Signs',
            filters: {
                patient: frm.doc.patient,
                name: ['!=', frm.doc.name]
            },
            fields: [
                'name', 'signs_date', 'temperature', 'systolic_bp', 'diastolic_bp',
                'heart_rate', 'respiratory_rate', 'oxygen_saturation', 'weight'
            ],
            order_by: 'signs_date desc',
            limit_page_length: 3
        },
        callback(r) {
            if (r.message && r.message.length) {
                let html = '<div class="frappe-card p-3 mb-3">';
                html += '<h6 class="text-muted">' + __('Previous Vitals') + '</h6>';
                html += '<table class="table table-sm table-bordered mb-0"><thead><tr>';
                html += '<th>' + __('Date') + '</th><th>' + __('Temp') + '</th>';
                html += '<th>' + __('BP') + '</th><th>' + __('HR') + '</th>';
                html += '<th>' + __('RR') + '</th><th>' + __('SpO2') + '</th>';
                html += '</tr></thead><tbody>';

                r.message.forEach(v => {
                    html += '<tr>';
                    html += '<td><a href="/app/vital-signs/' + v.name + '">' + frappe.datetime.str_to_user(v.signs_date) + '</a></td>';
                    html += '<td>' + (v.temperature || '-') + '</td>';
                    html += '<td>' + (v.systolic_bp ? v.systolic_bp + '/' + (v.diastolic_bp || '-') : '-') + '</td>';
                    html += '<td>' + (v.heart_rate || '-') + '</td>';
                    html += '<td>' + (v.respiratory_rate || '-') + '</td>';
                    html += '<td>' + (v.oxygen_saturation || '-') + '</td>';
                    html += '</tr>';
                });

                html += '</tbody></table></div>';
                $(frm.layout.wrapper).find('.form-layout').prepend(html);
            }
        }
    });
}
