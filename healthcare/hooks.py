app_name = "healthcare"
app_title = "Healthcare"
app_publisher = "Healthcare Team"
app_description = "Healthcare Management System built on Frappe/ERPNext"
app_email = "healthcare@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/healthcare/css/healthcare.css"
# app_include_js = "/assets/healthcare/js/healthcare.js"

# include js, css files in header of web template
# web_include_css = "/assets/healthcare/css/healthcare.css"
# web_include_js = "/assets/healthcare/js/healthcare.js"

# Installation
# ------------

# before_install = "healthcare.install.before_install"
# after_install = "healthcare.install.after_install"

# Fixtures
# --------

fixtures = []

# DocType Class
# -------------

# Override standard doctype classes
# override_doctype_class = {
#     "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------

doc_events = {
    "Patient": {
        "after_insert": "healthcare.healthcare.doctype.patient.patient.after_insert",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "daily": [
    #     "healthcare.tasks.daily"
    # ],
}

# Jinja
# -----

# Add methods and filters to jinja environment
# jinja = {
#     "methods": "healthcare.utils.jinja_methods",
#     "filters": "healthcare.utils.jinja_filters"
# }
