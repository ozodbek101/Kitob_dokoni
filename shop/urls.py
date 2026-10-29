from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("katalog/", views.catalog, name="catalog"),
    path("kitob/<slug:slug>/", views.book_detail, name="book_detail"),
    path("savat/", views.cart_detail, name="cart"),
    path("savat/qoshish/<int:book_id>/", views.cart_add, name="cart_add"),
    path("savat/yangilash/<int:book_id>/", views.cart_update, name="cart_update"),
    path("savat/olib-tashlash/<int:book_id>/", views.cart_remove, name="cart_remove"),
]
