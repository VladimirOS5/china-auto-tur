from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("policy/", views.policy, name="policy"),
    path("callback/", views.callback, name="callback"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
]
