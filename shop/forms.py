import re
from datetime import date

from django import forms

from .models import Order

PHONE_RE = re.compile(r"^\+?998\d{9}$")


class CheckoutForm(forms.ModelForm):
    # Modelda ixtiyoriy (olib ketishda kerak emas), lekin yetkazishda majburiy
    delivery_required = {"city", "street", "house"}

    class Meta:
        model = Order
        fields = [
            "full_name", "phone", "email",
            "region", "city", "street", "house", "apartment", "landmark", "note",
            "delivery_method", "payment_method",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Aziz Karimov"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "inputmode": "tel",
                                            "placeholder": "+998 90 123 45 67"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "Ixtiyoriy"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2", "placeholder": "Yunusobod tumani"}),
            "street": forms.TextInput(attrs={"autocomplete": "address-line1",
                                             "placeholder": "Amir Temur ko‘chasi, Bodomzor mahallasi"}),
            "house": forms.TextInput(attrs={"placeholder": "12"}),
            "apartment": forms.TextInput(attrs={"placeholder": "45"}),
            "landmark": forms.TextInput(attrs={"placeholder": "Maktab ro‘parasida"}),
            "note": forms.Textarea(attrs={"rows": 2, "placeholder": "Domofon kodi, qo‘ng‘iroq qilish vaqti…"}),
            "delivery_method": forms.RadioSelect,
            "payment_method": forms.RadioSelect,
        }

    def clean_phone(self):
        raw = re.sub(r"[^\d+]", "", self.cleaned_data["phone"])
        if raw.startswith("998"):
            raw = "+" + raw
        elif len(raw) == 9:
            raw = "+998" + raw
        if not PHONE_RE.match(raw):
            raise forms.ValidationError("Raqamni +998 90 123 45 67 ko‘rinishida kiriting.")
        return raw

    def clean(self):
        data = super().clean()
        if data.get("delivery_method") != Order.Delivery.PICKUP:
            for field in ("city", "street", "house"):
                if not data.get(field):
                    self.add_error(field, "Yetkazib berish uchun bu maydon kerak.")
        if (data.get("delivery_method") == Order.Delivery.COURIER
                and data.get("region") not in (Order.Region.TASHKENT_CITY, Order.Region.TASHKENT)):
            self.add_error("delivery_method",
                           "Kuryer faqat Toshkent shahri va viloyatiga boradi. Viloyatlar uchun pochtani tanlang.")
        return data


def luhn_ok(number):
    digits = [int(d) for d in number][::-1]
    total = sum(digits[0::2]) + sum(sum(divmod(d * 2, 10)) for d in digits[1::2])
    return total % 10 == 0


class CardPaymentForm(forms.Form):
    """Demo to‘lov shakli. Karta ma’lumotlari hech qayerda saqlanmaydi."""

    number = forms.CharField(label="Karta raqami", max_length=23, widget=forms.TextInput(attrs={
        "inputmode": "numeric", "autocomplete": "cc-number", "placeholder": "8600 1234 5678 9012"}))
    expiry = forms.CharField(label="Amal qilish muddati", max_length=5, widget=forms.TextInput(attrs={
        "inputmode": "numeric", "autocomplete": "cc-exp", "placeholder": "OO/YY"}))

    def clean_number(self):
        number = re.sub(r"\D", "", self.cleaned_data["number"])
        if len(number) != 16 or not luhn_ok(number):
            raise forms.ValidationError("Karta raqami noto‘g‘ri. 16 ta raqamni tekshirib qayta kiriting.")
        return number

    def clean_expiry(self):
        m = re.match(r"^(\d{2})\s*/?\s*(\d{2})$", self.cleaned_data["expiry"])
        if not m or not 1 <= int(m.group(1)) <= 12:
            raise forms.ValidationError("Muddatni OO/YY ko‘rinishida kiriting, masalan 08/28.")
        month, year = int(m.group(1)), 2000 + int(m.group(2))
        today = date.today()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError("Bu kartaning muddati tugagan.")
        return f"{month:02d}/{year % 100:02d}"
