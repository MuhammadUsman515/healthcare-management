from frappe import _

def get_data():
    return {
        "fieldname": "against_bill",
        "transactions": [
            {"label": _("Payments"), "items": ["Cashier Receipt", "Payment Entry", "Refund"]},
            {"label": _("Insurance"), "items": ["Claim Submission"]},
        ],
    }
