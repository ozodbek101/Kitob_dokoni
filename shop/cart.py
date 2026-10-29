from django.conf import settings

from .models import Book


class Cart:
    """Sessiyada saqlanadigan savat: {book_id: quantity}."""

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault(settings.CART_SESSION_KEY, {})
        self._items = None

    def add(self, book, quantity=1, replace=False):
        key = str(book.id)
        current = 0 if replace else self.data.get(key, 0)
        new_qty = max(0, min(current + quantity, book.stock))
        if new_qty:
            self.data[key] = new_qty
        else:
            self.data.pop(key, None)
        self._save()

    def remove(self, book):
        self.data.pop(str(book.id), None)
        self._save()

    def clear(self):
        self.session[settings.CART_SESSION_KEY] = {}
        self.data = self.session[settings.CART_SESSION_KEY]
        self._save()

    def _save(self):
        self.session.modified = True
        self._items = None

    @property
    def items(self):
        if self._items is None:
            books = Book.objects.filter(id__in=self.data.keys()).select_related("category")
            self._items = [
                {"book": b, "quantity": self.data[str(b.id)], "total": b.price * self.data[str(b.id)]}
                for b in books
            ]
        return self._items

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return sum(self.data.values())

    def __contains__(self, book):
        return str(book.id) in self.data

    @property
    def subtotal(self):
        return sum(i["total"] for i in self.items)
