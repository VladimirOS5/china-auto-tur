from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cabinet/", views.cabinet_client, name="cabinet"),
    path("manager/", views.cabinet_manager, name="manager"),
]
