import re

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

