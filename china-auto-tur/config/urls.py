from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dj-admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('catalog/', include('catalog.urls')),
    path('news/', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),  # <-- проверь наличие этой строки
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)