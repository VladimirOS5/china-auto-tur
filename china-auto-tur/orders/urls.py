from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_create_view, name='order_create'),
    path('<int:pk>/status/', views.order_status_update_view, name='order_status_update'),
]