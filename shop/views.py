from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import delivery
from .cart import Cart
from .models import Book, Category

SORTS = {
    "new": ("-created", "Yangilari"),
    "cheap": ("price", "Arzonroq"),
    "expensive": ("-price", "Qimmatroq"),
    "rating": ("-rating", "Reyting"),
    "title": ("title", "Nomi bo‘yicha"),
}


def home(request):
    books = Book.objects.select_related("category")
    return render(request, "shop/home.html", {
        "shelf": books.filter(stock__gt=0).order_by("?")[:30],
        "featured": books.filter(is_featured=True)[:6],
        "fresh": books.order_by("-year")[:6],
        "categories": Category.objects.annotate(n=Count("books")).order_by("order"),
        "book_total": books.count(),
        "free_from": delivery.FREE_COURIER_FROM,
    })


def catalog(request):
    books = Book.objects.select_related("category")
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    lang = request.GET.get("lang", "")
    sort = request.GET.get("sort", "new")
    price_max = request.GET.get("price_max", "")
    in_stock = request.GET.get("in_stock") == "1"

    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q))
    current_category = None
    if category:
        current_category = Category.objects.filter(slug=category).first()
        books = books.filter(category__slug=category)
    if lang in Book.Language.values:
        books = books.filter(language=lang)
    if price_max.isdigit():
        books = books.filter(price__lte=int(price_max))
    if in_stock:
        books = books.filter(stock__gt=0)
    books = books.order_by(SORTS.get(sort, SORTS["new"])[0], "id")

    page = Paginator(books, 12).get_page(request.GET.get("page"))
    return render(request, "shop/catalog.html", {
        "page": page,
        "q": q,
        "category": category,
        "current_category": current_category,
        "categories": Category.objects.annotate(n=Count("books")).order_by("order"),
        "lang": lang,
        "languages": Book.Language.choices,
        "sort": sort,
        "sorts": [(k, v[1]) for k, v in SORTS.items()],
        "price_max": price_max,
        "price_steps": [50_000, 80_000, 100_000, 150_000],
        "in_stock": in_stock,
    })


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related("category"), slug=slug)
    related = (Book.objects.filter(category=book.category).exclude(pk=book.pk)
               .select_related("category").order_by("-rating")[:4])
    return render(request, "shop/book_detail.html", {
        "book": book,
        "related": related,
        "delivery_options": delivery.OPTIONS,
        "free_from": delivery.FREE_COURIER_FROM,
    })


# ---------- Savat ----------

@require_POST
def cart_add(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    cart = Cart(request)
    qty = max(1, int(request.POST.get("quantity", 1) or 1))
    if not book.in_stock:
        messages.error(request, f"«{book.title}» hozir omborda yo‘q.")
    else:
        cart.add(book, qty)
        messages.success(request, f"«{book.title}» savatga qo‘shildi.")
    return redirect(request.POST.get("next") or "shop:cart")


@require_POST
def cart_update(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Cart(request).add(book, int(request.POST.get("quantity", 1) or 0), replace=True)
    return redirect("shop:cart")


@require_POST
def cart_remove(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    Cart(request).remove(book)
    messages.info(request, f"«{book.title}» savatdan olib tashlandi.")
    return redirect("shop:cart")


def cart_detail(request):
    cart = Cart(request)
    subtotal = cart.subtotal
    return render(request, "shop/cart.html", {
        "free_from": delivery.FREE_COURIER_FROM,
        "left_for_free": max(0, delivery.FREE_COURIER_FROM - subtotal),
        "free_progress": min(100, round(subtotal * 100 / delivery.FREE_COURIER_FROM)) if subtotal else 0,
    })
