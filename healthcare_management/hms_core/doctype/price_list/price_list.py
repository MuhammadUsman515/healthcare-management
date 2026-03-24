from frappe.model.document import Document


class PriceList(Document):
    def autoname(self):
        self.name = self.price_list_name
