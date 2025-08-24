from dataclasses import dataclass
from datetime import datetime
from app.services.emailer import send_invoice_email, render_invoice_html

@dataclass
class Invoice:
    order_id: int
    invoice_number: str
    subtotal: float
    tax_rate: float
    total: float
    created_at: datetime

def send_invoice(order, to_email: str, subtotal: float, tax_rate: float = 0.08):
    total = round(subtotal * (1 + tax_rate), 2)
    inv = Invoice(order_id=order.id, invoice_number=f"INV-{order.id:06d}", subtotal=subtotal, tax_rate=tax_rate, total=total, created_at=datetime.utcnow())
    html = render_invoice_html(order=order, invoice=inv)
    send_invoice_email(to_email, f"Invoice {inv.invoice_number}", html)
    return inv
