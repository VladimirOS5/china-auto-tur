from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_view, name='post_list'),
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    path('add/', views.post_create_view, name='post_create'),
    path('<int:pk>/edit/', views.post_edit_view, name='post_edit'),
    path('<int:pk>/delete/', views.post_delete_view, name='post_delete'),
]