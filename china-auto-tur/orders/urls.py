from django.urls import path
from . import views

urlpatterns = [
    path("order/", views.order_page, name="order"),
    path("order/success/", views.success, name="success"),
    path("quick/", views.quick, name="quick"),
]
