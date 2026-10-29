"""
To'lov shlyuzi qatlami.

Hozir `DemoGateway` ishlaydi: Luhn tekshiruvidan o'tgan istalgan karta
raqami muvaffaqiyatli to'lov hisoblanadi. Haqiqiy Payme yoki Click
ulanganda shu yerga yangi klass qo'shiladi va PAYMENT_PROVIDER sozlamasi
o'zgartiriladi — view'lar o'zgarmaydi.
"""
import uuid
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone


@dataclass
class PaymentResult:
    ok: bool
    transaction_id: str = ""
    error: str = ""


class DemoGateway:
    name = "Demo"

    def charge(self, order, card_number, expiry):
        # Test uchun: 4000 0000 0000 0002 doim rad etiladi
        if card_number == "4000000000000002":
            return PaymentResult(ok=False, error="Bank to‘lovni rad etdi. Boshqa karta bilan urinib ko‘ring.")
        return PaymentResult(ok=True, transaction_id=f"DEMO-{uuid.uuid4().hex[:12].upper()}")


GATEWAYS = {"demo": DemoGateway}


def get_gateway():
    return GATEWAYS[settings.PAYMENT_PROVIDER]()


def mark_paid(order, transaction_id):
    order.is_paid = True
    order.paid_at = timezone.now()
    order.transaction_id = transaction_id
    order.status = order.Status.PAID
    order.save(update_fields=["is_paid", "paid_at", "transaction_id", "status"])
