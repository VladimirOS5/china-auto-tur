from django.urls import path
from . import views

urlpatterns = [
    path("calc/", views.calculator, name="calc"),
    path("calc/api/", views.calc_api, name="calc_api"),
]
