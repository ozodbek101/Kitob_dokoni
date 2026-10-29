from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Sahifa — boshqaruv paneli"
admin.site.site_title = "Sahifa"
admin.site.index_title = "Do‘kon boshqaruvi"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('app_main.urls')),
    path('', include('shop.urls')),
]
