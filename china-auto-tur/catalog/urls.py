from django.urls import path
from . import views

urlpatterns = [
    path('', views.car_list_view, name='car_list'),
    path('<int:pk>/', views.car_detail_view, name='car_detail'),
    path('add/', views.car_create_view, name='car_create'),
    path('<int:pk>/edit/', views.car_edit_view, name='car_edit'),
    path('<int:pk>/delete/', views.car_delete_view, name='car_delete'),
]