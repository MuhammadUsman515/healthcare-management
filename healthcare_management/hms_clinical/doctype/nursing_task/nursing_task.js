frappe.ui.form.on("Nursing Task", {
    refresh(frm) {
        if (frm.doc.status === "Pending") {
            frm.add_custom_button(__("Start"), () => {
                frm.set_value("status", "In Progress");
                frm.save();
            }, __("Actions"));
        }
        if (["Pending", "In Progress"].includes(frm.doc.status)) {
            frm.add_custom_button(__("Complete"), () => {
                let d = new frappe.ui.Dialog({
                    title: __("Complete Task"),
                    fields: [
                        { fieldname: "notes", fieldtype: "Small Text", label: __("Completion Notes") },
                    ],
                    primary_action_label: __("Complete"),
                    primary_action(values) {
                        frm.set_value("status", "Completed");
                        frm.set_value("completed_datetime", frappe.datetime.now_datetime());
                        if (values.notes) {
                            frm.set_value("completion_notes", values.notes);
                        }
                        frm.save();
                        d.hide();
                    },
                });
                d.show();
            }, __("Actions"));
        }

        // Color indicator based on priority
        if (frm.doc.priority === "Urgent") {
            frm.set_indicator_formatter("priority", (doc) => "red");
        }
    },

    status(frm) {
        if (frm.doc.status === "Completed" && !frm.doc.completed_datetime) {
            frm.set_value("completed_datetime", frappe.datetime.now_datetime());
        }
    },
});
