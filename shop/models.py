import uuid

from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField("Nomi", max_length=80)
    slug = models.SlugField(unique=True)
    description = models.CharField("Qisqa tavsif", max_length=200, blank=True)
    order = models.PositiveSmallIntegerField("Tartib", default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:catalog") + f"?category={self.slug}"


class Book(models.Model):
    class Language(models.TextChoices):
        UZ = "uz", "O‘zbekcha"
        RU = "ru", "Ruscha"
        EN = "en", "Inglizcha"

    class Cover(models.TextChoices):
        SOFT = "soft", "Yumshoq muqova"
        HARD = "hard", "Qattiq muqova"

    title = models.CharField("Nomi", max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    author = models.CharField("Muallif", max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="books", verbose_name="Kategoriya"
    )
    description = models.TextField("Tavsif", blank=True)
    price = models.PositiveIntegerField("Narxi (so‘m)")
    old_price = models.PositiveIntegerField("Eski narxi (so‘m)", null=True, blank=True)
    pages = models.PositiveIntegerField("Sahifalar", default=0)
    year = models.PositiveSmallIntegerField("Nashr yili", null=True, blank=True)
    language = models.CharField("Til", max_length=2, choices=Language.choices, default=Language.UZ)
    cover_type = models.CharField("Muqova", max_length=4, choices=Cover.choices, default=Cover.SOFT)
    cover_color = models.CharField("Muqova rangi", max_length=7, default="#1D3A6E")
    accent_color = models.CharField("Bezak rangi", max_length=7, default="#E8A317")
    stock = models.PositiveIntegerField("Omborda", default=10)
    rating = models.DecimalField("Reyting", max_digits=2, decimal_places=1, default=4.5)
    is_featured = models.BooleanField("Tavsiya etiladi", default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"

    def __str__(self):
        return f"{self.title} — {self.author}"

    def get_absolute_url(self):
        return reverse("shop:book_detail", args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) * 100 / self.old_price)
        return 0


class Order(models.Model):
    class Region(models.TextChoices):
        TASHKENT_CITY = "toshkent_sh", "Toshkent shahri"
        TASHKENT = "toshkent_v", "Toshkent viloyati"
        ANDIJAN = "andijon", "Andijon viloyati"
        BUKHARA = "buxoro", "Buxoro viloyati"
        FERGANA = "fargona", "Farg‘ona viloyati"
        JIZZAKH = "jizzax", "Jizzax viloyati"
        KASHKADARYA = "qashqadaryo", "Qashqadaryo viloyati"
        KHOREZM = "xorazm", "Xorazm viloyati"
        NAMANGAN = "namangan", "Namangan viloyati"
        NAVOI = "navoiy", "Navoiy viloyati"
        SAMARKAND = "samarqand", "Samarqand viloyati"
        SURKHANDARYA = "surxondaryo", "Surxondaryo viloyati"
        SYRDARYA = "sirdaryo", "Sirdaryo viloyati"
        KARAKALPAKSTAN = "qoraqalpogiston", "Qoraqalpog‘iston Respublikasi"

    class Delivery(models.TextChoices):
        COURIER = "courier", "Kuryer orqali"
        POST = "post", "Pochta orqali"
        PICKUP = "pickup", "Do‘kondan olib ketish"

    class Payment(models.TextChoices):
        CARD = "card", "Karta orqali onlayn"
        CASH = "cash", "Qabul qilganda naqd"

    class Status(models.TextChoices):
        NEW = "new", "Qabul qilindi"
        PAID = "paid", "To‘landi"
        PACKING = "packing", "Yig‘ilmoqda"
        SHIPPED = "shipped", "Yo‘lda"
        DELIVERED = "delivered", "Yetkazildi"
        CANCELLED = "cancelled", "Bekor qilindi"

    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    # Mijoz
    full_name = models.CharField("Ism va familiya", max_length=120)
    phone = models.CharField("Telefon", max_length=20)
    email = models.EmailField("Email", blank=True)

    # Yashash manzili
    region = models.CharField("Viloyat", max_length=20, choices=Region.choices)
    city = models.CharField("Shahar yoki tuman", max_length=100)
    street = models.CharField("Ko‘cha va mahalla", max_length=200)
    house = models.CharField("Uy", max_length=20)
    apartment = models.CharField("Xonadon", max_length=20, blank=True)
    landmark = models.CharField("Mo‘ljal", max_length=200, blank=True)
    note = models.TextField("Kuryer uchun izoh", blank=True)

    # Yetkazish va to'lov
    delivery_method = models.CharField(
        "Yetkazish usuli", max_length=10, choices=Delivery.choices, default=Delivery.COURIER
    )
    delivery_price = models.PositiveIntegerField("Yetkazish narxi", default=0)
    payment_method = models.CharField(
        "To‘lov usuli", max_length=10, choices=Payment.choices, default=Payment.CARD
    )
    subtotal = models.PositiveIntegerField("Kitoblar summasi", default=0)
    total = models.PositiveIntegerField("Jami", default=0)
    is_paid = models.BooleanField("To‘langan", default=False)
    paid_at = models.DateTimeField("To‘langan vaqt", null=True, blank=True)
    transaction_id = models.CharField("Tranzaksiya ID", max_length=64, blank=True)
    status = models.CharField("Holati", max_length=10, choices=Status.choices, default=Status.NEW)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"#{self.number} — {self.full_name}"

    @property
    def number(self):
        return str(self.pk).zfill(6) if self.pk else "—"

    @property
    def full_address(self):
        parts = [self.get_region_display(), self.city, self.street, f"{self.house}-uy"]
        if self.apartment:
            parts.append(f"{self.apartment}-xonadon")
        return ", ".join(parts)

    def get_absolute_url(self):
        return reverse("shop:order_detail", args=[self.code])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="order_items")
    price = models.PositiveIntegerField("Narxi")
    quantity = models.PositiveIntegerField("Soni", default=1)

    class Meta:
        verbose_name = "Buyurtma qatori"
        verbose_name_plural = "Buyurtma qatorlari"

    def __str__(self):
        return f"{self.book.title} × {self.quantity}"

    @property
    def line_total(self):
        return self.price * self.quantity
