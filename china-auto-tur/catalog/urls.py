from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Purchase

urlpatterns = [
    path("catalog/", views.catalog, name="catalog"),
    path("catalog/<slug:slug>/", views.car_page, name="car"),
    path("purchases/", views.purchase_list, name="purchases"),
    path("purchases/add/", views.purchase_add, name="purchase_add"),
    path("purchases/<int:pk>/status/", views.purchase_status, name="purchase_status"),
]
