from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("catalog/", include("catalog.urls")),
    path("order/", include("orders.urls")),
    path("accounts/", include("accounts.urls")),
    path("news/", include("blog.urls")),
    path("calc/", include("calc.urls")),
    path("", include("pages.urls")),
]

# своя страница 404 вместо стандартной заглушки Django
handler404 = "pages.views.handler404"

# в режиме разработки отдаём медиа-файлы сами
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
