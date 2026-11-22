from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_page, name="order"),
    path("success/", views.order_success, name="success"),
]
