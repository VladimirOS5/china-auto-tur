from django.urls import path
from . import views

urlpatterns = [
    path("news/", views.news, name="news"),
    path("news/<slug:slug>/", views.article, name="article"),
]
