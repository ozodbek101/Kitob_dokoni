from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .forms import luhn_ok
from .models import Book, Order


class ShopFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_books", verbosity=0)
        cls.book = Book.objects.filter(stock__gte=5).first()

    def add_to_cart(self, qty=1, book=None):
        book = book or self.book
        return self.client.post(reverse("shop:cart_add", args=[book.id]), {"quantity": qty})

    def address(self, **extra):
        data = {
            "full_name": "Aziz Karimov", "phone": "90 123 45 67", "email": "",
            "region": "toshkent_sh", "city": "Yunusobod", "street": "Amir Temur 1",
            "house": "12", "apartment": "4", "landmark": "", "note": "",
            "delivery_method": "courier", "payment_method": "card",
        }
        data.update(extra)
        return data

    def test_pages_open(self):
        for url in [reverse("shop:home"), reverse("shop:catalog"), self.book.get_absolute_url(),
                    reverse("shop:cart"), reverse("shop:catalog") + "?q=Qodiriy&sort=cheap"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_seed_has_many_books(self):
        self.assertGreaterEqual(Book.objects.count(), 70)

    def test_search_finds_author(self):
        r = self.client.get(reverse("shop:catalog"), {"q": "Qodiriy"})
        self.assertContains(r, "O‘tkan kunlar")

    def test_cart_add_and_limit_to_stock(self):
        self.add_to_cart(qty=999)
        self.assertEqual(self.client.session["cart"][str(self.book.id)], self.book.stock)

    def test_checkout_requires_cart(self):
        r = self.client.get(reverse("shop:checkout"))
        self.assertRedirects(r, reverse("shop:catalog"))

    def test_checkout_card_then_pay(self):
        self.add_to_cart(qty=2)
        stock_before = self.book.stock
        r = self.client.post(reverse("shop:checkout"), self.address())
        order = Order.objects.get()
        self.assertRedirects(r, reverse("shop:payment", args=[order.code]))
        self.assertEqual(order.phone, "+998901234567")
        self.assertEqual(order.subtotal, self.book.price * 2)
        self.assertEqual(order.total, order.subtotal + order.delivery_price)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, stock_before - 2)

        r = self.client.post(reverse("shop:payment", args=[order.code]),
                             {"number": "4242 4242 4242 4242", "expiry": "12/39"})
        self.assertRedirects(r, order.get_absolute_url())
        order.refresh_from_db()
        self.assertTrue(order.is_paid)
        self.assertEqual(order.status, Order.Status.PAID)

    def test_declined_card(self):
        self.add_to_cart()
        self.client.post(reverse("shop:checkout"), self.address())
        order = Order.objects.get()
        r = self.client.post(reverse("shop:payment", args=[order.code]),
                             {"number": "4000000000000002", "expiry": "12/39"})
        self.assertContains(r, "rad etdi")
        order.refresh_from_db()
        self.assertFalse(order.is_paid)

    def test_courier_only_in_tashkent(self):
        self.add_to_cart()
        r = self.client.post(reverse("shop:checkout"), self.address(region="samarqand"))
        self.assertContains(r, "Kuryer faqat Toshkent")
        self.assertFalse(Order.objects.exists())

    def test_post_to_region_cash(self):
        self.add_to_cart()
        r = self.client.post(reverse("shop:checkout"),
                             self.address(region="samarqand", delivery_method="post", payment_method="cash"))
        order = Order.objects.get()
        self.assertRedirects(r, order.get_absolute_url())
        self.assertEqual(order.delivery_price, 35_000)

    def test_address_required_for_delivery(self):
        self.add_to_cart()
        r = self.client.post(reverse("shop:checkout"), self.address(street="", house=""))
        self.assertContains(r, "Yetkazib berish uchun bu maydon kerak", count=2)

    def test_pickup_without_address(self):
        self.add_to_cart()
        self.client.post(reverse("shop:checkout"),
                         self.address(delivery_method="pickup", city="", street="", house="", payment_method="cash"))
        self.assertEqual(Order.objects.get().delivery_price, 0)

    def test_free_courier_over_threshold(self):
        expensive = Book.objects.filter(stock__gte=5).order_by("-price").first()
        self.add_to_cart(qty=5, book=expensive)
        self.client.post(reverse("shop:checkout"), self.address(payment_method="cash"))
        self.assertEqual(Order.objects.get().delivery_price, 0)

    def test_luhn(self):
        self.assertTrue(luhn_ok("4242424242424242"))
        self.assertFalse(luhn_ok("4242424242424241"))
