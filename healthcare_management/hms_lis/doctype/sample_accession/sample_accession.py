import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SampleAccession(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.validate_not_duplicate()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for sample accession."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for sample accession."))

	def validate_not_duplicate(self):
		if self.is_new():
			existing = frappe.db.exists(
				"Sample Accession",
				{"lab_test": self.lab_test, "patient": self.patient, "status": "Active"},
			)
			if existing:
				frappe.throw(
					_("An active accession already exists for this Lab Test and Patient.")
				)

	def set_title_if_empty(self):
		if not self.title:
			patient_name = frappe.db.get_value("Patient", self.patient, "patient_name") or self.patient
			self.title = f"Accession - {patient_name} - {self.lab_test}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@frappe.whitelist()
	def receive_sample(self):
		"""Mark sample as received in the lab."""
		if self.status != "Active":
			frappe.throw(_("Only active accessions can receive samples."))
		self.status = "Completed"
		self.description = (
			(self.description or "")
			+ f"\nSample received by {frappe.session.user} at {now_datetime()}"
		)
		self.save()
		frappe.msgprint(_("Sample received and accession completed."))

	@frappe.whitelist()
	def reject_sample(self):
		"""Reject the sample and create a Sample Rejection record."""
		self.status = "Inactive"
		self.save()
		rejection = frappe.new_doc("Sample Rejection")
		rejection.patient = self.patient
		rejection.lab_test = self.lab_test
		rejection.description = f"Rejected during accession {self.name}"
		rejection.insert()
		frappe.msgprint(_("Sample rejected. Rejection record {0} created.").format(rejection.name))
		return rejection.name
