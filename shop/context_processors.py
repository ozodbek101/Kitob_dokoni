from .cart import Cart
from .models import Category


def store(request):
    """Har bir sahifaga savat va kategoriyalarni uzatadi."""
    return {
        "cart": Cart(request),
        "nav_categories": Category.objects.all(),
    }
