from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("", include("accounts.urls")),
    path("", include("catalog.urls")),
    path("", include("orders.urls")),
    path("", include("blog.urls")),
    path("", include("calc.urls")),
]
handler404 = "pages.views.not_found"
