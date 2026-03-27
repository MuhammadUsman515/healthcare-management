import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class LabWorklist(Document):
	def validate(self):
		self.set_title_if_empty()

	def set_title_if_empty(self):
		if not self.title:
			parts = [frappe.utils.formatdate(self.date or now_datetime(), "yyyy-MM-dd")]
			if self.lab_test:
				parts.append(self.lab_test)
			self.title = "Worklist - " + " - ".join(parts)

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@frappe.whitelist()
	def mark_completed(self):
		"""Mark all items in worklist as completed."""
		if self.status == "Completed":
			frappe.throw(_("Worklist is already completed."))
		self.status = "Completed"
		self.save()
		frappe.msgprint(_("Worklist marked as completed."))

	@staticmethod
	def get_active_worklists(lab_test=None):
		"""Retrieve active worklists, optionally filtered by lab test."""
		filters = {"status": "Active"}
		if lab_test:
			filters["lab_test"] = lab_test
		return frappe.get_all(
			"Lab Worklist",
			filters=filters,
			fields=["name", "title", "patient", "lab_test", "date", "status"],
			order_by="date desc",
		)

	@staticmethod
	def get_pending_count():
		"""Return count of active worklist entries."""
		return frappe.db.count("Lab Worklist", {"status": "Active"})
