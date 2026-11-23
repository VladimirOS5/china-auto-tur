from django.urls import path

from . import views

app_name = "calc"

urlpatterns = [
    path("", views.calculator, name="calculator"),
    path("api/", views.calculator_api, name="api"),
]
