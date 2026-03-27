import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date
import hashlib
import os


class ResultDownloadToken(Document):
	def validate(self):
		self.validate_mandatory_fields()
		self.set_title_if_empty()

	def validate_mandatory_fields(self):
		if not self.patient:
			frappe.throw(_("Patient is required for a download token."))
		if not self.lab_test:
			frappe.throw(_("Lab Test is required for a download token."))

	def set_title_if_empty(self):
		if not self.title:
			self.title = f"Token - {self.patient} - {self.lab_test}"

	def before_insert(self):
		"""Generate a secure token on creation."""
		if not self.description:
			token = hashlib.sha256(os.urandom(32)).hexdigest()[:32]
			self.description = token
		if not self.date:
			self.date = now_datetime()

	def is_expired(self, expiry_hours=24):
		"""Check whether this token has expired."""
		if not self.date:
			return True
		expiry_time = add_to_date(self.date, hours=expiry_hours)
		return now_datetime() > expiry_time

	@frappe.whitelist()
	def consume(self):
		"""Consume the token (mark as used)."""
		if self.status == "Completed":
			frappe.throw(_("Token has already been used."))
		if self.is_expired():
			self.status = "Inactive"
			self.save()
			frappe.throw(_("Token has expired."))
		self.status = "Completed"
		self.save()

	@staticmethod
	def generate_token(patient, lab_test):
		"""Generate a new download token for a patient and lab test."""
		doc = frappe.new_doc("Result Download Token")
		doc.patient = patient
		doc.lab_test = lab_test
		doc.insert(ignore_permissions=True)
		return {"name": doc.name, "token": doc.description}

	@staticmethod
	def validate_token(token_value):
		"""Validate a token string and return the associated record if valid."""
		token_name = frappe.db.get_value(
			"Result Download Token",
			{"description": token_value, "status": "Active"},
			"name",
		)
		if not token_name:
			frappe.throw(_("Invalid or expired download token."))
		return frappe.get_doc("Result Download Token", token_name)
