from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_page, name="order"),
    path("success/", views.order_success, name="success"),
    # приём заявки из модалки в шапке: отвечает JSON, без перезагрузки страницы
    path("quick/", views.quick_request, name="quick"),
]
