from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.news_list, name="list"),
    path("<slug:slug>/", views.article_detail, name="article"),
]
