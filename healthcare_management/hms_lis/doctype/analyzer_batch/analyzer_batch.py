import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class AnalyzerBatch(Document):
	def validate(self):
		self.set_title_if_empty()

	def set_title_if_empty(self):
		if not self.title:
			self.title = f"Batch - {frappe.utils.formatdate(self.date or now_datetime(), 'yyyy-MM-dd')}"

	def before_save(self):
		if not self.date:
			self.date = now_datetime()

	@frappe.whitelist()
	def start_batch(self):
		"""Start processing this analyzer batch."""
		if self.status != "Active":
			frappe.throw(_("Only active batches can be started."))
		self.description = (
			(self.description or "")
			+ f"\nBatch started by {frappe.session.user} at {now_datetime()}"
		)
		self.save()
		frappe.msgprint(_("Analyzer batch started."))

	@frappe.whitelist()
	def complete_batch(self):
		"""Mark batch as completed."""
		if self.status == "Completed":
			frappe.throw(_("Batch is already completed."))
		self.status = "Completed"
		self.description = (
			(self.description or "")
			+ f"\nBatch completed by {frappe.session.user} at {now_datetime()}"
		)
		self.save()
		frappe.msgprint(_("Analyzer batch completed."))

	@staticmethod
	def get_active_batches():
		"""Get all active analyzer batches."""
		return frappe.get_all(
			"Analyzer Batch",
			filters={"status": "Active"},
			fields=["name", "title", "date", "description"],
			order_by="date desc",
		)
