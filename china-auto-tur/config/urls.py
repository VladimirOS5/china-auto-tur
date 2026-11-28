from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# приложения включаем без префикса: внутренние пути уже содержат catalog/, calc/, order/
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalog.urls")),
    path("", include("orders.urls")),
    path("", include("calc.urls")),
    path("accounts/", include("accounts.urls")),
    path("news/", include("blog.urls")),
    path("", include("pages.urls")),
]

handler404 = "pages.views.handler404"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
