import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class CriticalValueAlert(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a critical value alert."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for a critical value alert."))
		if not self.description:
			frappe.throw(_("Description of the critical value is required."))

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"CRITICAL - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	def after_insert(self):
		self.send_alert()

	def send_alert(self):
		"""Send real-time alert and email notification for critical values."""
		frappe.publish_realtime(
			"critical_value_alert",
			{
				"name": self.name,
				"patient": self.patient,
				"lab_test": self.lab_test,
				"description": self.description,
			},
			after_commit=True,
		)
		self.notify_practitioners()

	def notify_practitioners(self):
		"""Notify healthcare practitioners linked to the patient."""
		practitioners = frappe.get_all(
			"Patient Appointment",
			filters={"patient": self.patient, "status": ["!=", "Cancelled"]},
			fields=["practitioner"],
			distinct=True,
			limit=5,
		)
		for p in practitioners:
			if p.practitioner:
				email = frappe.db.get_value("Healthcare Practitioner", p.practitioner, "email")
				if email:
					frappe.sendmail(
						recipients=[email],
						subject=_("Critical Lab Value Alert: {0}").format(self.patient),
						message=_(
							"Critical value detected for {0} on test {1}.\n\n{2}"
						).format(self.patient, self.lab_test, self.description),
						now=True,
					)

	@frappe.whitelist()
	def acknowledge(self):
		"""Acknowledge the alert."""
		if self.status == "Completed":
			frappe.throw(_("Alert has already been acknowledged."))
		self.status = "Completed"
		self.description = (
			(self.description or "")
			+ f"\nAcknowledged by {frappe.session.user} at {now_datetime()}"
		)
		self.save()
		frappe.msgprint(_("Critical value alert acknowledged."))

	@staticmethod
	def get_unacknowledged(patient=None):
		"""Get all active (unacknowledged) critical value alerts."""
		filters = {"status": "Active"}
		if patient:
			filters["patient"] = patient
		return frappe.get_all(
			"Critical Value Alert",
			filters=filters,
			fields=["name", "title", "patient", "lab_test", "date", "description"],
			order_by="date desc",
		)
